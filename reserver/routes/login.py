from flask import request, session, redirect, render_template, url_for

from reserver import app
from reserver.db_methods import query_db, Query


@app.route("/register", methods=["GET", "POST"])
def register():
    error = False
    if request.method == "POST":
        while True:
            try:
                email = request.form["email"]
                username = request.form["username"]
                age = int(request.form["age"])
                password = request.form["password"]
                conf_pass = request.form["confirm-password"]
                firstname = request.form["firstname"]
                lastname = request.form["lastname"]
                gender = request.form["gender"]
            except ValueError:
                error = "Invalid Age: Value not a number"
                break
            except Exception as e:
                error = "Invalid Form Values: " + str(e)
                break

            db_email = Query(
                "users", check_attrs={"email": email}, other_attrs=["email"]
            ).call_select_query(one=True)
            if db_email:
                error = "Email Already Registered"
                break

            user = Query(
                "users", check_attrs={"username": username}, other_attrs=["username"]
            ).call_select_query(one=True)
            if user:
                error = "Username Already Taken"
                break

            if age < 12 or age > 117:
                error = "Invalid Age: Enter a valid number (12-117)"
                break
            if password != conf_pass:
                error = "Password and confirm password did not match"
                break

            status = Query(
                "users",
                other_attrs={
                    "email": email,
                    "username": username,
                    "age": age,
                    "password": password,
                    "first_name": firstname,
                    "last_name": lastname,
                    "gender": gender,
                },
            ).call_insert_query()
            if status == "Success":
                return render_template("success.html")
            else:
                return render_template("failure.html", error=status)

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Query(
            "users",
            check_attrs={"username": username},
            other_attrs=["username", "id", "password"],
        ).call_select_query(one=True)
        if user:
            if user["password"] == password:
                session["userid"] = user["id"]
                session["username"] = user["username"]
                session["is_admin"] = False
                return redirect(url_for("user_home"))
            else:
                error = "Password Mismatch"
        else:
            error = "Username not found!"
    return render_template("login.html", error=error)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Query(
            "admins",
            check_attrs={"username": username},
            other_attrs=["id", "username", "password"],
        ).call_select_query(one=True)
        if user:
            if user["password"] == password:
                session["userid"] = user["id"]
                session["username"] = user["username"]
                session["is_admin"] = True
                return redirect(url_for("admin_home"))
            else:
                error = "Password Mismatch"
        else:
            error = "Username not found!"
    return render_template("login.html", error=error, mode="admin")


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("userid", None)
    session.pop("is_admin", None)
    session.pop("username", None)
    return redirect(url_for("home"))
