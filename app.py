#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the main Python script to run Cisco Command Center

This script runs the Flask web server which handles the API backend (/api)
and the Vue.js frontend (/) for Cisco Command Center.

This script will also schedule events to be loaded into the database
at a regular interval.
"""


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
import xmltodict

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from modules import pxgrid_controller
from requests.auth import HTTPBasicAuth

# Configuration
DEBUG = False
PRODUCTION = True

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

    # If a product is specified, then use it.
    if 'product' in request.args:
        query_filter['product'] = {'$eq': request.args['product']}

    # If an event name is specified, then use it.
    if 'event_name' in request.args:
        query_filter['event_name'] = {'$eq': request.args['event_name']}

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


# Stealthwatch Functions
@app.route('/api/stealthwatch/host-snapshot', methods=['GET'])
def get_stealthwatch_host_snapshot():
    """A function to get host snapshots from Stealthwatch"""

    # Build the API URL
    api_url = "https://{}/smc/swsService/hosts".format(CONFIG_DATA["stealthwatch"]["address"])

    # Get the XML that we'll send to Stealthwatch
    xml = _get_stealthwatch_host_snapshot_xml(request.args['host_ip'])

    # Send the request to Stealthwatch
    http_request = requests.post(api_url,
                                 auth=HTTPBasicAuth(CONFIG_DATA["stealthwatch"]["username"],
                                                    CONFIG_DATA["stealthwatch"]["password"]),
                                 data=xml,
                                 verify=False)

    # Check to make sure the POST was successful
    if http_request.status_code == 200:

        # Return JSON formatted flows
        return jsonify(xmltodict.parse(http_request.text)['soapenc:Envelope']['soapenc:Body'])

    else:
        print('Stealthwatch Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit()


@app.route('/api/stealthwatch/flows', methods=['GET'])
def get_stealthwatch_flows():
    """A function to get recent flows from Stealthwatch"""

    # Build the API URL
    api_url = "https://{}/smc/swsService/flows".format(CONFIG_DATA["stealthwatch"]["address"])

    # Change the number of hours to milliseconds for Stealthwatch
    duration = int(request.args['timeframe']) * 60 * 60 * 1000

    # Get the XML that we'll send to Stealthwatch
    xml = _get_stealthwatch_flows_xml(duration, request.args['host_ip'])

    # Send the request to Stealthwatch
    http_request = requests.post(api_url,
                                 auth=HTTPBasicAuth(CONFIG_DATA["stealthwatch"]["username"],
                                                    CONFIG_DATA["stealthwatch"]["password"]),
                                 data=xml,
                                 verify=False)

    # Check to make sure the POST was successful
    if http_request.status_code == 200:

        # Return JSON formatted flows
        return jsonify(xmltodict.parse(http_request.text)['soapenc:Envelope']['soapenc:Body'])

    else:
        print('Stealthwatch Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit()


def _get_stealthwatch_host_snapshot_xml(host_ip):
    """A function to generate XML to fetch host snapshots from Stealthwatch"""

    # Build the XML
    return_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\">
        <soapenv:Body>
            <getHostSnapshot>
                <host-filter domain-id=\"{}\">
                    <host-selection>
                        <ip-address-selection value=\"{}\"/>
                    </host-selection>
                </host-filter>
            </getHostSnapshot>
        </soapenv:Body>
    </soapenv:Envelope>""".format(CONFIG_DATA["stealthwatch"]["tenant"], host_ip)

    return return_xml


def _get_stealthwatch_flows_xml(duration, host_ip):
    """A function to generate XML to fetch flows from Stealthwatch"""

    # Build the XML
    return_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <soapenc:Envelope xmlns:soapenc=\"http://schemas.xmlsoap.org/soap/envelope/\">
        <soapenc:Body>
            <getFlows>
                <flow-filter max-rows=\"10000\" domain-id=\"{}\" remove-duplicates=\"true\" order-by=\"TOTAL_BYTES\" order-by-desc=\"true\" include-interface-data=\"false\">
                    <date-selection>
                        <time-window-selection duration=\"{}\"/>
                    </date-selection>
                    <host-selection>
                        <host-pair-selection direction=\"BETWEEN_SELECTION_1_SELECTION_2\">
                            <selection-1>
                                <ip-address-list-selection>
                                    <ip-address value=\"{}\" />
                                </ip-address-list-selection>
                            </selection-1>
                        </host-pair-selection>
                    </host-selection>
                    <protocols>1,6,17</protocols>
                </flow-filter>
            </getFlows>
        </soapenc:Body>
    </soapenc:Envelope>""".format(CONFIG_DATA["stealthwatch"]["tenant"], duration, host_ip)

    return return_xml


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

# If in production, load the Vue.js routes
if PRODUCTION:

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template("index.html")

if __name__ == '__main__':

    # Load the config data
    load_config()

    # Run the webserver
    app.run(host='0.0.0.0')
