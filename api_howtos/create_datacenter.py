import json
from abiquo.client import Abiquo
from abiquo.client import check_response

api = Abiquo(API_URL, auth=(username, password))
code, datacenters = api.admin.datacenters.get(
    headers={'Accept':'application/vnd.abiquo.datacenters+json'})

print "Response code is: %s" % code
for dc in datacenters:
    print "Creating rack in datacenter %s [%s]" % (dc.name, dc.location)
    code, rack = dc.follow('racks').post(
            data=json.dumps({'name': 'New rack'}),
            headers={'accept':'application/vnd.abiquo.rack+json',
                     'content-type':'application/vnd.abiquo.rack+json'})
    check_response(201, code, rack)
    print "Response code is: %s" % code
    print "Created Rack: %s" % rack.name