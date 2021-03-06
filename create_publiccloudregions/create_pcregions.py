#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Create PCRs
# ============
# Environment: With access to internet
#
# Dependencies:
# abiquo-api installed with pip3
#
# Example:
# python3 create_pcregions.py --s https://abq.bcn.abiquo.com/api --u cloudadmin --p cloudadmin --a --e china --d --v rs.bcn.abiquo.com
#
# Requires:
# * Remote services registered in Abiquo
# * Can specify remote services by IP with option
#
# Constants:
# - Provider list
# - Provider code list
# - PCR remote services list
# - Text substitution strings
#
# Arguments (separated by spaces):
# * --a - URL of the Abiquo API
# * --u - Abiquo username
# * --p - Abiquo password
#
# Optional arguments:
# * --a - if present, create all regions from Abiquo (otherwise from CSV file)
# * --c - if present, use name from CSV file
# * --r - if present, use substitution list as defined in this file
# * --b - if parenthesis, use only text in parenthesis (e.g N. Virginia)
# * --e - if present, use exception string (eg "china" not case sensitive)
# * --d - if present, add a provider code as defined in this file
# * --v - if present, use this IP for remote services, or use API IP
#
#
# Files:
# * To use region names from CSV files or create only regions in the CSVs
# * you MUST create 1 x CSV file for each provider with file name -
# * {provider}_regions.csv: amazon_regions.csv, azurecompute-arm_regions.csv
# *
# * 1 x Header line and mandatory columns: 1. Provider ID, 2. Friendly Name
# * Example CSV file:
# ** Code, Name
# ** "uaenorth","UAE North"
# **
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


PROVIDERCODES = {"AMAZON": "AWS ", "azurecompute-arm": "Azure "}
PROVIDERSLIST = ["AMAZON", "azurecompute-arm"]
PCRREMOTESERVICES = ["NARS", "VIRTUALSYSTEMMONITOR",
                     "VIRTUALFACTORY", "REMOTEACCESS"]
# Use this on the names
FRIENDLYNAMESUBS = {"Canada \(Central\)": "Canada Central",
                    "AWS GovCloud \((.*?)\)": "AWS GovCloud \g<1>",
                    "uaenorth": "UAE North"}


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
    parser.add_argument("--s",
                        type=str, help="URL of Abiquo API")
    parser.add_argument("--u", default="admin",
                        type=str, help="Username, default admin")
    parser.add_argument("--p", default="xabiquo",
                        type=str, help="Password, default xabiquo")
    parser.add_argument("--a", action="store_true",
                        help="Create all regions not just those in CSVs")
    parser.add_argument("--c", action="store_true",
                        help="Use region names from CSV files, or Abiquo")
    parser.add_argument("--r", action="store_false",
                        help="Don't replace text strings from script")
    parser.add_argument("--b", action="store_false",
                        help="Use AWS full name, not just text in parenthesis")
    parser.add_argument("--e", type=str,
                        help="Don't create excepted regions, default china")
    parser.add_argument("--d", action="store_true",
                        help="Use a provider code in name as defined")
    parser.add_argument("--v", type=str,
                        help="IP of Remote Services, or use API IP")

    args = parser.parse_args()
    apiUrl = args.s
    username = args.u
    password = args.p
    createAll = args.a
    useCsvNames = args.c
    subList = args.r
    removeParenthesis = args.b
    dontCreateExcepted = args.e
    useProviderCode = args.d
    remoteServicesIp = args.v

    api = Abiquo(apiUrl, auth=(username, password), verify=False)

    # Get the links of the remote services for the post request
    code, remoteServicesList = api.admin.remoteservices.get(
        headers={'Accept': 'application/vnd.abiquo.remoteservices+json'})
    print("Get remote services. Response code is: ", code)
    # Assuming not more than a page of remote services

    rsFromRsIpList = []
    pCRBaseLinks = []
    print("REMOTE SERVICES ---")

    for remoteService in remoteServicesList:
        # Check that the URI of the RS has the api ip or supplied IP
        if not remoteServicesIp:
            rsIpAPI = apiUrl[:]
            remoteServicesIpList = re.findall(r'https://(.*?)/api', rsIpAPI)
            rsIpInput = remoteServicesIpList.pop()
        else:
            rsIpInput = remoteServicesIp
        # print("remoteServicesIp: ", rsIpInput)
        if rsIpInput in remoteService.json["uri"]:
            print("rsIpInput: ", remoteService.json["uri"])
            rsFromRsIpList.append(remoteService)

    rsAllLinks = []
    for remoteServiceFromIp in rsFromRsIpList:
        # Get only the links for public cloud remote services
        for rsl in remoteServiceFromIp.json["links"]:
            if rsl["title"] in PCRREMOTESERVICES:
                rsAllLinks.append(rsl)

    for rsLink in rsAllLinks:
        # Create links to remote services for PCR object
        print("Remote Service: ", rsLink["title"])
        rsPostLink = copy.deepcopy(rsLink)
        rsPostLink["rel"] = "remoteservice"
        pCRBaseLinks.append(rsPostLink)

    # Create a dictionary with providerId and friendlyName from user file
    # if user file is required (use CSV names and/or don't create All)
    regsToCreate = {}
    if (useCsvNames is True or createAll is False):
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
                    # print("\tProvider ID:\t", sreg.providerId)

                    if dontCreateExcepted:
                        if (dontCreateExcepted in sreg.name.lower() or
                                dontCreateExcepted in sreg.providerId.lower()):
                            print("------------------------------------------")
                            print("Excepted region not created: Name is",
                                  sreg.name,
                                  "and ProviderId is: ", sreg.providerId)
                            print("------------------------------------------")
                            continue
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

                    pcrNameNoProv = pcrBaseName + " (" + sreg.providerId + ")"

                    if useProviderCode is True:
                        pcrName = PROVIDERCODES[provider] + pcrNameNoProv
                    else:
                        pcrName = pcrNameNoProv[:]

                    print("\tAbiquo name:\t", pcrName)
                    pubCloudRegion = {"provider": provider,
                                      "name": pcrName}
                    pubCloudRegion["links"] = pCRBaseLinks[:]
                    pubCloudRegion["links"].append(regionPostLink)

                    # print("PCR: ", json.dumps(pubCloudRegion, indent=2))

                    # Create a public cloud region
                    code, createdpcr = api.admin.publiccloudregions.post(
                        headers={'accept': 'application/vnd.abiquo.publiccloudregion+json',
                                 'content-type': 'application/vnd.abiquo.publiccloudregion+json'},
                        data=json.dumps(pubCloudRegion))
                    print("\tCREATE REGION:\t", sreg.providerId)
                    print("\tResponse code:\t", code)
                    message = ""
                    if code == 201:
                        message = "Region created successfully. "
                    elif code == 409:
                        message = "Could not create region. "
                    else:
                        message = "Situation unknown. "
                    print("\tMessage:\t", message)


# Calls the main() function
if __name__ == '__main__':
    main()
