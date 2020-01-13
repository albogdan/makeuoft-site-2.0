from flask import render_template

from application.review import review


@review.route("/")
def index():
    return "hi"
