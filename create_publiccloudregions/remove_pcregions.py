#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Remove PCRs
# ============
# Environment: With access to internet
# Removes a page of PCRs in order returned by the API
#

from abiquo.client import Abiquo
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


def main():

    parser = argparse.ArgumentParser(description='Remove PCRs!')
    parser.add_argument("--s", default="mjsabiquo",
                        type=str, help="Local system")
    parser.add_argument("--u", default="admin",
                        type=str, help="Username")
    parser.add_argument("--p", default="xabiquo",
                        type=str, help="Password")

    args = parser.parse_args()
    localsystem = args.s
    username = args.u
    password = args.p

    API_URL = "https://" + localsystem + LOCALDOMAINAPI
    api = Abiquo(API_URL, auth=(username, password), verify=False)

    code, pcrsList = api.admin.publiccloudregions.get(
        headers={'Accept': 'application/vnd.abiquo.publiccloudregions+json'})
    print("Get public cloud regions. Response code is: ", code)

    for pcr in pcrsList:
        code = pcr.follow('edit').delete()
        print("Delete public cloud region. Response code is: ", code)


# Calls the main() function
if __name__ == '__main__':
    main()
