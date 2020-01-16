from flask import request, jsonify
from application.db_models import *

from application import db
from application.api import api
from application.review import manager

import json
from flask_login import login_required, current_user

from application import roles_required

from flask_cors import cross_origin


# === API routes in use by the main site ===
@api.route("/teams/", methods=["GET", "POST"])
@cross_origin()
@login_required
def teams():
    if not current_user.is_active:
        return "User not activated", 401

    if request.method == "GET":
        if not current_user.is_allowed(["admin"]):
            return "Not allowed", 403

        return jsonify([t.serialize() for t in Team.query.all()])

    if request.method == "POST":
        if current_user.team is not None:
            return "Already on a team", 409

        team = Team()
        team.team_members.append(current_user)
        db.session.add(team)
        db.session.commit()

        return team.json(), 201


@api.route("/teams/<team_code>/", methods=["GET", "PATCH"])
@cross_origin()
@login_required
def teams_detail(team_code):
    if not current_user.is_active:
        return "User not activated", 401

    if request.method == "GET":
        if current_user.team.team_code == team_code or current_user.is_admin:
            return Team.query.filter_by(team_code=team_code).first().json()
        else:
            return "Not allowed", 403

    elif request.method == "PATCH":
        if not current_user.is_allowed(["admin", "staff"]):
            return "Not allowed", 403

        for field in manager.reviewer_fields:
            if field in request.json:
                manager.set_team_application_attribute(team_code, field, request.json[field])

        return manager.get_team(team_code).json()


@api.route("/users/", methods=["GET"])
@cross_origin()
@login_required
@roles_required(["admin"])
def users():
    if request.method == "GET":
        return jsonify([u.serialize() for u in User.query.filter(is_active=True)])


@api.route("/users/<uuid>/", methods=["PATCH"])
@cross_origin()
@login_required
def users_detail(uuid):
    if request.method == "PATCH":
        if not current_user.is_allowed(["admin", "staff"]):
            return "Not allowed", 403

        for field in manager.reviewer_fields:
            if field in request.json:
                manager.set_user_application_attribute(uuid, field, request.json[field])

        return manager.get_user(uuid).json()


# === API routes in use by the hardware signout site ===
@api.route("/test", methods=["GET", "POST"])
@login_required
@roles_required(["admin"])
def api_main():
    print("success")
    return jsonify({"message": "User registration"})


