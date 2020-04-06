#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is an API client for Cisco AMP for Endpoints.

amp_client.py
----------------
Author: Alan Nix
Property of: Cisco Systems
"""

import json

import requests

from requests.auth import HTTPBasicAuth


class AmpClient(object):
    """This is an API client for Cisco AMP for Endpoints."""

    __sdk_version = "0.1"

    __amp_fqdn = None
    __amp_client_id = None
    __amp_api_key = None

    __debug = False

    def __init__(self, fqdn="api.amp.cisco.com", client_id=None, api_key=None, debug=False):
        """Initializes the AmpClient object."""

        self.__amp_fqdn = fqdn
        self.__amp_client_id = client_id
        self.__amp_api_key = api_key

        self.__debug = debug

    def get_computers(self, internal_ip=None, external_ip=None, group_guids=[], hostnames=[]):
        """Get AMP Computers matching the specified criteria."""

        # Build the Computers URL
        url = "https://{}/v1/computers?".format(self.__amp_fqdn)

        if internal_ip:
            url += "&internal_ip={}".format(internal_ip)

        if external_ip:
            url += "&external_ip={}".format(external_ip)

        for group_guid in group_guids:
            url += "&group_guid[]={}".format(group_guid)

        for hostname in hostnames:
            url += "&hostname[]={}".format(hostname)

        # Get the Computer data
        response = self._get_paginated_data(url)

        return response

    def patch_computer(self, connector_guid=None, data=None):
        """Patch AMP Computer with the specified GUID and payload."""

        # Build the Computers URL
        url = "https://{}/v1/computers/{}".format(self.__amp_fqdn, connector_guid)

        response = self._patch_request(url, data)

        return response

    def get_events(self, detection_sha256=None, application_sha256=None,
                   connector_guid=[], group_guid=[], start_date=None, event_type=[]):
        """Get AMP Events matching the specified criteria."""

        # Build the Events URL
        url = "https://{}/v1/events?".format(self.__amp_fqdn)

        if detection_sha256:
            url += "&detection_sha256={}".format(detection_sha256)

        if application_sha256:
            url += "&application_sha256={}".format(application_sha256)

        for guid in connector_guid:
            url += "&event_type[]={}".format(guid)

        for guid in group_guid:
            url += "&group_guid[]={}".format(guid)

        if start_date:
            url += "&start_date={}".format(start_date)

        for type_id in event_type:
            url += "&event_type[]={}".format(type_id)

        # Get the Event data
        response = self._get_paginated_data(url)

        return response

    def get_event_types(self):
        """Get the AMP Event Types."""

        # Build the Event Types URL
        url = "https://{}/v1/event_types".format(self.__amp_fqdn)

        # Get the Event Types data
        response = self._get_request(url)

        return response

    def get_file_lists_application_blocking(self, names=[]):
        """Get the Application Blocking File Lists from AMP."""

        # Build the Application Blocking File Lists URL
        url = "https://{}/v1/file_lists/application_blocking".format(self.__amp_fqdn)

        for name in names:
            url += "&name[]={}".format(name)

        response = self._get_paginated_data(url)

        return response

    def get_group(self, guid=None):
        """Get a specific AMP Group."""

        if guid:
            # Build the Groups URL
            url = "https://{}/v1/groups/{}?".format(self.__amp_fqdn, guid)

            # Get the Group data
            response = self._get_request(url)

            return response

        else:
            print("No Group GUID was provided.")
            return None

    def get_groups(self, name=None):
        """Get all AMP Groups with an optional 'name' filter."""

        # Build the Groups URL
        url = "https://{}/v1/groups?".format(self.__amp_fqdn)

        # Optionally, filter on name
        if name:
            url += "&name={}".format(name)

        # Get all of the paginated Group data
        response = self._get_paginated_data(url)

        return response

    def get_isolation(self, guid=None):
        """Get the isolation status for the specified GUID."""

        if guid:
            # Build the Isolation status URL
            url = "https://{}/v1/computers/{}/isolation?".format(self.__amp_fqdn, guid)

            # Get the Isolation data
            response = self._get_request(url)

            return response

        else:
            print("No Connector GUID was provided.")
            return None

    def delete_isolation(self, guid=None, data=None):
        """Delete the isolation status for the specified GUID."""

        if guid:
            # Build the Isolation status URL
            url = "https://{}/v1/computers/{}/isolation?".format(self.__amp_fqdn, guid)

            if data:
                # Delete the Isolation data
                response = self._delete_request(url, data)
            else:
                response = self._delete_request(url)

            return response

        else:
            print("No Connector GUID was provided.")
            return None

    def options_isolation(self, guid=None):
        """Get the isolation options that are available for the specified GUID."""

        if guid:
            # Build the Isolation options URL
            url = "https://{}/v1/computers/{}/isolation?".format(self.__amp_fqdn, guid)

            # Get the Isolation data
            response = self._options_request(url)

            return response

        else:
            print("No Connector GUID was provided.")
            return None

    def put_isolation(self, guid=None, data=None):
        """Put an isolation request for the specified GUID."""

        if guid:
            # Build the Isolation options URL
            url = "https://{}/v1/computers/{}/isolation?".format(self.__amp_fqdn, guid)

            # Get the Isolation data
            response = self._put_request(url, data)

            return response

        else:
            print("No Connector GUID was provided.")
            return None

    def get_policy(self, guid=None):
        """Get a specific AMP Policy."""

        if guid:
            # Build the Policies URL
            url = "https://{}/v1/policies/{}?".format(self.__amp_fqdn, guid)

            # Get the Policy data
            response = self._get_request(url)

            return response

        else:
            print("No Policy GUID was provided.")
            return None

    def get_policies(self, name=None, product=None):
        """Get all AMP Policies with optional 'name' and 'product' filters."""

        # Build the Policies URL
        url = "https://{}/v1/policies?".format(self.__amp_fqdn)

        # Optionally, filter on name
        if name:
            url += "&name={}".format(name)

        # Optionally, filter on product
        if product:
            url += "&product={}".format(product)

        # Get all of the paginated Policy data
        response = self._get_paginated_data(url)

        return response

    def get_version(self):
        """Get the version of the AMP API."""

        # Build the Version URL
        url = "https://{}/v1/version".format(self.__amp_fqdn)

        # Get the Version data
        response = self._get_request(url)

        return response

    def get_vulnerabilities(self, start_time=None, end_time=None, group_guid=[], sha256=None):
        """Get Vulnerabilities that have been detected by AMP."""

        # Build the Vulnerabilities URL
        if sha256:
            url = "https://{}/v1/vulnerabilities/{}/computers?".format(self.__amp_fqdn, sha256)
        else:
            url = "https://{}/v1/vulnerabilities?".format(self.__amp_fqdn)

        if start_time:
            url += "&start_time={}".format(start_time)

        if end_time:
            url += "&end_time={}".format(end_time)

        for guid in group_guid:
            url += "&group_guid[]={}".format(guid)

        # Get the Vulnerabilties data
        response = self._get_paginated_data(url)

        return response

    def _get_paginated_data(self, url=None, limit=10, offset=0):
        """Performs an HTTP GET request that returns all paginated data."""

        # A placeholder for looping
        returned_results = limit

        # A placeholder for return data
        return_data = []

        # Loop through requests
        while returned_results == limit:

            # Build the API URL
            paginated_url = url + "&limit={}&offset={}".format(limit, offset)

            # Send the GET request
            response = self._get_request(paginated_url)

            # Append all data to the return data
            for item in response["data"]:
                return_data.append(item)

            # Update the number of returned results
            returned_results = response['metadata']['results']['current_item_count']

            # Increment the offset
            offset += limit

        return return_data

    def _delete_request(self, url=None, data=None):
        """Performs an HTTP DELETE request."""

        if self.__debug:
            print("Delete URL: {}".format(url))

        # Perform the DELETE request
        response = requests.delete(url, data=data, auth=HTTPBasicAuth(self.__amp_client_id, self.__amp_api_key))

        # Check to see if the DELETE was successful
        if response.status_code >= 200 and response.status_code < 300:

            if self.__debug:
                print("AMP Returned Result: {}\n".format(json.dumps(response.json(), indent=4)))

            # Return the JSON formatted response
            return response.json()

        else:
            print("AMP Connection Failure.\nHTTP Return Code: {}\nResponse: {}".format(response.status_code,
                                                                                       response.text))
            return None

    def _get_request(self, url=None):
        """Performs an HTTP GET request."""

        if self.__debug:
            print("Get URL: {}".format(url))

        # Perform the GET request
        response = requests.get(url, auth=HTTPBasicAuth(self.__amp_client_id, self.__amp_api_key))

        # Check to see if the GET was successful
        if response.status_code >= 200 and response.status_code < 300:

            if self.__debug:
                print("AMP Returned Result: {}\n".format(json.dumps(response.json(), indent=4)))

            # Return the JSON formatted response
            return response.json()

        else:
            print("AMP Connection Failure.\nHTTP Return Code: {}\nResponse: {}".format(response.status_code,
                                                                                       response.text))
            return None

    def _options_request(self, url=None):
        """Performs an HTTP OPTIONS request."""

        if self.__debug:
            print("Option URL: {}".format(url))

        # Perform the OPTIONS request
        response = requests.options(url, auth=HTTPBasicAuth(self.__amp_client_id, self.__amp_api_key))

        # Check to see if the OPTIONS was successful
        if response.status_code >= 200 and response.status_code < 300:

            if self.__debug:
                print("AMP Returned Result: {}\n".format(json.dumps(response.json(), indent=4)))

            # Return the JSON formatted response
            return response.json()
        else:
            print("AMP Connection Failure.\nHTTP Return Code: {}\nHeaders:{}\nResponse: {}".format(response.status_code,
                                                                                                   response.headers,
                                                                                                   response.text))
            return None

    def _patch_request(self, url=None, data=None):
        """Performs an HTTP PATCH request."""

        if self.__debug:
            print("Patch URL: {}".format(url))

        # Perform the PATCH request
        response = requests.patch(url, data, auth=HTTPBasicAuth(self.__amp_client_id, self.__amp_api_key))

        # Check to see if the PATCH was successful
        if response.status_code >= 200 and response.status_code < 300:

            if self.__debug:
                print("AMP Returned Result: {}\n".format(json.dumps(response.json(), indent=4)))

            # Return the JSON formatted response
            return response.json()

        else:
            print("AMP Connection Failure.\nHTTP Return Code: {}\nResponse: {}".format(response.status_code,
                                                                                       response.text))
            exit()

    def _put_request(self, url=None, data=None):
        """Performs an HTTP PUT request."""

        if self.__debug:
            print("Put URL: {}".format(url))

        # Perform the PUT request
        response = requests.put(url, data, auth=HTTPBasicAuth(self.__amp_client_id, self.__amp_api_key))

        # Check to see if the PUT was successful
        if response.status_code >= 200 and response.status_code < 300:

            if self.__debug:
                print("AMP Returned Result: {}\n".format(json.dumps(response.json(), indent=4)))

            # Return the JSON formatted response
            return response.json()

        else:
            print("AMP Connection Failure.\nHTTP Return Code: {}\nResponse: {}".format(response.status_code,
                                                                                       response.text))
            return None
