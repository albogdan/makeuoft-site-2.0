from flask import Blueprint, request, render_template, flash, session, redirect, url_for, jsonify
from datetime import datetime

from application.db_models import *

import json

from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

# Import the homepage Blueprint from home/__init__.py
from application.hardware_signout import hardware_signout


@hardware_signout.route('/')
@hardware_signout.route('/index', methods=['GET', 'POST'])
#@login_required
def index():
    return render_template('hardware_signout/index.html')
