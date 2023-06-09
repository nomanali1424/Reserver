from flask import g
import sqlite3

from reserver.constants import DATABASE
from reserver import app


class Query:
    def __init__(self, table: str, check_attrs: dict = None, other_attrs=None) -> None:
        self.table = table
        self.check_attrs = check_attrs
        self.attrs = other_attrs

    def select_query(self):
        select_cols = ", ".join(list(map(str.strip, self.attrs))) if self.attrs else "*"
        query = f"SELECT {select_cols} FROM {self.table}"
        if self.check_attrs:
            query += f" WHERE {' = ? AND '.join(self.check_attrs.keys())} = ?"
            return [query, list(self.check_attrs.values())]
        return [query]

    def insert_query(self):
        query = f"INSERT INTO {self.table} ({', '.join(self.attrs.keys())}) VALUES ({', '.join(['?']*len(self.attrs))})"
        return query, list(self.attrs.values())

    def update_query(self):
        query = f"UPDATE {self.table} SET {' = ? , '.join(self.attrs.keys())} = ? WHERE {' = ? , '.join(self.check_attrs.keys())} = ?"
        vals = list(self.attrs.values())
        vals.extend(list(self.check_attrs.values()))
        return query, vals

    def delete_query(self):
        query = f"DELETE FROM {self.table} WHERE {' = ? AND'.join(self.check_attrs.keys())} = ?"
        return query, list(self.check_attrs.values())

    def call_select_query(self, one=False):
        query_items = self.select_query()
        if len(query_items) == 1:
            return query_db(query_items[0], one=one)
        return query_db(query_items[0], query_items[1], one=one)

    def call_insert_query(self):
        query, values = self.insert_query()
        return query_db(query, values, type="INSERT")

    def call_update_query(self):
        query, values = self.update_query()
        return query_db(query, values, type="UPDATE")

    def call_delete_query(self):
        query, values = self.delete_query()
        return query_db(query, values, type="DELETE")


def init_db(init: bool = True):
    schema = "schema/init_schema.sql" if init else "schema/update_schema.sql"
    with app.app_context():
        db = get_db()
        with app.open_resource(schema, mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(
            DATABASE, detect_types=sqlite3.PARSE_DECLTYPES
        )
    db.row_factory = sqlite3.Row
    db.text_factory = lambda b: b.decode(errors="ignore")
    return db


def query_db(query, args=(), one=False, type="SELECT"):
    db = get_db()
    cur = db.execute(query, args)
    if type == "SELECT":
        rv = cur.fetchall()
        return_val = (rv[0] if rv else None) if one else rv
    else:
        db.commit()
        return_val = "Success" if cur.rowcount else "ERR: Database not updated"
    cur.close()
    return return_val


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
