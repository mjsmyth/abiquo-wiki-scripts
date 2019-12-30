#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Create PCRs
# ============
# Environment: With access to internet

# Requires:
# * Remote services registered in Abiquo

# Steps
# * Get file with list of regions, plus friendly names or AWS names
# * Get existing remote services (or IP of remote services)
# * List Abiquo regions per provider hypervisor type, get endpoint, etc
# * Create regions

#
#
import copy
import json
from abiquo.client import Abiquo
from abiquo.client import check_response
import sys
import csv
import re

# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Abbreviate region names
COMPASSPOINTS = {"north": "n", "east": "e", "south": "s", "west": "w", "central": "c"}
LOCALDOMAINAPI = ".bcn.abiquo.com/api"
PROVIDERSLIST = {"AMAZON", "azurecompute-ARM"}


def main():
    # For test env, pass in the IP of local system, username and password
    localsystem = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    API_URL = "https://" + localsystem + LOCALDOMAINAPI
    api = Abiquo(API_URL, auth=(username, password), verify=False)
    # Another option:
    #   API_URL = input("Enter Abiquo API URL,
    #    e.g 'https://abq.example.abiquo.com/api': ")
    #   username = input("Username: ")
    #   password = input("Password: ")
    # Assuming test environment with self-signed certificate
    #   api = Abiquo(API_URL, auth=(username, password), verify=False)

    # Create a dictionary with providerId and friendlyName from user file
    providersToCreate = {}
    with open("amazon_regions.csv") as providerregionsfile:
        regionslist = csv.reader(providerregionsfile, delimiter=",")
        # Discard the first row because it is a header
        for row in regionslist:
            if "Code" in row[0]:
                continue
            providerId = row[0]
            # assuming only one set of brackets in friendly name
            friendlyName = re.findall("\((.*?)\)", row[1])[0]
            if "Central" in friendlyName:
                friendlyName = "Canada"
            print("providerId: ", providerId, " friendlyName: ", friendlyName)
            providersToCreate[providerId] = friendlyName
    for pr, fna in providersToCreate.items():
        print("pr: ", pr, " fn: ", fna)

    # Get regions for provider type
    code, hypervisorTypes = api.config.hypervisortypes.get(
        headers={'Accept': 'application/vnd.abiquo.hypervisortypes+json'})
    print("Get hypervisortypes, response code: ", code)

    for providerHT in hypervisorTypes:
        for provider in PROVIDERSLIST:
            if provider in providerHT.name:
                code, providerRegions = providerHT.follow('regions').get(
                    headers={'Accept': 'application/vnd.abiquo.regions+json'})
                for reg in providerRegions:
                    print("region: ", reg.endpoint)




# Calls the main() function
if __name__ == '__main__':
    main()
