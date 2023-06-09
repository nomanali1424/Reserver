from flask import render_template, abort
from werkzeug.exceptions import HTTPException

from reserver import app


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        error = {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
        return render_template("failure.html", error=error), e.code

    abort(500)
