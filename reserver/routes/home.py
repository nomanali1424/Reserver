from flask import request, session, redirect, render_template, url_for

from reserver import app


@app.route("/", methods=["GET"])
def home():
    if "userid" in session:
        if session["is_admin"]:
            return redirect(url_for("admin_home"))
        else:
            return redirect(url_for("user_home"))
    return render_template("landing.html")


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")