# Inventory.js
@api.route("/inventory", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def inventoryAll():
    partsList = PartsAvailable.query.all()
    partsJSON = []
    for part in partsList:
        partsJSON.append(
            {
                "id": part.id,
                "name": part.part_name,
                "manufacturer": part.part_manufacturer,
                "total": part.quantity_available,
                "available": part.quantity_remaining,
                "serialnum": part.serial_number,
                "tags": [tag.tag_name for tag in part.tag_list],
            }
        )

    return jsonify(partsJSON)


# App.js
@api.route("/teamlist", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def teamsAll():
    # Get a list of all the teams
    teamList = Team.query.all()
    teamsJSON = []
    # For each team:
    for team in teamList:
        teamDict = {}
        teamDict["index"] = team.id
        teamDict["members"] = []
        # For each contestant on that team
        print("TEST:")
        print(team.team_members)

        for teammate in team.team_members:
            name = str(teammate.first_name + " " + teammate.last_name)
            teamDict["members"].append(
                {"name": name, "govt_id": teammate.id_provided, "id": teammate.id}
            )
        teamsJSON.append(teamDict)
    return jsonify(teamsJSON)


# Inventory.js
@api.route("/taglist", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def tagsAll():
    # Get a list of all the teams
    tagList = Tag.query.all()
    tagsJSON = []
    # For each team:
    for tag in tagList:
        tagDict = {}
        tagDict["id"] = tag.id
        tagDict["name"] = tag.tag_name
        tagsJSON.append(tagDict)
    print(tagsJSON)
    return jsonify(tagsJSON)


# Checkout.js
@api.route("/teamscheckout", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def teamsCheckout():
    # Get a list of all the teams
    teamList = Team.query.all()
    teamsJSON = []
    # For each team:
    for team in teamList:
        teamDict = {}
        teamDict["value"] = team.id
        teamDict["label"] = "Team: " + str(team.id)
        teamsJSON.append(teamDict)
    return jsonify(teamsJSON)


# App.js
@api.route("/info", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def info():
    # Get a count of all the teams
    teamCount = len(Team.query.all())
    # Get a count of all of the users
    userCount = len(User.query.all())
    # Get a count of all the parts that are available
    parts_all = PartsAvailable.query.all()
    parts_all_count = 0
    for part in parts_all:
        parts_all_count += part.quantity_available
    # Get a count of all the parts that are signed out
    parts_out = len(PartsSignedOut.query.all())
    returnJSON = {
        "teamcount": teamCount,
        "usercount": userCount,
        "partsall": parts_all_count,
        "partsout": parts_out,
    }
    return jsonify(returnJSON)


# Checkout.js
@api.route("/checkoutitems", methods=["POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def itemCheckout():
    data = json.loads(request.data)
    print("Request for team {0}".format(data["team"]))
    print("Items requested: {0}".format(data["items"]))
    # Get the team
    team = Team.query.filter_by(id=data["team"]).first()

    # For each item, check if the quantity requested exists
    # Then iterate through the quantity they requested
    for item in data["items"]:
        partDB = PartsAvailable.query.filter_by(part_name=item["name"]).first()
        if partDB.quantity_remaining < item["quantity"]:
            return jsonify(
                {
                    "status": "failed",
                    "message": "Not enough parts remaining!",
                    "name": item["name"],
                    "requested_parts": item["quantity"],
                    "remaining_parts": partDB.quantity_remaining,
                }
            )
        for i in range(0, item["quantity"]):
            part_out = PartsSignedOut()
            team.parts_used.append(part_out)
            partDB.quantity_remaining -= 1
            partDB.parts_signed_out.append(part_out)
            db.session.add(part_out)
    db.session.commit()
    return jsonify({"status": "success", "message": "all parts recorded successfully"})


# AddTeamSelector.js
@api.route("/manageteams/getparticipants", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def usersNotOnTeam():
    users_no_team = User.query.filter(User.team == None).all()
    usersJSON = []
    for user in users_no_team:
        if user.team == None:
            usersJSON.append(
                {"value": user.id, "label": str(user.first_name + " " + user.last_name)}
            )
    return jsonify(usersJSON)


## ADD A CHECK FOR MINIMUM 2 PEOPLE
# CreateTeam.js
@api.route("/manageteams/addrecord", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def addrecord():
    data = json.loads(request.data)
    newTeam = Team()
    for user in data:
        userDBEntry = User.query.filter_by(id=user["value"]).first()
        userDBEntry.id_provided = user["governmentID"]
        newTeam.team_members.append(userDBEntry)
    db.session.add(newTeam)
    db.session.commit()
    return jsonify({"status": "success", "message": "new team created successfully"})


# EditTeam.js
@api.route("/manageteams/getmembers", methods=["GET", "POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def getMembers():
    data = json.loads(request.data)
    teamNumber = data["teamNumber"]
    team = Team.query.filter_by(id=teamNumber).first()
    if team == None:
        return jsonify({"status": "error", "message": "team does not exist"})
    teamMembers = team.team_members.all()
    teamMembersJSON = []
    for member in teamMembers:
        teamMembersJSON.append(
            {
                "value": member.id,
                "label": str(member.first_name + " " + member.last_name),
            }
        )
    return jsonify(teamMembersJSON)


# EditTeam.js
@api.route("/manageteams/deleteteam", methods=["POST"])
@cross_origin()
@login_required
@roles_required(["admin"])
def deleteTeam():
    data = json.loads(request.data)
    teamNumber = data["teamNumber"]
    team = Team.query.filter_by(id=teamNumber).first()
    if team == None:
        return jsonify({"status": "error", "message": "team does not exist"})
    teamMembers = team.team_members.all()
    for member in teamMembers:
        team.team_members.remove(member)
    Team.query.filter_by(id=teamNumber).delete()
    db.session.commit()
    return jsonify({"status": "success", "message": "team deleted successfully"})


"""
Requests summary:
 - JSON of teams with contestants in each team, and whether id was provided for each
 - JSON of all the parts signed out w/ a time signed out
 - JSON of all the teams that a part has been signed out to (team, people, quantity to that team, time signed out)
 - JSON same as api/inventory but only with tag and item name
 - JSON that returns a list of all the teams and their team names (id + name)
"""
