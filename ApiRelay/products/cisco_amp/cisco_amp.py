#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Python module to extend the API Relay for Cisco's AMP for Endpoints
"""

import os

import requests
import modules.cisco_amp.amp_client as amp_client

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

class AmpGroup(BaseModel):
    group_guid: str

class AmpIsolation(BaseModel):
    comment: str = None
    unlock_code: str = None

router = APIRouter()

# AMP Functions
@router.get('/computer/{ip_address}')
def get_computer(ip_address: str):
    """A function to retrieve AMP computer data and return it as JSON"""

    # Return HTTP 501 if not configured
    if not os.getenv("AMP_API_CLIENT_ID") or not os.getenv("AMP_API_KEY"):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Create an AMP API Client
    client = amp_client.AmpClient(client_id=os.getenv("AMP_API_CLIENT_ID"),
                                  api_key=os.getenv("AMP_API_KEY"))

    # Get the computers that have been at the internal IP
    response = client.get_computers(internal_ip=ip_address)

    if response:
        # Return a JSON formatted response
        return response
    else:
        # If AMP returns nothing, return a 204
        return Response(status_code=204)


@router.get('/groups')
def get_groups():
    """A function to get all groups from AMP"""

    # Return HTTP 501 if not configured
    if not os.getenv("AMP_API_CLIENT_ID") or not os.getenv("AMP_API_KEY"):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Create an AMP API Client
    client = amp_client.AmpClient(client_id=os.getenv("AMP_API_CLIENT_ID"),
                                  api_key=os.getenv("AMP_API_KEY"))

    # Get the groups that exist in AMP
    response = client.get_groups()

    if response:
        # Return a JSON formatted response
        return response
    else:
        # If AMP returns nothing, return a 204
        return Response(status_code=204)


@router.post('/computer/{connector_guid}/group')
def set_computer_group(connector_guid: str, group_data: AmpGroup):
    """A function to set the Group for a specific AMP computer"""

    # Return HTTP 501 if not configured
    if not os.getenv("AMP_API_CLIENT_ID") or not os.getenv("AMP_API_KEY"):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Create an AMP API Client
    client = amp_client.AmpClient(client_id=os.getenv("AMP_API_CLIENT_ID"),
                                  api_key=os.getenv("AMP_API_KEY"))

    # Patch the computer to change the group
    response = client.patch_computer(connector_guid=connector_guid, data=group_data.dict())

    if response:
        # Return a JSON formatted response
        return response
    else:
        # If AMP returns nothing, return a 204
        return Response(status_code=204)


@router.get('/computer/{connector_guid}/isolation')
def get_computer_isolation(connector_guid: str):
    """A function to get the AMP isolation status of a computer"""

    # Return HTTP 501 if not configured
    if not os.getenv("AMP_API_CLIENT_ID") or not os.getenv("AMP_API_KEY"):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Create an AMP API Client
    client = amp_client.AmpClient(client_id=os.getenv("AMP_API_CLIENT_ID"),
                                  api_key=os.getenv("AMP_API_KEY"))

    # Get the AMP Isolation status
    response = client.get_isolation(guid=connector_guid)

    if response:
        # Return a JSON formatted response
        return response
    else:
        # If AMP returns nothing, return a 204
        return Response(status_code=204)


@router.put('/computer/{connector_guid}/isolation')
def put_computer_isolation(connector_guid: str, isolation_data: AmpIsolation):
    """A function to put the AMP isolation status of a computer"""

    # Return HTTP 501 if not configured
    if not os.getenv("AMP_API_CLIENT_ID") or not os.getenv("AMP_API_KEY"):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Create an AMP API Client
    client = amp_client.AmpClient(client_id=os.getenv("AMP_API_CLIENT_ID"),
                                  api_key=os.getenv("AMP_API_KEY"))

    # Put the AMP Isolation status
    response = client.put_isolation(guid=connector_guid, data=isolation_data.dict())

    if response:
        # Return a JSON formatted response
        return response
    else:
        # If AMP returns nothing, return a 204
        return Response(status_code=204)


@router.delete('/computer/{connector_guid}/isolation')
def delete_computer_isolation(connector_guid: str, isolation_data: AmpIsolation):
    """A function to delete the AMP isolation status of a computer"""

    # Return HTTP 501 if not configured
    if not os.getenv("AMP_API_CLIENT_ID") or not os.getenv("AMP_API_KEY"):
        raise HTTPException(status_code=501, detail="Module not configured")

    # Create an AMP API Client
    client = amp_client.AmpClient(client_id=os.getenv("AMP_API_CLIENT_ID"),
                                  api_key=os.getenv("AMP_API_KEY"))

    # Delete the AMP Isolation status
    response = client.delete_isolation(guid=connector_guid, data=isolation_data.dict())

    if response:
        # Return a JSON formatted response
        return response
    else:
        # If AMP returns nothing, return a 204
        return Response(status_code=204)
