#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Create PCRs
# ============
# Environment: With access to internet
#
# Requires:
# * Remote services registered in Abiquo
# * Can specify remote services by IP in this file
# * Configure local domain in this file
#
# Arguments (separated by spaces):
# * name of local system
# * Abiquo username
# * Abiquo password
#
# Optional arguments (for false send nonvalues as placeholders):
# * ALL - create all regions from Abiquo
# * USECSV - if present, use name from CSV file
# * SUBL - if present, use substitution list as defined in this file
# * INPA - if parenthesis, use only text in parenthesis (e.g N. Virginia)
#
# Steps:
# * Get existing remote services (match IP of remote services)
#
# * Get provider region files
# *  Expects 1 x CSV file for each provider with first two columns:
# * 1. providerId, 2. friendlyName
#
#
#
#
import copy
import json
from abiquo.client import Abiquo
# from abiquo.client import check_response
# import sys
import csv
import re
import argparse

# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOCALDOMAINAPI = ".bcn.abiquo.com/api"
PROVIDERCODES = {"AMAZON": "AWS", "azurecompute-arm": "AZ"}
PROVIDERSLIST = ["AMAZON", "azurecompute-arm"]
PCRREMOTESERVICES = ["NARS", "VIRTUALSYSTEMMONITOR",
                     "VIRTUALFACTORY", "REMOTEACCESS"]
REMOTESERVICESID = "mjsabiquo"

# Use this on the names
FRIENDLYNAMESUBS = {"Canada (Central)": "Canada",
                    "AWS GovCloud \((.*?)\)": "GovCloud \g<1>"}


def SubList(friendlyName):
    # Do some initial substituations from exception list above
    for friendlyNameSub, friendlyNameRep in FRIENDLYNAMESUBS.items():
        friendlyName = re.sub(
            friendlyNameSub,
            friendlyNameRep,
            friendlyName)
    return friendlyName


def TextInPar(friendlyName):
    # Get rid of text outside brackets and brackets themselves
    # This is for AWS
    if "(" in friendlyName:
        friendlyName = re.sub(".*?\(", "", friendlyName)
        friendlyName = re.sub("\).*?", "", friendlyName)
    return friendlyName


def main():
    parser = argparse.ArgumentParser(description='Create PCRs!')
    parser.add_argument("--s", default="mjsabiquo",
                        type=str, help="Local system")
    parser.add_argument("--u", default="admin",
                        type=str, help="Username")
    parser.add_argument("--p", default="xabiquo",
                        type=str, help="Password")
    parser.add_argument("--a", action="store_true",
                        help="Create all regions not just those in CSVs")
    parser.add_argument("--c", action="store_true",
                        help="Use names from CSV files")
    parser.add_argument("--r", action="store_false",
                        help="Don't replace text strings from script")
    parser.add_argument("--b", action="store_false",
                        help="Use AWS full name, not just text in parenthesis")

    args = parser.parse_args()
    localsystem = args.s
    username = args.u
    password = args.p
    createAll = args.a
    useCsvNames = args.c
    subList = args.r
    removeParenthesis = args.b

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
    print("REMOTE SERVICES ---")
    for remoteService in remoteServicesList:
        # Get the links for public cloud remote services
        rsLinks = list(filter(lambda link:
                       link["title"] in PCRREMOTESERVICES,
                       remoteService.json["links"]))

        for rsLink in rsLinks:
            print("Remote Service: ", rsLink["title"])
            # print("rsLink: ", json.dumps(rsLink, indent=2))
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
                csvName = row[1]
                # print("providerId: ", providerId,
                #      " friendlyName: ", friendlyName)
                regsToCreate[providerId] = csvName[:]
    print("REGIONS IN CSV FILES ---:")
    for pcr, fna in regsToCreate.items():
        print("region: ", pcr, "\tcsvname: ", fna)

    # Get regions for provider type
    code, hypervisorTypes = api.config.hypervisortypes.get(
        headers={'Accept': 'application/vnd.abiquo.hypervisortypes+json'})
    print("Get hypervisortypes, response code: ", code)

    for provider in PROVIDERSLIST:
        print("-------------------------------------")
        print("PROVIDER: ", provider)
        print("-------------------------------------")
        for providerHT in hypervisorTypes:
            if provider in providerHT.name:
                code, providerRegions = providerHT.follow('regions').get(
                    headers={'Accept': 'application/vnd.abiquo.regions+json'})

                if createAll is True:
                    selRegs = providerRegions
                else:
                    # Filter provider regions by region list from input files
                    selRegs = list(
                        filter(
                            lambda regi:
                                regi.json["providerId"] in regsToCreate,
                                providerRegions))

                for sreg in selRegs:
                    print("REGION -----: ", sreg.name)
                    print("\tProvider ID: ", sreg.providerId)

                    # Get self link of region to use for post request
                    regionSelfLinks = list(filter(
                        lambda link: link["rel"] == "self",
                        sreg.json["links"]))
                    regionSelfLink = regionSelfLinks[0]
                    # print("Region self link: ",
                    #      json.dumps(regionSelfLink, indent=2))

                    # Make a mini link to use in post request
                    regionPostLink = {"rel": "region",
                                      "href": regionSelfLink["href"]}
                    # Create friendly name with Abiquo name
                    pcrBaseName = sreg.name[:]
                    if useCsvNames is True:
                        if sreg.providerId in regsToCreate:
                            pcrBaseName = regsToCreate[sreg.providerId][:]

                    if subList is True:
                        pcrBaseName = SubList(pcrBaseName)
                    if removeParenthesis is True:
                        pcrBaseName = TextInPar(pcrBaseName)

                    pcrName = pcrBaseName + " (" + sreg.providerId + ")"

                    print("\tAbiquo name: ", pcrName)
                    pubCloudRegion = {"provider": provider,
                                      "name": pcrName}
                    pubCloudRegion["links"] = pCRBaseLinks[:]
                    pubCloudRegion["links"].append(regionPostLink)

                    # Create a public cloud region
                    code, createdpcr = api.admin.publiccloudregions.post(
                        headers={'accept': 'application/vnd.abiquo.publiccloudregion+json',
                                 'content-type': 'application/vnd.abiquo.publiccloudregion+json'},
                        data=json.dumps(pubCloudRegion))
                    print("\tCREATE REGION: ", sreg.providerId,
                          ", Response code: ", code)


# Calls the main() function
if __name__ == '__main__':
    main()
