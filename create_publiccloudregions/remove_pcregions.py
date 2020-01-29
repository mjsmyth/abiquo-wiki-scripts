#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Remove PCRs
# ============
# Environment: With access to internet
# Removes a page of PCRs in order returned by the API
# Can't remove PCRs with stuff in them

from abiquo.client import Abiquo
import argparse
# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():

    parser = argparse.ArgumentParser(description='Remove a page of PCRs!')
    parser.add_argument("--s", default="https://mjsabiquo.bcn.abiquo.com/api",
                        type=str, help="API url")
    parser.add_argument("--u", default="admin",
                        type=str, help="Username")
    parser.add_argument("--p", default="xabiquo",
                        type=str, help="Password")

    args = parser.parse_args()
    apiUrl = args.s
    username = args.u
    password = args.p

    api = Abiquo(apiUrl, auth=(username, password), verify=False)

    code, pcrsList = api.admin.publiccloudregions.get(
        headers={'Accept': 'application/vnd.abiquo.publiccloudregions+json'})
    print("Get public cloud regions. Response code is: ", code)

    for pcr in pcrsList:
        print("Delete public cloud region: ", pcr.name)
        code, pcrobject = pcr.follow('edit').delete()
        print("Response code is: ", code)


# Calls the main() function
if __name__ == '__main__':
    main()
