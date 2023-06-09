from flask import jsonify, request, session, redirect, render_template, url_for, abort

from reserver import app
from reserver.db_methods import Query


class Show:
    def __init__(
        self, rating, tags, price, timing, name, booked_seats=0, v_id=None, id=None
    ) -> None:
        self.name = name
        self.rating = rating
        self.tags = tags
        self.price = price
        self.timing = timing
        if v_id:
            self.v_id = v_id
        if id:
            self.id = id
        self.booked_seats = booked_seats


@app.route("/shows", methods=["GET"])
def get_shows():
    shows = Query("shows").call_select_query()
    results = [dict(row) for row in shows]
    return results


@app.route("/shows/<int:id>", methods=["GET"])
def get_show(id):
    show = Query("shows", check_attrs={"id": id}).call_select_query(one=True)
    return dict(show)


def create_show(show: Show):
    if "is_admin" in session and session["is_admin"]:
        status = Query(
            "shows",
            other_attrs={
                "name": show.name,
                "rating": show.rating,
                "tags": show.tags,
                "price": show.price,
                "timing": show.timing,
                "venue_id": show.v_id,
                "booked_seats": show.booked_seats,
            },
        ).call_insert_query()
        return status
    abort(401)


def edit_show(show: Show):
    if "is_admin" in session and session["is_admin"]:
        if not show.id:
            abort(400)

        check_show = Query("shows", check_attrs={"id": show.id}).call_select_query(
            one=True
        )
        if not check_show:
            abort(400)
        status = Query(
            "shows",
            other_attrs={
                "name": show.name,
                "rating": show.rating,
                "tags": show.tags,
                "price": show.price,
                "timing": show.timing,
                "booked_seats": show.booked_seats,
            },
            check_attrs={"id": show.id},
        ).call_update_query()
        return status
    abort(401)


@app.route("/shows/<int:id>", methods=["DELETE"])
def delete_show(id):
    if "is_admin" in session and session["is_admin"]:
        status = Query("shows", check_attrs={"id": id}).call_delete_query()
        return status
    abort(401)
