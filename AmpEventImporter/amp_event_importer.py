#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is used to import Cisco AMP for Endpoints events into Cisco Command Center
"""

import json
import os
import time

import pymongo
import requests

from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def get_events(start_date=None):
    """Get AMP events"""

    # Format the date for AMP
    start_date = start_date.isoformat()

    # Build the API URL
    api_url = "https://{}/v1/events?start_date={}&event_type[]=1090519054&event_type[]=553648147&event_type[]=553648168&event_type[]=1090519084".format(os.getenv("AMP_API_FQDN"), start_date)

    print("Fetching {}".format(api_url))

    # Get AMP Events
    http_request = requests.get(api_url, auth=HTTPBasicAuth(os.getenv("AMP_API_CLIENT_ID"), os.getenv("AMP_API_KEY")))

    # Check to make sure the GET was successful
    if http_request.status_code == 200:
        return http_request.json()
    else:
        print('AMP Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit(1)


def run():
    """Main function to get new AMP events and commit them to the MongoDB database"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(os.getenv("MONGO_INITDB_ADDRESS")),
                                    username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                                    password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    # Use the specified database
    command_center_db = db_client[os.getenv("MONGO_INITDB_DATABASE")]

    # Use the 'events' collection from the specified database
    command_center_events = command_center_db['events']

    # Get the count of AMP for Endpoints documents
    event_count = command_center_events.count_documents({"product": "AMP for Endpoints"})

    # If there's no latest event, the Event collection is empty, so we create a timestamp to import from.
    if event_count:

        # Get the latest 'AMP for Endpoints' event
        latest_event = command_center_events.find({"product": "AMP for Endpoints"}).sort("timestamp", -1)
        latest_event = latest_event[0]
    else:
        print("No events in database.  Setting latest_event timestamp to 30 days ago.")
        start_date = datetime.utcnow().replace(microsecond=0) + timedelta(-30)
        latest_event = {"timestamp": start_date}

    print("Latest AMP Event: ", latest_event['timestamp'])

    # Get the latest AMP events
    amp_events = get_events(latest_event['timestamp'])

    # Iterate through all fetched events
    for event in amp_events['data']:

        current_event_time = datetime.strptime(event["date"], "%Y-%m-%dT%H:%M:%S+00:00")
        latest_event_time = latest_event["timestamp"]

        src_ip = None

        # Get the first network address that isn't empty
        for network_address in event['computer']['network_addresses']:
            if network_address['ip']:
                src_ip = network_address['ip']
                break

        # If no network address was found, then fall back to the external IP
        if not src_ip:
            src_ip = event['computer']['external_ip']

        if current_event_time > latest_event_time:

            # Make common fields for the event
            event_common_fields = {
                "event_name": event["event_type"],
                "event_details": event["detection"],
                "product": "AMP for Endpoints",
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
    sleep_time = int(os.getenv("AMP_API_LOAD_INTERVAL"))

    # If the AMP API is configured
    while os.getenv("AMP_API_CLIENT_ID"):

        # Run the script
        run()

        # Wait a specified amount of time
        time.sleep(sleep_time)

    print("AMP API not enabled. Exiting.")
