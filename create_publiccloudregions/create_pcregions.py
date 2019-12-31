#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Create PCRs
# ============
# Environment: With access to internet

# Requires:
# * Remote services registered in Abiquo

# Steps
# * Get files with region providerID and friendly name
# *  Expects CSV files with first two items
# * Get existing remote services (or IP of remote services)
# * List Abiquo regions per provider hypervisor type, get endpoint, etc
# * Create regions

#
#
import copy
import json
from abiquo.client import Abiquo
# from abiquo.client import check_response
import sys
import csv
import re

# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Abbreviate region names
COMPASSPOINTS = {"north": "n",
                 "east": "e",
                 "south": "s",
                 "west": "w",
                 "central": "c"}
LOCALDOMAINAPI = ".bcn.abiquo.com/api"
PROVIDERSLIST = ["AMAZON", "azurecompute-arm"]
PCRREMOTESERVICES = ["NARS", "VIRTUALSYSTEMMONITOR",
                     "VIRTUALFACTORY", "REMOTEACCESS"]
REMOTESERVICESID = "mjsabiquo"
FRIENDLYNAMESUBS = {"Canada (Central)": "Canada",
                    "AWS GovCloud \(.*?\)": "GovCloud $1"}


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

    # Get the links of the remote services for the post request
    code, remoteServicesList = api.admin.remoteservices.get(
        headers={'Accept': 'application/vnd.abiquo.remoteservices+json'},
        params={'has': REMOTESERVICESID})
    print("Get remote services. Response code is: ", code)

    pCRBaseLinks = []
    for remoteService in remoteServicesList:
        # Get the links for public cloud remote services
        rsLinks = list(filter(lambda link:
                       link["title"] in PCRREMOTESERVICES,
                       remoteService.json["links"]))
        for rsLink in rsLinks:
            print("rsLink: ", json.dumps(rsLink, indent=2))
            rsPostLink = copy.deepcopy(rsLink)
            rsPostLink["rel"] = "remoteservice"
            pCRBaseLinks.append(rsPostLink)

    # Create a dictionary with providerId and friendlyName from user file
    regsToCreate = {}
    for providerCode in PROVIDERSLIST:
        provider_file = providerCode.lower() + "_regions.csv"
        with open(provider_file) as providerregionsfile:
            header_row = 0
            regionslist = csv.reader(providerregionsfile, delimiter=",")
            for row in regionslist:
                # Discard the first row because it is a header
                if header_row == 0:
                    header_row = 1
                    continue
                providerId = row[0]
                friendlyName = row[1]

                # Do some initial substituations from exception list above
                for friendlyNameSub, friendlyNameRep in FRIENDLYNAMESUBS.items():
                    friendlyName = re.sub(
                        friendlyNameSub,
                        friendlyNameRep,
                        friendlyName)

                # Get rid of text outside brackets and brackets themselves
                # This is for AWS
                if "(" in friendlyName:
                    friendlyName = re.sub(".*?\(", "", friendlyName)
                    friendlyName = re.sub("\).*?", "", friendlyName)

                # print("providerId: ", providerId,
                #      " friendlyName: ", friendlyName)
                regsToCreate[providerId] = friendlyName
    for pr, fna in regsToCreate.items():
        print("pr: ", pr, " fn: ", fna)

    # Get regions for provider type
    code, hypervisorTypes = api.config.hypervisortypes.get(
        headers={'Accept': 'application/vnd.abiquo.hypervisortypes+json'})
    print("Get hypervisortypes, response code: ", code)

    for provider in PROVIDERSLIST:
        for providerHT in hypervisorTypes:
            if provider in providerHT.name:
                code, providerRegions = providerHT.follow('regions').get(
                    headers={'Accept': 'application/vnd.abiquo.regions+json'})
                # Filter provider regions by region list from input files

                selRegs = list(filter(lambda regi:
                                      regi.json["providerId"] in regsToCreate,
                                      providerRegions))

                for reg in selRegs:
                    print("REGION REGION REGION REGION -----: ", reg.name)
                    print("Region provider ID: ", reg.providerId)

                    # Get self link of region to use for post request
                    regionSelfLinks = list(filter(
                        lambda link: link["rel"] == "self", reg.json["links"]))
                    regionSelfLink = regionSelfLinks[0]
                    print("Region self link: ",
                          json.dumps(regionSelfLink, indent=2))

                    # Make a mini link to use in post request
                    regionPostLink = {"rel": "region",
                                      "href": regionSelfLink["href"]}
                    pcrName = regsToCreate[reg.providerId] + \
                        " (" + providerId + ")"
                    pubCloudRegion = {"provider": provider,
                                      "name": pcrName}
                    pubCloudRegion["links"] = pCRBaseLinks[:]
                    pubCloudRegion["links"].append(regionPostLink)

                    # Create a public cloud region
                    code, createdpcr = api.admin.publiccloudregions.post(
                        headers={'accept': 'application/vnd.abiquo.publiccloudregion+json',
                                 'content-type': 'application/vnd.abiquo.publiccloudregion+json'},
                        data=json.dumps(pubCloudRegion))
                    print("Create public cloud region: ", reg.providerId,
                          ", Response code: ", code)


# Calls the main() function
if __name__ == '__main__':
    main()
