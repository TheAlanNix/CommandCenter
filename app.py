#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the main Python script to run Cisco Command Center

This script runs the Flask web server which handles the API backend (/api)
and the Vue.js frontend (/) for Cisco Command Center.

This script will also schedule events to be loaded into the database
at a regular interval.
"""


import atexit
import json
import os
import uuid
from bson.json_util import dumps
from datetime import datetime, timedelta

import flask
import pymongo

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from modules import amp_event_importer
from modules import umbrella_event_importer

# Configuration
DEBUG = True
PRODUCTION = False

CONFIG_FILE = "./config.json"
CONFIG_DATA = None

# Instantiate the app
app = Flask(__name__, static_folder="./www/dist/static", template_folder="./www/dist")
app.config.from_object(__name__)

# Enable CORS
CORS(app)


###################
#    FUNCTIONS    #
###################


def load_config():
    """Load the Configuration JSON"""
    global CONFIG_DATA

    print("Loading Config Data...")

    with open(CONFIG_FILE, 'r') as json_config_file:
        CONFIG_DATA = json.loads(json_config_file.read())


# Sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


# Alerts Functions
@app.route('/api/events', methods=['GET'])
def get_alerts():
    """A function to retrieve events from the database and return them as JSON"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(CONFIG_DATA["database"]["address"]),
                                    username=CONFIG_DATA["database"]["username"],
                                    password=CONFIG_DATA["database"]["password"])

    # Use the 'commandcenter' database
    command_center_db = db_client['commandcenter']

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db['events']

    # Get the events
    if 'timeframe' in request.args:
        timeframe = int(request.args["timeframe"])
        query_date = datetime.utcnow().replace(microsecond=0) - timedelta(hours=timeframe)
        query_date = query_date.isoformat() + "+00:00"
        latest_events = command_center_events.find({'timestamp': {'$gte': query_date}}).sort("timestamp", -1)
    else:
        latest_events = command_center_events.find({}).sort("timestamp", -1)

    latest_events = dumps(latest_events)

    response_object = {'status': 'success'}
    response_object['events'] = json.loads(latest_events)

    return jsonify(response_object)


def load_events():
    """A function to trigger all event imports into the database"""
    amp_event_importer.run()
    umbrella_event_importer.run()


# If in production, load the Vue.js routes
if PRODUCTION:

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template("index.html")

if __name__ == '__main__':

    # When Flask is in debug mode, it loads twice.
    # To prevent the scheduler from loading twice, we check to see
    # if we're in debug mode, if we are, then we wait for the second load.
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":

        # Run an event load and schedule future runs
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=load_events, trigger="interval", minutes=1)
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    # Load the config data
    load_config()

    # Run the webserver
    app.run()
