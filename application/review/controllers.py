import math

from flask import render_template, request

from application.review import review, manager

# Number of teams to display on one page
page_size = 10


@review.route("/")
def index():
    page = int(request.args.get("page", 1))
    # status = request.args.get("status", "all")

    offset = (page-1)*page_size

    teams_query = manager.get_teams()
    num_pages = math.ceil(teams_query.count() / page_size)
    teams = teams_query.offset(offset).limit(page_size).all()

    return render_template("review/portal.html", teams=teams, page=page, num_pages=num_pages)
