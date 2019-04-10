#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module is used to communicate with pxGrid for Cisco Command Center
"""

import base64
import json
import ssl
import time
import urllib.request


class PxgridControl:
    def __init__(self, address, client_name, client_cert, client_key):
        self.address = address
        self.client_name = client_name
        self.client_cert = client_cert
        self.client_key = client_key

    def send_rest_request(self, url_suffix, payload):

        # Build the API URL
        api_url = 'https://{}:8910/pxgrid/{}'.format(self.address, url_suffix)

        # Make the payload into JSON
        json_string = json.dumps(payload)

        print("API URL: " + api_url)
        print("Payload: " + json_string)

        # Build the SSL Context
        handler = urllib.request.HTTPSHandler(context=self.get_ssl_context())
        opener = urllib.request.build_opener(handler)

        rest_request = urllib.request.Request(url=api_url, data=str.encode(json_string))
        rest_request.add_header('Content-Type', 'application/json')
        rest_request.add_header('Accept', 'application/json')

        b64 = base64.b64encode((self.client_name + ':').encode()).decode()
        rest_request.add_header('Authorization', 'Basic ' + b64)
        rest_response = opener.open(rest_request)
        response = rest_response.read().decode()

        if response is not '':
            print("Response:" + json.dumps(json.loads(response), indent=4))
            return json.loads(response)
        else:
            return None

    def account_activate(self):
        payload = {}
        return self.send_rest_request('control/AccountActivate', payload)

    def service_lookup(self, service_name):
        payload = {'name': service_name}
        return self.send_rest_request('control/ServiceLookup', payload)

    def get_access_secret(self, peer_node_name):
        payload = {'peerNodeName': peer_node_name}
        return self.send_rest_request('control/AccessSecret', payload)

    def get_ssl_context(self):

        # Create an SSL context for client auth
        context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)

        # Load the client certificate
        if self.client_cert is not None:
            context.load_cert_chain(certfile=self.client_cert,
                                    keyfile=self.client_key)

        return context
