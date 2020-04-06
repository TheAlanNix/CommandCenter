#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Python module to extend the API Relay for Cisco's Stealthwatch Enterprise
"""

import os

import requests
import xmltodict
import modules.cisco_stealthwatch.stealthwatch_client as stealtwatch_client

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

router = APIRouter()

# Stealthwatch Functions
@router.get('/flows')
def get_flows(ip_address: str, timeframe: int):
    """A function to get recent flows from Stealthwatch"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("STEALTHWATCH_API_ADDRESS") or
        not os.getenv("STEALTHWATCH_API_USERNAME") or
        not os.getenv("STEALTHWATCH_API_PASSWORD")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Build the API URL
    api_url = "https://{}/smc/swsService/flows".format(os.getenv("STEALTHWATCH_API_ADDRESS"))

    # Change the number of hours to milliseconds for Stealthwatch
    duration = timeframe * 60 * 60 * 1000

    # Get the XML that we'll send to Stealthwatch
    xml = _get_stealthwatch_flows_xml(duration, ip_address)

    # Send the request to Stealthwatch
    http_request = requests.post(api_url,
                                 auth=HTTPBasicAuth(os.getenv("STEALTHWATCH_API_USERNAME"),
                                                    os.getenv("STEALTHWATCH_API_PASSWORD")),
                                 data=xml,
                                 verify=False)

    # Check to make sure the POST was successful
    if http_request.status_code == 200:

        response = xmltodict.parse(http_request.text)['soapenc:Envelope']['soapenc:Body']

        if response['getFlowsResponse']['flow-list']:
            # Return JSON formatted flows
            return response
        else:
            # If Stealthwatch returns nothing, return a 204
            return Response(status_code=204)

    else:
        print('Stealthwatch Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code,
                                                                                            http_request.text))
        exit()


def _get_stealthwatch_flows_xml(duration, ip_address):
    """A function to generate XML to fetch flows from Stealthwatch"""

    # Build the XML
    return_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <soapenc:Envelope xmlns:soapenc=\"http://schemas.xmlsoap.org/soap/envelope/\">
        <soapenc:Body>
            <getFlows>
                <flow-filter max-rows=\"10000\"
                             domain-id=\"{}\"
                             remove-duplicates=\"true\"
                             order-by=\"TOTAL_BYTES\"
                             order-by-desc=\"true\"
                             include-interface-data=\"false\">
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
    </soapenc:Envelope>""".format(os.getenv("STEALTHWATCH_API_TENANT"), duration, ip_address)

    return return_xml

@router.get('/host-snapshot')
def get_host_snapshot(ip_address: str):
    """A function to get host snapshots from Stealthwatch"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("STEALTHWATCH_API_ADDRESS") or
        not os.getenv("STEALTHWATCH_API_USERNAME") or
        not os.getenv("STEALTHWATCH_API_PASSWORD")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Build the API URL
    api_url = "https://{}/smc/swsService/hosts".format(os.getenv("STEALTHWATCH_API_ADDRESS"))

    # Get the XML that we'll send to Stealthwatch
    xml = _get_stealthwatch_host_snapshot_xml(ip_address)

    # Send the request to Stealthwatch
    http_request = requests.post(api_url,
                                 auth=HTTPBasicAuth(os.getenv("STEALTHWATCH_API_USERNAME"),
                                                    os.getenv("STEALTHWATCH_API_PASSWORD")),
                                 data=xml,
                                 verify=False)

    # Check to make sure the POST was successful
    if http_request.status_code == 200:

        # Return JSON formatted flows
        return xmltodict.parse(http_request.text)['soapenc:Envelope']['soapenc:Body']

    else:
        # If Stealthwatch returns nothing, return a 204
        return Response(status_code=204)


def _get_stealthwatch_host_snapshot_xml(ip_address):
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
    </soapenv:Envelope>""".format(os.getenv("STEALTHWATCH_API_TENANT"), ip_address)

    return return_xml



