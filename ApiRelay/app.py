#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Python script to run Cisco Command Center's API backend.

This script runs a FastAPI web server which handles the API (/api) requests for
event data, and interactions with security products.
"""

import os
import pprint
import uvicorn

import config

from fastapi import FastAPI
from products.cisco_amp import cisco_amp
from products.cisco_ise import cisco_ise
from products.cisco_stealthwatch import cisco_stealthwatch
from products.command_center import command_center

# Instantiate FastAPI
app = FastAPI(
    title="Command Center API Relay",
    version="0.1"
)
app.include_router(cisco_amp.router, prefix="/amp", tags=["Cisco AMP"])
app.include_router(cisco_ise.router, prefix="/ise", tags=["Cisco ISE"])
app.include_router(cisco_stealthwatch.router, prefix="/stealthwatch", tags=["Cisco Stealthwatch"])
app.include_router(command_center.router, prefix="/command-center", tags=["Command Center"])

# Sanity check route
@app.get('/ping')
async def ping_pong():
    """A simple sanity check route."""

    return {'pong!'}


def _get_config_mongodb():
    """This will get configuration data from a MongoDB instance."""

    raise NotImplementedError

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
