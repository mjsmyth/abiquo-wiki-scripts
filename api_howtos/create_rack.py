import json
from abiquo.client import Abiquo
from abiquo.client import check_response
import sys

# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

localsystem = sys.argv[1]
newrackname = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]
API_URL = "https://" + localsystem + ".bcn.abiquo.com/api"

api = Abiquo(API_URL, auth=(username, password), verify=False)
# api = Abiquo(API_URL, auth=(username, password))

code, datacenters = api.admin.datacenters.get(
    headers={'Accept': 'application/vnd.abiquo.datacenters+json'})

print("Response code is: ", code)
for dc in datacenters:
    print("Creating rack in datacenter: ", dc.name, "[", dc.location, "]")
    code, rack = dc.follow('racks').post(
            data=json.dumps({'name': newrackname,
                             'vlanIdMax': 4094}),
            headers={'accept': 'application/vnd.abiquo.rack+json',
                     'content-type': 'application/vnd.abiquo.rack+json'})
    check_response(201, code, rack)
    print("Response code is: ", code)
    print("Created Rack: ", rack.name)

    # Print edit link of rack
    for racklink in rack.links:
        if racklink["rel"] == "edit":
            print("Rack edit link: ", json.dumps(racklink, indent=2))
