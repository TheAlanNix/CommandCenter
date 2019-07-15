#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module is used to import Cisco Stealthwatch events into Cisco Command Center
"""

import json
import time

import pymongo
import requests

from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from requests.packages import urllib3

try:
    urllib3.disable_warnings()
except:
    pass


CONFIG_FILE = "./config.json"
CONFIG_DATA = None

# Initialize a requests session
API_SESSION = requests.Session()

###################
#    FUNCTIONS    #
###################


def load_config():
    """Load the Configuration JSON"""
    global CONFIG_DATA

    print("Loading Config Data...")

    with open(CONFIG_FILE, 'r') as json_config_file:
        CONFIG_DATA = json.loads(json_config_file.read())


def login():
    """Log in to Stealthwatch"""

    print("Logging in to Stealthwatch...")

    # Set the URL for SMC login
    url = "https://" + CONFIG_DATA["stealthwatch"]["address"] + "/token/v2/authenticate"

    # Create the login request data
    login_request_data = {
        "username": CONFIG_DATA["stealthwatch"]["username"],
        "password": CONFIG_DATA["stealthwatch"]["password"]
    }

    # Perform the POST request to login
    response = API_SESSION.request("POST", url, verify=False, data=login_request_data)

    if (response.status_code != 200):
        print("An error has ocurred, while logging in, with the following code {}".format(response.status_code))
        exit()


def get_event_names():
    """Get Stealthwatch Event Names"""

    print("Getting Stealthwatch event names...")

    # Set the URL for getting the Security Events
    url = 'https://' + CONFIG_DATA["stealthwatch"]["address"] + '/sw-reporting/v1/tenants/' + CONFIG_DATA["stealthwatch"]["tenant"] + '/security-events/templates'

    # Build the request headers
    request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    # Perform the query to initiate the search
    response = API_SESSION.request("GET", url, verify=False, headers=request_headers)

    # If successful
    if (response.status_code == 200):

        # Store the event names
        return json.loads(response.content)["data"]
    else:
        print("An error has occured while fetching event names.  HTTP Code: {}".format(response.status_code))
        exit()


def get_events(start_date=None):
    """Get Stealthwatch Events"""

    # Set the URL for the query to POST the filter and initiate the search
    url = 'https://' + CONFIG_DATA["stealthwatch"]["address"] + '/sw-reporting/v1/tenants/' + CONFIG_DATA["stealthwatch"]["tenant"] + '/security-events/queries'

    # Set the current time as the end
    end_datetime = datetime.utcnow()

    # If a start date is specified, use it, otherwise get the previous day
    if start_date is None:
        start_datetime = end_datetime - timedelta(days=1)
    else:
        start_datetime = start_date

    # Format the timestamps for Stealtwatch
    end_timestamp = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    start_timestamp = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Set the filter with the request data
    request_data = {
        "timeRange": {
            "from": start_timestamp,
            "to": end_timestamp
        }
    }

    # Build the request headers
    request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    # Perform the query to initiate the search
    response = API_SESSION.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)

    # If successfully able to initiate search, grab the search details
    if (response.status_code == 200):
        print("Getting Event Query results. Please wait...")
        search = json.loads(response.content)["data"]["searchJob"]
        search_id = search["id"]

        # Set the URL to check the search status
        url = url + '/' + search_id

        # While search status is not complete, check the status every second
        while search["percentComplete"] != 100.0:
            response = API_SESSION.request("GET", url, verify=False)
            search = json.loads(response.content)["data"]
            print("{}% Complete...".format(search["percentComplete"]))
            time.sleep(1)

        # Set the URL to check the search results and get them
        url = 'https://' + CONFIG_DATA["stealthwatch"]["address"] + '/sw-reporting/v1/tenants/' + CONFIG_DATA["stealthwatch"]["tenant"] + '/security-events/results/' + search_id
        response = API_SESSION.request("GET", url, verify=False)

        # Return the results
        return response.json()

    # If unable to update the IPs for a given tag (host group)
    else:
        print("An error has ocurred, while getting security events, with the following code {}".format(response.status_code))
        exit()


def clear_events(event_table):
    """Clear Stealthwatch events with an ID of '0'"""

    # Setup a query for Stealthwatch events with ID '0'
    sw_zero_query = {"product": "Stealthwatch", "id": 0}

    # Delete the events with ID '0'
    results = event_table.delete_many(sw_zero_query)

    print(results.deleted_count, " documents deleted.")


def event_name_lookup(id, event_names):
    """Get the human readable event name"""

    for event_name in event_names:
        if id == event_name["id"]:
            return (event_name["name"], event_name["description"])


def run():
    """Main function to get new Stealthwatch events and commit them to the MongoDB database"""

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

    # Delete SW Events with ID '0'
    clear_events(command_center_events)

    # Get the latest 'Stealthwatch' event
    latest_event = command_center_events.find({"product": "Stealthwatch", "id": {"$ne": 0}}).sort("timestamp", -1)

    # If there's no latest event, the Event collection is empty, so we create a timestamp to import from.
    if latest_event.count():
        latest_event = latest_event[0]
    else:
        print("No events in database.  Setting latest_event timestamp to 30 days ago.")
        start_date = datetime.utcnow().replace(microsecond=0) + timedelta(-30)
        latest_event = {"timestamp": start_date}

    print("Latest Stealtwatch Event: ", latest_event['timestamp'])

    # Log in to Stealtwatch
    login()

    # Get the Stealthwatch event names
    event_names = get_event_names()

    # Get the latest Stealthwatch events
    stealthwatch_events = get_events(latest_event['timestamp'])

    # Iterate through all fetched events
    for event in stealthwatch_events['data']['results']:

        # Filters for some really chatty event types
        #   310: Flow_Denied
        if event["securityEventType"] in [310]:
            continue

        # A placholder to see if we've already imported this event
        event_exists = False

        # If the event ID isn't zero, then check to see if we've already imported it
        if event["id"]:

            # Query to see if the event ID exists
            existing_event = command_center_events.find_one({"product": "Stealthwatch", "id": event["id"]})

            # Print a logging message
            if existing_event:
                event_exists = True
                print(f"Found that the event already exists: {event['id']}")

        current_event_time = datetime.strptime(event["lastActiveTime"], "%Y-%m-%dT%H:%M:%S.%f+0000")
        latest_event_time = latest_event["timestamp"]

        if current_event_time > latest_event_time:

            # Make common fields for the event
            (event["event_name"], event["event_details"]) = event_name_lookup(event["securityEventType"], event_names)

            event_common_fields = {
                "product": "Stealthwatch",
                "src_ip": event["source"]["ipAddress"],
                "timestamp": current_event_time
            }

            # Add the common fields to the event
            event.update(event_common_fields)

            if event_exists:

                # Update the event in the database
                x = command_center_events.replace_one({"_id": existing_event["_id"]}, event)

                print("Updated Stealthwatch Event ID {} at MongoDB ID {}".format(event["id"], x.inserted_id))

            else:

                # Store the event in the database
                x = command_center_events.insert_one(event)

                print("Inserted Stealthwatch Event ID {} at MongoDB ID {}".format(event["id"], x.inserted_id))

###################
# !!! DO WORK !!! #
###################

if __name__ == "__main__":

    # Run the script
    run()
