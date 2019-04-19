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
import pprint
import time
import uuid
from bson.json_util import dumps
from datetime import datetime, timedelta

import flask
import pymongo
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from modules import amp_event_importer
from modules import pxgrid_controller
from modules import stealthwatch_event_importer
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
def get_events():
    """A function to retrieve events from the database and return them as JSON"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(CONFIG_DATA["database"]["address"]),
                                    username=CONFIG_DATA["database"]["username"],
                                    password=CONFIG_DATA["database"]["password"])

    # Use the 'commandcenter' database
    command_center_db = db_client['commandcenter']

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db['events']

    # Set up a basic query filter
    query_filter = {}

    # If the host IP is specified, then only return those events.
    if 'host_ip' in request.args:
        query_filter['src_ip'] = request.args['host_ip']

    # If a timeframe is specified, then use it.
    if 'timeframe' in request.args:
        timeframe = int(request.args['timeframe'])
        query_date = datetime.utcnow().replace(microsecond=0) - timedelta(hours=timeframe)
        query_filter['timestamp'] = {'$gte': query_date}

    # Get the events
    latest_events = command_center_events.find(query_filter).sort('timestamp', -1)

    # Set up a response object
    response_object = {
        'status': 'success',
        'events': [],
    }

    # Iterate through all events
    for event in latest_events:

        # Make a human readable date
        event['formatted_timestamp'] = event["timestamp"].strftime("%b %d, %Y %H:%M:%S UTC")

        # Append the event to the response
        response_object['events'].append(json.loads(dumps(event)))

    return jsonify(response_object)


# ISE Functions
@app.route('/api/ise_actions', methods=['GET'])
def get_ise_actions():
    """A function to get the ANC profiles from ISE"""

    api_url = "https://{}:{}@{}:9060/ers/config/ancpolicy".format(CONFIG_DATA["ise"]["username"],
                                                                  CONFIG_DATA["ise"]["password"],
                                                                  CONFIG_DATA["ise"]["address"])

    print("Fetching {}".format(api_url))

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Get ISE ANC Policies
    http_request = requests.get(api_url, headers=headers, verify=False)

    # Check to make sure the GET was successful
    if http_request.status_code == 200:
        return jsonify(http_request.json())
    else:
        print('ISE Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit()


@app.route('/api/ise_anc_status/<mac_address>', methods=['GET'])
def get_ise_anc_assignment(mac_address):
    """A function to look up the ISE ANC assignment for a given MAC address"""

    pxgrid = pxgrid_controller.PxgridControl(CONFIG_DATA["ise"]["address"],
                                             CONFIG_DATA["ise"]["pxgrid_name"],
                                             CONFIG_DATA["ise"]["pxgrid_cert"],
                                             CONFIG_DATA["ise"]["pxgrid_key"])

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        return '', 403

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.config.anc')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/getEndpointByMacAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, {"macAddress": mac_address})

    if pxgrid_response is not None:
        return jsonify(pxgrid_response)
    else:
        return '', 204


@app.route('/api/ise_anc_status', methods=['POST'])
def set_ise_anc_assignment():
    """A function to set the ISE ANC assignment for a given MAC address"""

    pxgrid = pxgrid_controller.PxgridControl(CONFIG_DATA["ise"]["address"],
                                             CONFIG_DATA["ise"]["pxgrid_name"],
                                             CONFIG_DATA["ise"]["pxgrid_cert"],
                                             CONFIG_DATA["ise"]["pxgrid_key"])

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        return '', 403

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.config.anc')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/applyEndpointByMacAddress'

    # Get the POST data from the request
    post_data = request.get_json()

    pxgrid_data = {
        "macAddress": post_data.get("mac_address"),
        "policyName": post_data.get("anc_policy")
    }

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, pxgrid_data)

    if pxgrid_response is not None:
        return jsonify(pxgrid_response)
    else:
        return '', 204


@app.route('/api/ise_anc_status/<mac_address>', methods=['DELETE'])
def clear_ise_anc_assignment(mac_address):
    """A function to clear the ISE ANC assignment for a given MAC address"""

    pxgrid = pxgrid_controller.PxgridControl(CONFIG_DATA["ise"]["address"],
                                             CONFIG_DATA["ise"]["pxgrid_name"],
                                             CONFIG_DATA["ise"]["pxgrid_cert"],
                                             CONFIG_DATA["ise"]["pxgrid_key"])

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        return '', 403

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.config.anc')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/clearEndpointByMacAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, {"macAddress": mac_address})

    if pxgrid_response is not None:
        return jsonify(pxgrid_response)
    else:
        return '', 204


@app.route('/api/ise_session_data/<ip_address>', methods=['GET'])
def get_ise_session_data(ip_address):
    """A function to look up the ISE session data for a given IP"""

    pxgrid = pxgrid_controller.PxgridControl(CONFIG_DATA["ise"]["address"],
                                             CONFIG_DATA["ise"]["pxgrid_name"],
                                             CONFIG_DATA["ise"]["pxgrid_cert"],
                                             CONFIG_DATA["ise"]["pxgrid_key"])

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        return '', 403

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.session')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/getSessionByIpAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, {"ipAddress": ip_address})

    if pxgrid_response is not None:
        return jsonify(pxgrid_response)
    else:
        return '', 204


def load_events():
    """A function to trigger all event imports into the database"""
    amp_event_importer.run()
    umbrella_event_importer.run()
    stealthwatch_event_importer.run()


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

        # Load events right out of the gate
        load_events()

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
