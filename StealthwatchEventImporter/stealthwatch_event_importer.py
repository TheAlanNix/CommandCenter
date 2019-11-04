#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module is used to import Cisco Stealthwatch events into Cisco Command Center
"""

import json
import os
import time

import pymongo
import requests

from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from requests.packages import urllib3

load_dotenv()

try:
    urllib3.disable_warnings()
except:
    pass

# Initialize a requests session
API_SESSION = requests.Session()


def login():
    """Log in to Stealthwatch"""

    print("Logging in to Stealthwatch...")

    # Set the URL for SMC login
    url = f"https://{os.getenv('STEALTHWATCH_API_ADDRESS')}/token/v2/authenticate"

    # Create the login request data
    login_request_data = {
        "username": os.getenv("STEALTHWATCH_API_USERNAME"),
        "password": os.getenv("STEALTHWATCH_API_PASSWORD")
    }

    # Perform the POST request to login
    response = API_SESSION.request("POST", url, verify=False, data=login_request_data)

    if (response.status_code != 200):
        print(f"An error has ocurred, while logging in, with the following code {response.status_code}")
        exit(1)


def get_event_names():
    """Get Stealthwatch Event Names"""

    print("Getting Stealthwatch event names...")

    # Set the URL for getting the Security Events Templates
    url = f"https://{os.getenv('STEALTHWATCH_API_ADDRESS')}/sw-reporting/v1/tenants/{os.getenv('STEALTHWATCH_API_TENANT')}" \
           "/security-events/templates"

    # Build the request headers
    request_headers = {"Content-type": "application/json", "Accept": "application/json"}

    # Perform the Get request
    response = API_SESSION.request("GET", url, verify=False, headers=request_headers)

    # If successful
    if (response.status_code == 200):

        # Store the event names
        event_names = json.loads(response.content)["data"]

        # Make a placeholder dict
        return_dict = {}

        # Store a tuple of the name and description with a key of the ID
        for event_name in event_names:
            return_dict[event_name["id"]] = (event_name["name"], event_name["description"])

        return return_dict
    else:
        print(f"An error has occured while fetching event names.  HTTP Code: {response.status_code}")
        exit(1)


def get_events(start_date=None, end_date=None):
    """Get Stealthwatch Events"""

    # Set the URL for the query to POST the filter and initiate the search
    url = f"https://{os.getenv('STEALTHWATCH_API_ADDRESS')}/sw-reporting/v1/tenants/{os.getenv('STEALTHWATCH_API_TENANT')}" \
           "/security-events/queries"

    # If an end date is specified, use it, otherwise set it to now
    if end_date is None:
        # Set the current time as the end
        end_datetime = datetime.utcnow()
    else:
        end_datetime = end_date

    # If a start date is specified, use it, otherwise get the previous day
    if start_date is None:
        start_datetime = end_datetime - timedelta(days=1)
    else:
        start_datetime = start_date

    # Format the timestamps for Stealtwatch
    end_timestamp = end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_timestamp = start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Set the filter with the request data
    request_data = {
        "timeRange": {
            "from": start_timestamp,
            "to": end_timestamp
        }
    }

    # Build the request headers
    request_headers = {"Content-type": "application/json", "Accept": "application/json"}

    # Perform the query to initiate the search
    response = API_SESSION.request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)

    # If successfully able to initiate search, grab the search details
    if (response.status_code == 200):
        print("Getting Event Query results. Please wait...")
        search = json.loads(response.content)["data"]["searchJob"]
        search_id = search["id"]

        # Set the URL to check the search status
        url = url + "/" + search_id

        # While search status is not complete, check the status every second
        while search["percentComplete"] != 100.0:
            response = API_SESSION.request("GET", url, verify=False)
            search = json.loads(response.content)["data"]
            print(f"{search['percentComplete']}% Complete...")
            time.sleep(1)

        # Set the URL to check the search results and get them
        url = f"https://{os.getenv('STEALTHWATCH_API_ADDRESS')}/sw-reporting/v1/tenants/{os.getenv('STEALTHWATCH_API_TENANT')}" \
              f"/security-events/results/{search_id}"

        response = API_SESSION.request("GET", url, verify=False)

        # Return the results
        return response.json()

    # If unable to update the IPs for a given tag (host group)
    else:
        print(f"An error has ocurred, while getting security events, with the following code {response.status_code}")
        exit(1)


def get_existing_event(event_table, event):
    """A function to search the database for an existing active event"""

    # Set up a query to look for an identical active event
    active_event_query = {
        "id": 0,
        "product": "Stealthwatch",
        "firstActiveTime": event["firstActiveTime"],
        "securityEventType": event["securityEventType"],
        "source": event["source"],
        "target": event["target"]
    }

    # Get the event
    event = event_table.find_one(active_event_query)

    return event


def run():
    """Main function to get new Stealthwatch events and commit them to the MongoDB database"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGO_INITDB_ADDRESS')}/",
                                    username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                                    password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    # Use the 'commandcenter' database
    command_center_db = db_client["commandcenter"]

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db["events"]

    # Get the latest 'Stealthwatch' event
    latest_event = command_center_events.find({"product": "Stealthwatch"}).sort("timestamp", -1)

    # If there's no latest event, the Event collection is empty, so we create a timestamp to import from.
    if latest_event.count():
        latest_event = latest_event[0]
    else:
        print("No events in database.  Setting latest_event timestamp to 1 days ago.")
        start_date = datetime.utcnow().replace(microsecond=0) + timedelta(-1)
        latest_event = {"timestamp": start_date}

    print("Latest Stealtwatch Event: ", latest_event["timestamp"])

    # Log in to Stealtwatch
    login()

    # Get the Stealthwatch event names
    event_names = get_event_names()

    # Get the latest Stealthwatch events
    stealthwatch_events = get_events(latest_event["timestamp"])

    print("Total Events Returned: ", len(stealthwatch_events["data"]["results"]))

    # Iterate through all fetched events
    for event in stealthwatch_events["data"]["results"]:

        # Filters for some really chatty event types
        #   262: Reset/TCP
        #   310: Flow_Denied
        if event["securityEventType"] in [262, 310]:
            continue

        # Check to see if there's an existing active event
        existing_event = get_existing_event(command_center_events, event)

        current_event_time = datetime.strptime(event["lastActiveTime"], "%Y-%m-%dT%H:%M:%S.%f+0000")
        latest_event_time = latest_event["timestamp"]

        if current_event_time > latest_event_time:

            # Make common fields for the event
            (event["event_name"], event["event_details"]) = event_names[event["securityEventType"]]

            event_common_fields = {
                "product": "Stealthwatch",
                "src_ip": event["source"]["ipAddress"],
                "timestamp": current_event_time,
                "formatted_timestamp": current_event_time.strftime("%b %d, %Y %H:%M:%S UTC")
            }

            # Add the common fields to the event
            event.update(event_common_fields)

            if existing_event:

                # Update the event in the database
                x = command_center_events.replace_one({"_id": existing_event["_id"]}, event)

                print(f"Updated Stealthwatch Event ID {event['id']} at MongoDB ID {existing_event['_id']}")

            else:

                # Store the event in the database
                x = command_center_events.insert_one(event)

                print(f"Inserted Stealthwatch Event ID {event['id']} at MongoDB ID {x.inserted_id}")

###################
# !!! DO WORK !!! #
###################

if __name__ == "__main__":

    # Cast the interval as an int
    sleep_time = int(os.getenv("STEALTHWATCH_API_LOAD_INTERVAL"))

    # If the Stealthwatch API is configured
    while os.getenv("STEALTHWATCH_API_ADDRESS"):

        # Run the script
        run()

        # Wait a specified amount of time
        time.sleep(sleep_time)

    print("Stealthwatch API not enabled. Exiting.")
