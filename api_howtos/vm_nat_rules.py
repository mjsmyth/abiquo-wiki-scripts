#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# VM NAT rules
# ============ 
# Environment: NAT and VDC with NAT IP
#
# Add NAT rules to VM 
# -------------------
# * Requires: 1 x VM 
# ** With private IP to add NAT rules
# ** Not deployed or powered off 
# *** - check if only 1 snat per NATIP/check only one DNAT per port 
# * Steps
# ** Get VM without NAT rules by vmlabel (default NATADD) 
# ** Get its private IP to add to NAT rules JSON
# ** Get VDC of VM (use in part 2 also)
# ** Get NAT IPs of VDC to add to NAT rules JSON
# ** Get NAT rules of VDC?
# ** Create a NAT rule with private IP/NAT IP
#
# Create a VM with NAT rules
# --------------------------
# * Requires:
# ** 1 x private IP available in VDC 
# ** VM label will be NATNEW
# * Steps:
# ** Use VDC of NATADD VM 
# ** Get template from the NATADD VM
# ** Get virtual appliance from NATADD VM
# ** Get available private IPs in VDC
# ** Get NAT IPs in VDC. If same NATIP, add 1 to port number
# ** Create VM with NAT rules
#

import json
from abiquo.client import Abiquo
from abiquo.client import check_response
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DNATPORTORIGINAL = 36913
DNATPORTTRANSLATED = 22
DNATPROTOCOL = "TCP"

def main ():

# For test
	localsystem = sys.argv[1] 
	username = sys.argv[2]
	password = sys.argv[3]
	API_URL="https://" + localsystem + ".bcn.abiquo.com/api"
	api = Abiquo(API_URL, auth=(username, password), verify=False)

# For customers
#	API_URL = input("Enter Abiquo API URL, e.g 'https://abiquoapi.bcn.abiquo.com/api': ")
#	username = input("Username: ")
#	password = input("Password: ")
	# Assuming test environment with self-signed certificate
#	api = Abiquo(API_URL, auth=(username, password), verify=False)

# Get NATADD VM to add NAT rules, with vmlabel filter = NATADD
	code, virtualmachines = api.cloud.virtualmachines.get(
	headers={'Accept':'application/vnd.abiquo.virtualmachines+json'},
	params={'vmlabel':'NATADD'})
	print ("Response code is: ", code)
	if virtualmachines.totalSize > 1:
		print ("Warning! Multiple VMs with same label!")
	for vm in virtualmachines:
		print ("NATADD VM: ", str(vm.label))
		if vm.natrules:
			print ("Warning! VM already has NAT Rules!")
			break
		if not vm.nic0:
			print ("Warning! VM has no NIC")	
		else:
			# ** Get its private IP to add to NAT rules JSON
			privateIPUrl = vm.nic0.url
			print ("Private IP: ", privateIPUrl)
			code, NIC = vm.follow('nic0').get(
				headers={'Accept':'application/vnd.abiquo.privateip+json'}) 

			# ** Get VDC of VM (use in part 2 also)
			vdcUrl = vm.virtualdatacenter.url
			print ("Virtual datacenter: ", vdcUrl)

			code, virtualdatacenter = vm.follow('virtualdatacenter').get(
				headers={'Accept':'application/vnd.abiquo.virtualdatacenter+json'})
			print ("Response code is: ", code)
			print ("VM belongs to VDC: ", virtualdatacenter.name)

			# ** Get NAT IPs of VDC to add to NAT rules JSON
			code, natips = virtualdatacenter.follow('natips').get(
				headers={'Accept':'application/vnd.abiquo.natips+json'})
			print ("Response code is: ", code)
			for nnip in natips:
				print ("nnip url: ", nnip.ip)
				code, nini = nnip.follow('natnetwork').get(
				headers={'Accept':'application/vnd.abiquo.natnetwork+json'})	
				print ("Response code: ", code)
				print ("nini: ", nini.address)

			 
			# print ("NAT IP URL: ", naipUrl)
			# mediaTypeNatIP = "application/vnd.abiquo.natip+json"
			# mediaTypePriIP = "application/vnd.abiquo.privateip+json"
			# # ** Create NAT rules with private IP/NAT IP
			# natrules = []

			# snatrule = {}
			# snatrule["snat"] = True
			# snatrule["links"] = []
			# snatrule["links"].append ({"rel":"original","href":privateIPUrl,"type":mediaTypePriIP})
			# snatrule["links"].append ({"rel":"translated","href":naipUrl,"type":mediaTypeNatIP})
			# natrules.append(snatrule)
			
			# dnatrule = {} 
			# dnatrule["snat"] = False
			# dnatrule["originalPort"] = DNATPORTORIGINAL
			# dnatrule["translatedPort"] = DNATPORTTRANSLATED
			# dnatrule["protocol"] = DNATPROTOCOL
			# dnatrule["links"].append ({"rel":"original","href":naipUrl,"type":mediaTypeNATIP})
			# snatrule["links"].append ({"rel":"translated","href":privateIPUrl,"type":mediaTypePriIP})
			# natrules.append(dnatrule)

			# print ("natrules: ", json.dumps(natrules, indent=2))

# Calls the main() function
if __name__ == '__main__':
	main()
			