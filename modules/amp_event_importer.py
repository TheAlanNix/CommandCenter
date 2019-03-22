#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module is used to import Cisco AMP for Endpoints events into Cisco Command Center
"""

import json

import pymongo
import requests

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

CONFIG_FILE = "./config.json"
CONFIG_DATA = None

###################
#    FUNCTIONS    #
###################


def load_config():
    """Load the Configuration JSON"""
    global CONFIG_DATA

    print("Loading Config Data...")

    with open(CONFIG_FILE, 'r') as json_config_file:
        CONFIG_DATA = json.loads(json_config_file.read())


def get_events(start_date=None):
    """Get AMP events"""

    # Format the date for AMP
    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S+00:00")
    start_date = start_date.isoformat()

    # Build the API URL
    api_url = "https://{}//v1/events?start_date={}&event_type[]=1090519054&event_type[]=553648147&event_type[]=553648168&event_type[]=1090519084".format(CONFIG_DATA["amp"]["api_fqdn"], start_date)

    print("Fetching {}".format(api_url))

    # Get AMP Events
    http_request = requests.get(api_url, auth=HTTPBasicAuth(CONFIG_DATA["amp"]["client_id"], CONFIG_DATA["amp"]["api_key"]))

    # Check to make sure the GET was successful
    if http_request.status_code == 200:
        return http_request.json()
    else:
        print('AMP Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit()


def run():
    """Main function to get new AMP events and commit them to the MongoDB database"""

    # Load the config data
    load_config()

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(CONFIG_DATA["database"]["address"]),
                                    username=CONFIG_DATA["database"]["username"],
                                    password=CONFIG_DATA["database"]["password"])

    # Use the 'commandcenter' database
    command_center_db = db_client['commandcenter']

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db['events']

    # Get the latest 'AMP for Endpoints' event
    latest_event = command_center_events.find({"product": "AMP for Endpoints"}).sort("timestamp", -1)

    # If there's no latest event, the Event collection is empty, so we create a timestamp to import from.
    if latest_event.count() > 0:
        latest_event = latest_event[0]
    else:
        print("No events in database.  Setting latest_event timestamp to 30 days ago.")
        start_date = datetime.utcnow().replace(microsecond=0) + timedelta(-30)
        latest_event = {"timestamp": start_date.isoformat() + "+00:00"}

    print("Latest AMP Event: ", latest_event['timestamp'])

    # Get the latest AMP events
    amp_events = get_events(latest_event['timestamp'])

    # Iterate through all fetched events
    for event in amp_events['data']:

        current_event_time = datetime.strptime(event["date"], "%Y-%m-%dT%H:%M:%S+00:00")
        latest_event_time = datetime.strptime(latest_event["timestamp"], "%Y-%m-%dT%H:%M:%S+00:00")

        if current_event_time > latest_event_time:

            # Make common fields for the event
            event_common_fields = {
                "event_name": event["event_type"],
                "event_details": event["detection"],
                "product": "AMP for Endpoints",
                "src_ip": event['computer']['network_addresses'][0]['ip'],
                "timestamp": event["date"]
            }

            # Add the common fields to the event
            event.update(event_common_fields)

            # Store the event in the database
            x = command_center_events.insert_one(event)

            print(x.inserted_id)

###################
# !!! DO WORK !!! #
###################

if __name__ == "__main__":

    # Run the script
    run()
