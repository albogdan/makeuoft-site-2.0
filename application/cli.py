from flask import render_template

# from application import flask_app
# from application.db_models import Users, Teams, PartsAvailable, PartsSignedOut, Tag, tags
from application import db  # import the db instance from application/__init__.py
from flask import jsonify
import click
import os
import json
import random
import string

# Import mail
from application import mail
from flask_mail import Message

from application.db_models import *

"""
Encapsulate the commands in a function to be able to register it with the application
and pass different parameters if the need arises
"""


def register(flask_app):
    @flask_app.cli.group()
    def test():
        """Testing commands for various services"""
        pass

    @flask_app.cli.group()
    def seed():
        """Seeding commands for database tables for the hardware parts and tags, etc"""
        pass

    @test.command()
    def mailsend():
        """Sends a test email through the makeuoft email account"""
        #    msg = Message('Confirm Email', sender= 'email@address.com', recipients= [session['email']])
        msg = Message("Test", recipients=["some_email@example.com"])
        msg.body = "This is a test"
        msg.html = render_template(
            "mails/reset-password.html", username="Test Subject", link="github.com"
        )
        mail.send(msg)

    @seed.command()
    def seedall():
        """Runs all the commands to reinitialize the database with necessary seeds"""
        """These commands are taken from the cmd.txt file in seeds/"""
        commands_csv_path = "application/seeds/cmd.txt"
        with open(commands_csv_path, "r") as commands_csv:
            for command in commands_csv:
                print("\n Executing command : {0} \n\n".format(command[:-1]))
                os.system(command[:-1])

    @seed.command()
    def partsavailable():
        """Seeds the PartsAvailable table with values from PartsAvailable.csv in the seeds/ folder"""
        """Note: if get 'unique constraint failed' then you have to clear the table before you seed it"""
        # temp_tag = Tag.query.filter_by(tag_name="MCU").first()
        # print(temp_tag) #This is a class object
        parts_available_csv_path = (
            "application/seeds/PartsAvailable.csv"
        )  # os.path.join(BASE_DIR, 'FroshGroups.csv')
        with open(parts_available_csv_path, "r") as parts_available_csv:
            count = 0
            for i in parts_available_csv:
                j = i[:-1].split(",")
                record = PartsAvailable(
                    part_name=j[0],
                    part_manufacturer=j[1],
                    serial_number=j[2],
                    quantity_available=j[3],
                    quantity_remaining=j[3],
                )

                temp_tag = Tag.query.filter_by(tag_name=j[4]).first()
                record.tag_list.append(temp_tag)
                db.session.add(record)
        db.session.commit()

    @seed.command()
    def tags():
        """Seeds the Tags table with values from Tags.csv in the seeds/ folder"""
        tags_csv_path = (
            "application/seeds/Tags.csv"
        )  # os.path.join(BASE_DIR, 'FroshGroups.csv')
        with open(tags_csv_path, "r") as tags_csv:
            for i in tags_csv:
                if i[-1] == "\n":
                    record = Tag(tag_name=i[:-1])
                else:
                    record = Tag(tag_name=i)
                db.session.add(record)
        db.session.commit()

    @seed.command()
    def users():
        """Seeds the Users table with values from Users.csv in the seeds/ folder"""
        users_csv_path = (
            "application/seeds/Users.csv"
        )  # os.path.join(BASE_DIR, 'FroshGroups.csv')
        with open(users_csv_path, "r") as users_csv:
            for i in users_csv:
                j = i[:-1].split(",")
                record = User(
                    first_name=j[0],
                    last_name=j[1],
                    email=j[2],
                    id_provided=bool(random.getrandbits(1)),
                )
                record.set_password(j[3])
                db.session.add(record)
        db.session.commit()

    @seed.command()
    def teams():
        """Seeds the Teams table with integers from 1 to n for each team"""
        teams_csv_path = (
            "application/seeds/Teams.csv"
        )  # os.path.join(BASE_DIR, 'FroshGroups.csv')
        userSeeds = User.query.filter_by().all()
        print(userSeeds)
        with open(teams_csv_path, "r") as teams_csv:
            for team in teams_csv:
                #            for i in range(0, 5):#len(userSeeds)//Teams.max_members):
                code = "".join(
                    random.choice(string.ascii_uppercase) for i in range(5)
                )  # 5 char ID
                record = Team(team_code=code, team_name=team[:-1])
                for k in range(0, 4):
                    record.team_members.append(userSeeds[0])
                    del userSeeds[0]
                db.session.add(record)
        db.session.commit()

    @seed.command()
    def checkteams():
        teamList = Team.query.all()
        print(teamList)
        for i in teamList:
            for j in i.team_members.all():
                print(j.first_name, end="")
            print()

    @seed.command()
    def checkuser():
        userList = User.query.all()
        print(userList)
        for i in userList:
            print(i.team, end="")  # prints the team number
            print(Team.query.filter_by(id=i.team).first().team_name, end="")
            print()

    @seed.command()
    def checkparts():
        tagList = Tag.query.all()
        for tag_item in tagList:
            PartsAvailable.query()
            print(tag_item.tag_name)

    @seed.command()
    def findsametag():
        # Choose random part
        part = PartsAvailable.query.all()[0]
        testdict = {}
        testdict[part.id] = {
            "name": part.part_name,
            "manufacturer": part.part_manufacturer,
            "total": part.quantity_available,
            "available": part.quantity_remaining,
            "serialnum": part.serial_number,
            "tags": [tag.tag_name for tag in part.tag_list],
        }
        print(jsonify(testdict))
        # **Tags for a part
        # **part_tag = part.tag_list.all() # This returns a Tag object

        # **print(part_tag)
        # **Parts for a tag
        # **print(part_tag[0].partsavailable.all())
        # To get all the tags for a part:
        # print(Tag.query.filter(Tag.partsavailable.any(id=part_tag.id)).all())

        # To get all the parts for a tag:
        # print(part_tag.count_parts())
        # all_parts = PartsAvailable.query.filter(Tag.partsavailable.any(id=tag_id).all())
        # part_ids = tags.query.filter_by(tag_id=part_tag.id)
        # print(part_ids)
        # print(PartsAvailable.query.filter(tags.c.tag_id==part_tag.id).all())

    @seed.command()
    def usersnoteam():
        users_no_team = User.query.filter(User.team == None).all()
        for i in users_no_team:
            print(i.team)
