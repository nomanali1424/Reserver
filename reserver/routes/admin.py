from flask import request, session, redirect, render_template, url_for, abort
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import json

from reserver import app
from reserver.routes.venue import (
    get_venues,
    delete_venue,
    get_venue,
    edit_venue,
    create_venue,
    Venue,
)
from reserver.routes import show as Show


@app.route("/admin/home", methods=["GET"])
def admin_home():
    if "userid" in session and "is_admin" in session:
        if not session["is_admin"]:
            return redirect(url_for("user_home"))
        else:
            venues = get_venues()
            return render_template(
                "admin_home.html",
                name=session["username"],
                venue_list=venues,
            )
    else:
        return render_template("login.html", error="Please Log-in to continue")


@app.route("/admin/venue/delete/<int:id>", methods=["GET"])
def admin_delete_venue(id):
    if "userid" in session and "is_admin" in session:
        if session["is_admin"]:
            status = delete_venue(id)
            if status == "Success":
                return redirect(request.referrer)
            else:
                return render_template("failure.html", error=status)
        abort(400)
    else:
        return redirect(url_for("login"), error="Please Log-in to continue")


@app.route("/admin/venue/manage", methods=["GET", "POST"])
def admin_manage_venue():
    if "userid" in session and "is_admin" in session:
        if session["is_admin"]:
            if request.method == "GET":
                venue_id = request.args.get("v_id")
                if venue_id:
                    venue = get_venue(venue_id)
                    return render_template(
                        "manage_venue.html", name=session["username"], venue=venue
                    )
                else:
                    return render_template(
                        "manage_venue.html", name=session["username"]
                    )
            elif request.method == "POST":
                error = False
                while True:
                    try:
                        type = request.form["type"]
                        if type == "Create":
                            name = request.form["name"]
                        else:
                            id = request.form["id"]
                        place = request.form["place"]
                        capacity = int(request.form["capacity"])
                        location = request.form["location"]
                        multiplier = int(request.form["multiplier"])
                    except ValueError:
                        error = "Invalid Values"
                        break
                    except Exception as e:
                        error = "Invalid Form Values: " + str(e)
                        break
                    if type == "Create":
                        venue = Venue(capacity, place, location, name=name)
                        status = create_venue(venue)
                    elif type == "Edit":
                        venue = Venue(capacity, place, location, id=id)
                        status = edit_venue(venue)
                    else:
                        abort(400)
                    if status != "Success":
                        error = status
                    break
                if error:
                    return render_template(
                        "manage_venue.html", name=session["username"], error=error
                    )
                else:
                    return redirect(url_for("admin_home"))
        abort(400)
    else:
        return redirect(url_for("login"), error="Please Log-in to continue")


@app.route("/admin/show/delete/<int:id>", methods=["GET"])
def admin_delete_show(id):
    if "userid" in session and "is_admin" in session:
        if session["is_admin"]:
            status = Show.delete_show(id)
            if status == "Success":
                return redirect(url_for("admin_home"))
            else:
                return render_template("failure.html", error=status)
        abort(400)
    else:
        return redirect(url_for("login"), error="Please Log-in to continue")


@app.route("/admin/show/manage", methods=["GET", "POST"])
def admin_manage_show():
    if "userid" in session and "is_admin" in session:
        if session["is_admin"]:
            if request.method == "GET":
                show_id = request.args.get("s_id")
                if show_id:
                    show = Show.get_show(show_id)
                    return render_template(
                        "manage_show.html", name=session["username"], show=show
                    )
                else:
                    venue_id = request.args.get("v_id")
                    return render_template(
                        "manage_show.html", name=session["username"], v_id=venue_id
                    )
            elif request.method == "POST":
                error = False
                id = None
                v_id = None
                while True:
                    try:
                        type = request.form["type"]
                        if type == "Edit":
                            id = request.form["id"]
                        else:
                            v_id = request.form["v_id"]
                        name = request.form["name"]
                        rating = int(request.form["rating"])
                        tags = request.form["tags"]
                        price = int(request.form["price"])
                        timing = request.form["timing"]
                    except ValueError:
                        error = "Invalid Values"
                        break
                    except Exception as e:
                        error = "Invalid Form Values: " + str(e)
                        break
                    if rating > 100 or rating < 0:
                        error = "Invalid Rating: Try Values between 0-100"
                        break
                    if price <= 0:
                        error = "Invalid Price: Not a whole number"
                        break
                    if type == "Create":
                        show = Show.Show(rating, tags, price, timing, name, v_id=v_id)
                        status = Show.create_show(show)
                    elif type == "Edit":
                        show = Show.Show(rating, tags, price, timing, name, id=id)
                        status = Show.edit_show(show)
                    else:
                        abort(400)
                    if status != "Success":
                        error = status
                    break
                if error:
                    if id:
                        show = Show.get_show(id)
                        return render_template(
                            "manage_show.html",
                            name=session["username"],
                            show=show,
                            error=error,
                        )
                    elif v_id:
                        return render_template(
                            "manage_show.html",
                            name=session["username"],
                            v_id=v_id,
                            error=error,
                        )
                    else:
                        abort(400)

                else:
                    return redirect(url_for("admin_home"))
        abort(400)
    else:
        return redirect(url_for("login"), error="Please Log-in to continue")


@app.route("/admin/summary", methods=["GET"])
def admin_summary():
    if "userid" in session and "is_admin" in session:
        if session["is_admin"]:
            results = requests.get(request.host_url.rstrip("/") + url_for("get_venues"))
            venues = json.loads(results.text)
            print(venues)
            for venue in venues:
                x = []
                y1 = []
                y2 = []
                for id in venue["show_ids"]:
                    results = requests.get(
                        request.host_url.rstrip("/") + url_for("get_show", id=id)
                    )
                    show = json.loads(results.text)
                    x.append(show["name"])
                    y1.append((show["booked_seats"] / venue["capacity"]) * 100)
                    y2.append(show["rating"])
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.plot(x, y1, "-o", label="Booking %")
                ax.plot(x, y2, "-o", label="Rating")
                ax.set_ylabel("Rating/Booking %")
                ax.set_xlabel("Shows")
                ax.legend()
                plt.savefig(f"{app.static_folder}/venue_{venue['id']}.png")

            return render_template(
                "admin_summary.html", name=session["username"], venues=venues
            )
        abort(400)
    else:
        return redirect(url_for("login"), error="Please Log-in to continue")
