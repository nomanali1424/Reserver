from flask import jsonify, request, session, redirect, render_template, url_for, abort

from reserver import app
from reserver.db_methods import query_db, Query


class Venue:
    def __init__(
        self, capacity, place, location, multiplier=100, name=None, id=None
    ) -> None:
        if name:
            self.name = name
        self.capacity = capacity
        self.place = place
        self.location = location
        self.multiplier = multiplier
        if id:
            self.id = id


@app.route("/venues", methods=["GET"])
def get_venues():
    q = request.args.get("query")
    args = []
    query = """
    SELECT venues.id, venues.name, venues.capacity,
    GROUP_CONCAT(shows.name) as show_names,
    GROUP_CONCAT(shows.id) as show_ids,
    GROUP_CONCAT(shows.booked_seats) as show_seats
    FROM venues
    LEFT JOIN shows ON venues.id = shows.venue_id"""
    if q:
        query += " WHERE LOWER(venues.name) LIKE LOWER(?)"
        args.append("%" + q + "%")
    query += " GROUP BY venues.id"
    venues = query_db(query=query, args=args)
    results = [dict(row) for row in venues]
    for venue in results:
        venue["show_names"] = (
            venue["show_names"].split(",") if venue["show_names"] else []
        )
        venue["show_ids"] = (
            list(map(int, venue["show_ids"].split(","))) if venue["show_ids"] else []
        )
        venue["show_seats"] = (
            list(map(int, venue["show_seats"].split(",")))
            if venue["show_seats"]
            else []
        )
    return results


@app.route("/venues/<int:id>", methods=["GET"])
def get_venue(id):
    venues = Query("venues", check_attrs={"id": id}).call_select_query(one=True)
    return dict(venues)


@app.route("/venues/<int:id>/shows", methods=["GET"])
def get_venue_shows(id):
    if "is_admin" in session and session["is_admin"]:
        shows = Query("shows", check_attrs={"venue_id": id}).call_select_query()
        results = [dict(row) for row in shows]
        return results
    abort(401)


def create_venue(venue: Venue):
    if "is_admin" in session and session["is_admin"]:
        check_venue = Query(
            "venues", check_attrs={"name": venue.name}
        ).call_select_query(one=True)
        if check_venue:
            return "Venue already exists"

        status = Query(
            "venues",
            other_attrs={
                "name": venue.name,
                "capacity": venue.capacity,
                "place": venue.place,
                "location": venue.location,
                "multiplier": venue.multiplier,
            },
        ).call_insert_query()
        return status
    abort(401)


def edit_venue(venue: Venue):
    if "is_admin" in session and session["is_admin"]:
        if not venue.id:
            abort(400)

        check_venue = Query("venues", check_attrs={"id": venue.id}).call_select_query(
            one=True
        )
        if not check_venue:
            abort(400)

        status = Query(
            "venues",
            other_attrs={
                "capacity": venue.capacity,
                "place": venue.place,
                "location": venue.location,
                "multiplier": venue.multiplier,
            },
            check_attrs={"id": venue.id},
        ).call_update_query()
        return status
    abort(401)


@app.route("/venues/<int:id>", methods=["DELETE"])
def delete_venue(id):
    if "is_admin" in session and session["is_admin"]:
        status = Query("venues", check_attrs={"id": id}).call_delete_query()
        return status
    abort(401)
