#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module is used to import Firepower syslog events into Cisco Command Center
"""

import json
import os
import re
import socketserver

import pymongo

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class FirepowerSyslogHandler():
    """
    A class to parse Firepower syslog events.
    """

    __db_address = None
    __db_username = None
    __db_password = None

    def __init__(self):
        self.__db_address = os.getenv("MONGO_INITDB_ADDRESS")
        self.__db_username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.__db_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    def _parse_event(self, data):
        """
        Parse the data using regex to extract the pertinent Firepower data.
        """

        # A Regex string for parsing Firepower IPS events generated by the FMC
        regex_string = r"([a-zA-z]{3}\s*\d{1,2}\s\d{2}:\d{2}:\d{2}) (\S*) SFIMS: \[([0-9:]*)\] \"([^\"]*)\"\s*" \
                       r"\[Impact: ([^\]]*)\]?\s*From \"([^\"]*)\" at ([a-zA-Z]{3}\s[a-zA-Z]{3}\s*\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4}\s\S*)\s*" \
                       r"\[Classification: ([^\]]*)\]?\s*\[Priority: ([^\]]*)\]\s\{([^\}]*)\} ([0-9.]*):?([0-9]*)?\s?\(?([^\)]*)\)?->([0-9.]*)" \
                       r":?([0-9]*)?\s*\(?([^\)]*)\)?"

        # Try to parse the event, if this fails None is returned
        parsed_event = re.search(regex_string, data, re.MULTILINE)

        # If we properly parsed the event, do stuff
        if parsed_event:

            # Store the parsed data into a dict
            event_json = {
                "product": "Firepower",
                "fmc_hostname": parsed_event.group(2),
                "snort_id": parsed_event.group(3),
                "snort_name": parsed_event.group(4),
                "event_name": parsed_event.group(4),
                "event_details": "{} event {} was detected by '{}'.".format(parsed_event.group(8), parsed_event.group(4), parsed_event.group(6)),
                "impact_level": parsed_event.group(5),
                "sensor_name": parsed_event.group(6),
                "timestamp": datetime.strptime(parsed_event.group(7), "%a %b %d %H:%M:%S %Y %Z"),
                "classification": parsed_event.group(8),
                "priority": parsed_event.group(9),
                "protocol": parsed_event.group(10),
                "src_ip": parsed_event.group(11),
                "src_port": parsed_event.group(12),
                "src_geo": parsed_event.group(13),
                "dst_ip": parsed_event.group(14),
                "dst_port": parsed_event.group(15),
                "dst_geo": parsed_event.group(16),
            }

            return event_json

        else:
            return None

    def _commit_to_db(self, event_json):
        """
        Commit the provided Event JSON to the database.
        """

        # Connect to the MongoDB instance
        db_client = pymongo.MongoClient("mongodb://{}/".format(self.__db_address),
                                        username=self.__db_username,
                                        password=self.__db_password)

        # Use the 'commandcenter' database
        command_center_db = db_client['commandcenter']

        # Use the 'events' collection from the 'commandcenter' database
        command_center_events = command_center_db['events']

        # Store the event in the database
        db_record = command_center_events.insert_one(event_json)

        print("Inserted Firepower event at MongoDB ID {}".format(db_record.inserted_id))


class SyslogHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for Command Center Syslog events.
    """

    def handle(self):
        """
        Handle when a packet is received on the socket.
        """

        self.data = bytes.decode(self.request[0].strip())
        self.socket = self.request[1]

        print("{} sent the following: {}".format(self.client_address[0], self.data))

        event_parser = FirepowerSyslogHandler()

        # Try to parse the event data
        event_json = event_parser._parse_event(self.data)

        # If the event was parsed
        if event_json:

            # Store the event
            event_parser._commit_to_db(event_json)


if __name__ == "__main__":

    try:
        server = socketserver.UDPServer(('0.0.0.0', 4514), SyslogHandler)
        server.serve_forever()
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")