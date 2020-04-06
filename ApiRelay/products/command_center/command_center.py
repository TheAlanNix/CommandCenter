#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Python module to extend the API Relay for Command Center.
"""

import json
import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime, timedelta

import pymongo

from dotenv import load_dotenv
from fastapi import APIRouter

# Load the .env
load_dotenv()

router = APIRouter()

# Events Functions
@router.get('/events')
def get_events(timeframe: int, event_name: str = None, product: str = None, src_ip: str = None):
    """A function to retrieve events from the database and return them as JSON"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(os.getenv("MONGO_INITDB_ADDRESS")),
                                    username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                                    password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    # Use the 'commandcenter' database
    command_center_db = db_client['commandcenter']

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db['events']

    # Set up a basic query filter
    query_filter = {}

    # If the source IP is specified, then only return those events.
    if src_ip:
        query_filter['src_ip'] = src_ip

    # If a timeframe is specified, then use it.
    if timeframe:
        query_date = datetime.utcnow().replace(microsecond=0) - timedelta(hours=timeframe)
        query_filter['timestamp'] = {'$gte': query_date}

    # If a product is specified, then use it.
    if product:
        query_filter['product'] = {'$eq': product}

    # If an event name is specified, then use it.
    if event_name:
        query_filter['event_name'] = {'$eq': event_name}

    # Projection to return a subset of fields
    projection = {
        'event_name': 1,
        'event_details': 1,
        'product': 1,
        'src_ip': 1,
        'timestamp': 1
    }

    # Get the events
    latest_events = command_center_events.find(query_filter, projection).sort('timestamp', -1)

    # Set up a response object
    response_object = {
        'status': 'success',
        'events': [],
    }

    # Iterate through all events
    for event in latest_events:

        # Make a human readable date if one doesn't exist - starting to do this on event import now
        if 'formatted_timestamp' not in event.keys():
            event['formatted_timestamp'] = event["timestamp"].strftime("%b %d, %Y %H:%M:%S UTC")

        # Append the event to the response
        response_object['events'].append(json.loads(dumps(event)))

    return response_object


@router.get('/event/{event_id}')
def get_event(event_id: str):
    """A function to retrieve an event from the database and return it as JSON"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(os.getenv("MONGO_INITDB_ADDRESS")),
                                    username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                                    password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    # Use the 'commandcenter' database
    command_center_db = db_client['commandcenter']

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db['events']

    # Set up a basic query filter
    query_filter = {}

    # Filter for the specified event ID
    query_filter['_id'] = ObjectId(event_id)

    # Get the event
    event = command_center_events.find_one(query_filter)

    # Make a human readable timestamp
    event['formatted_timestamp'] = event["timestamp"].strftime("%b %d, %Y %H:%M:%S UTC")

    # Parse the bson event into json
    event = json.loads(dumps(event))

    # Set up a response object
    response_object = {
        'status': 'success',
        'event': [event],
    }

    return response_object


@router.get('/events-over-time')
def get_events_over_time(timeframe: int, event_name: str = None, product: str = None, src_ip: str = None):
    """A function to retrieve event counts from the database aggregated into intervals and return them as JSON"""

    # Connect to the MongoDB instance
    db_client = pymongo.MongoClient("mongodb://{}/".format(os.getenv("MONGO_INITDB_ADDRESS")),
                                    username=os.getenv("MONGO_INITDB_ROOT_USERNAME"),
                                    password=os.getenv("MONGO_INITDB_ROOT_PASSWORD"))

    # Use the 'commandcenter' database
    command_center_db = db_client['commandcenter']

    # Use the 'events' collection from the 'commandcenter' database
    command_center_events = command_center_db['events']

    # Set up a basic query filter
    query_filter = {}

    # If the source IP is specified, then only return those events.
    if src_ip:
        query_filter['src_ip'] = src_ip

    # If a timeframe is specified, then use it.
    if timeframe:
        query_date = datetime.utcnow().replace(microsecond=0) - timedelta(hours=timeframe)
        query_filter['timestamp'] = {'$gte': query_date}

    # If a product is specified, then use it.
    if product:
        query_filter['product'] = {'$eq': product}

    # If an event name is specified, then use it.
    if event_name:
        query_filter['event_name'] = {'$eq': event_name}

    # Get the aggregated events
    aggregated_events = command_center_events.aggregate([
        {"$match": query_filter},
        {"$group":
            {"_id":
                {"$toDate":
                    {"$subtract": [
                        {"$toLong": "$timestamp"},
                        {"$mod": [
                            {"$toLong": "$timestamp"},
                            1000 * 60 * 5
                        ]}
                    ]}},
                "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ])

    # Set up a response object
    response_object = {
        'status': 'success',
        'event_counts': [],
    }

    # Iterate through all events
    for event in aggregated_events:

        # Append the event to the response
        response_object['event_counts'].append(json.loads(dumps(event)))

    return response_object
