#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Python module to extend the API Relay for Cisco's AMP for Endpoints
"""

import json
import os

import requests
import modules.cisco_ise.pxgrid_client as pxgrid_client

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

class AncData(BaseModel):
    macAddress: str
    policyName: str

router = APIRouter()

# ISE Functions
@router.get('/anc_policies')
def get_anc_policies():
    """A function to get the ANC policies from ISE"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("ISE_API_ADDRESS") or
        not os.getenv("ISE_API_USERNAME") or
        not os.getenv("ISE_API_PASSWORD")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    api_url = "https://{}:{}@{}:9060/ers/config/ancpolicy".format(os.getenv("ISE_API_USERNAME"),
                                                                  os.getenv("ISE_API_PASSWORD"),
                                                                  os.getenv("ISE_API_ADDRESS"))

    print("Fetching {}".format(api_url))

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Get ISE ANC Policies
    http_request = requests.get(api_url, headers=headers, verify=False)

    # Check to make sure the GET was successful
    if http_request.status_code == 200:
        return http_request.json()
    else:
        print('ISE Connection Failure - HTTP Return Code: {}\nResponse: {}'.format(http_request.status_code, http_request.text))
        exit()


@router.get('/anc_status/{mac_address}')
def get_anc_assignment(mac_address: str):
    """A function to look up the ISE ANC assignment for a given MAC address"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("ISE_API_ADDRESS") or
        not os.getenv("ISE_PXGRID_CLIENT_NAME")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    pxgrid = pxgrid_client.PxgridClient(os.getenv("ISE_API_ADDRESS"),
                                        os.getenv("ISE_PXGRID_CLIENT_NAME"),
                                        os.getenv("ISE_PXGRID_CERT_PATH"),
                                        os.getenv("ISE_PXGRID_KEY_PATH"))

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        raise HTTPException(status_code=403, detail="pxGrid account is currently not enabled.")

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.config.anc')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/getEndpointByMacAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, {"macAddress": mac_address})

    if pxgrid_response is not None:
        # Return a JSON formatted response
        return pxgrid_response
    else:
        # If ISE returns nothing, return a 204
        return Response(status_code=204)


@router.post('/anc_status')
def set_anc_assignment(anc_data: AncData):
    """A function to set the ISE ANC assignment for a given MAC address"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("ISE_API_ADDRESS") or
        not os.getenv("ISE_PXGRID_CLIENT_NAME")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    pxgrid = pxgrid_client.PxgridClient(os.getenv("ISE_API_ADDRESS"),
                                        os.getenv("ISE_PXGRID_CLIENT_NAME"),
                                        os.getenv("ISE_PXGRID_CERT_PATH"),
                                        os.getenv("ISE_PXGRID_KEY_PATH"))

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        raise HTTPException(status_code=403, detail="pxGrid account is currently not enabled.")

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.config.anc')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/applyEndpointByMacAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, anc_data.dict())

    if pxgrid_response is not None:
        # Return a JSON formatted response
        return pxgrid_response
    else:
        # If ISE returns nothing, return a 204
        return Response(status_code=204)


@router.delete('/anc_status/{mac_address}')
def clear_anc_assignment(mac_address: str):
    """A function to clear the ISE ANC assignment for a given MAC address"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("ISE_API_ADDRESS") or
        not os.getenv("ISE_PXGRID_CLIENT_NAME")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    pxgrid = pxgrid_client.PxgridClient(os.getenv("ISE_API_ADDRESS"),
                                        os.getenv("ISE_PXGRID_CLIENT_NAME"),
                                        os.getenv("ISE_PXGRID_CERT_PATH"),
                                        os.getenv("ISE_PXGRID_KEY_PATH"))

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        raise HTTPException(status_code=403, detail="pxGrid account is currently not enabled.")

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.config.anc')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/clearEndpointByMacAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, {"macAddress": mac_address})

    if pxgrid_response is not None:
        # Return a JSON formatted response
        return pxgrid_response
    else:
        # If ISE returns nothing, return a 204
        return Response(status_code=204)


@router.get('/session_data/{ip_address}')
def get_session_data(ip_address: str):
    """A function to look up the ISE session data for a given IP"""

    # Return HTTP 204 if not configured
    if (
        not os.getenv("ISE_API_ADDRESS") or
        not os.getenv("ISE_PXGRID_CLIENT_NAME")
    ):
        raise HTTPException(status_code=501, detail="Module not configured")

    pxgrid = pxgrid_client.PxgridClient(os.getenv("ISE_API_ADDRESS"),
                                        os.getenv("ISE_PXGRID_CLIENT_NAME"),
                                        os.getenv("ISE_PXGRID_CERT_PATH"),
                                        os.getenv("ISE_PXGRID_KEY_PATH"))

    # Check to see if the account is enabled
    if pxgrid.account_activate()['accountState'] != 'ENABLED':
        print("pxGrid Account is not enabled.")
        raise HTTPException(status_code=403, detail="pxGrid account is currently not enabled.")

    # Lookup the session service
    service_lookup_response = pxgrid.service_lookup('com.cisco.ise.session')

    # Store the session service
    session_service = service_lookup_response['services'][0]

    # Build the URL to get session details
    url = session_service['properties']['restBaseUrl'] + '/getSessionByIpAddress'

    # Run the session query
    pxgrid_response = pxgrid.send_rest_request(url, {"ipAddress": ip_address})

    if pxgrid_response is not None:
        # Return a JSON formatted response
        return pxgrid_response
    else:
        # If ISE returns nothing, return a 204
        return Response(status_code=204)
