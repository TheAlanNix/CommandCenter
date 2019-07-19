#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is used to import Cisco Umbrella events into Cisco Command Center
"""

import json
import os
import time

import pymongo
import requests

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def get_events(start_date=None):
    """Get Umbrella events"""

    # Format the date for AMP
    start_date = int(start_date.replace(tzinfo=timezone.utc).timestamp())

    # Build the API URL
    api_url = "https://reports.api.umbrella.com/v1/organizations/{}/security-activity?limit=500&start={}".format(os.getenv("UMBRELLA_API_ORG_ID"), start_date)

    print("Fetching {}".format(api_url))

    # Get Umbrella Events
    http_request = requests.get(api_url, auth=HTTPBasicAuth(os.getenv("UMBRELLA_API_REPORTING_KEY"), os.getenv("UMBRELLA_API_REPORTING_SECRET")))

    # Check to make sure the GET was successful
    if http_request.status_code == 200:
        return http_request.json()
    else:
        print('Umbrella Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit()


def run():
    """Main function to get new Umbrella events and commit them to the MongoDB database"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(os.getenv("MONGO_INITDB_ADDRESS")),
                                    username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                                    password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    # Use the specified database
    command_center_db = db_client[os.getenv("MONGO_INITDB_DATABASE")]

    # Use the 'events' collection from the specified database
    command_center_events = command_center_db['events']

    # Get the count of Umbrella documents
    event_count = command_center_events.count_documents({"product": "Umbrella"})

    # If there are no events, the Event collection is empty, so we create a timestamp to import from.
    if event_count:

        # Get the latest 'Umbrella' event
        latest_event = command_center_events.find({"product": "Umbrella"}).sort("timestamp", -1)
        latest_event = latest_event[0]
    else:
        print("No events in database.  Setting latest_event timestamp to 24 hours ago. (The maximum for Umbrella)")
        start_date = datetime.utcnow().replace(microsecond=0) + timedelta(hours=-24)
        latest_event = {"timestamp": start_date}

    print("Latest Umbrella Event: ", latest_event['timestamp'])

    # Get the latest Umbrella events
    umbrella_events = get_events(latest_event['timestamp'])

    # Iterate through all fetched events
    for event in umbrella_events['requests']:

        current_event_time = datetime.strptime(event["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        latest_event_time = latest_event["timestamp"]

        if current_event_time > latest_event_time:

            if event["internalIp"]:
                src_ip = event["internalIp"]
            else:
                src_ip = event["externalIp"]

            # Make common fields for the event
            event_common_fields = {
                "event_name": "Umbrella {} Destination".format(event["actionTaken"]),
                "event_details": "Umbrella {} the following destination: {}".format(event["actionTaken"], event["destination"]),
                "product": "Umbrella",
                "src_ip": src_ip,
                "timestamp": current_event_time
            }

            # Add the common fields to the event
            event.update(event_common_fields)

            # Store the event in the database
            x = command_center_events.insert_one(event)

            print(x.inserted_id)


if __name__ == "__main__":

    # Cast the interval as an int
    sleep_time = int(os.getenv("UMBRELLA_API_LOAD_INTERVAL"))

    # If the AMP API is configured
    while os.getenv("UMBRELLA_API_REPORTING_KEY"):

        # Run the script
        run()

        # Wait a specified amount of time
        time.sleep(sleep_time)

    print("Umbrella API not enabled. Exiting.")
