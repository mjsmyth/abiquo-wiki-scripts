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
import copy
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
			print ("Warning! VM has no NICs")
			break	
		else:
			# ** Get link to its private IP to add to NAT rules JSON
			privateIPLinks = list(filter(lambda vmlink: "privateip" in vmlink["type"], vm.json["links"]))
			# Use the first private IP
			pipLink = privateIPLinks[0]
			print ("Private IP link:", json.dumps(pipLink, indent=2))

			# ** Get VDC of VM (use in part 2 also)
			code, vdc = vm.follow('virtualdatacenter').get(
				headers={'accept':'application/vnd.abiquo.virtualdatacenter+json'})
			print ("Response code is: ", code)
			print ("VM belongs to VDC: ", vdc.name)

			# ** Get NAT IPs of VDC to add to NAT rules JSON
			code, natips = vdc.follow('natips').get(
				headers={'accept':'application/vnd.abiquo.natips+json'})
			print ("Response code is: ", code)

			nonDefaultSNATIPs = list(filter(lambda nsnatip: nsnatip.json["defaultSnat"] == False, natips))

			# Get first NAT IP of VDC that is not the default SNAT 
			ndsnaip = nonDefaultSNATIPs[0]
			print ("ndsnaip: ", json.dumps(ndsnaip.json, indent=2))
			# Get the self link of the NAT IP
			natipLinks = list(filter(lambda link: link["rel"] == "self", ndsnaip.json["links"]))
			natipLink = natipLinks[0]
			print ("natipLink: ", json.dumps(natipLink, indent=2))
			 

			mediaTypeNatIP = "application/vnd.abiquo.natip+json"
			mediaTypePriIP = "application/vnd.abiquo.privateip+json"
			# # ** Create NAT rules with private IP/NAT IP
			addnatrules = []

			snatrule = {}
			snatrule["snat"] = True
			snatrule["links"] = []
			snatruleOriginalLink = copy.deepcopy(pipLink)
			snatruleOriginalLink["rel"] = "original"
			snatrule["links"].append (snatruleOriginalLink)
			snatruleTranslatedLink = copy.deepcopy(natipLink)
			snatruleTranslatedLink["rel"] = "translated"
			snatrule["links"].append (snatruleTranslatedLink)
			print ("snatrule: ", json.dumps(snatrule, indent=2))
			addnatrules.append(snatrule)
			
			dnatrule = {} 
			dnatrule["snat"] = False
			dnatrule["originalPort"] = DNATPORTORIGINAL
			dnatrule["translatedPort"] = DNATPORTTRANSLATED
			dnatrule["protocol"] = DNATPROTOCOL
			dnatruleOriginalLink = copy.deepcopy(natipLink)
			dnatruleOriginalLink["rel"] = "original"
			dnatrule["links"] = []
			dnatrule["links"].append (dnatruleOriginalLink)
			dnatruleTranslatedLink = copy.deepcopy(pipLink)
			dnatruleTranslatedLink["rel"] = "translated"
			dnatrule["links"].append (dnatruleTranslatedLink)
			print ("dnatrule: ", json.dumps(dnatrule, indent=2))
			addnatrules.append(dnatrule)

			vmEditLinks = list(filter(lambda link: link["rel"] == "edit", vm.json["links"]))
			vmEditLink = vmEditLinks[0]
			print ("vm edit link", json.dumps(vmEditLink, indent=2))

			#	newvm = copy.deepcopy(vm.json)
			# Add the nat rules to the VM object
			vm.json["natrules"] = addnatrules[:]

			# If VM is deployed receive acceptedrequest!
			code, vmaddnr = vm.follow('edit').put(
				headers={'accept':'application/vnd.abiquo.acceptedrequest+json', 'content-type':'application/vnd.abiquo.virtualmachine+json'},
				data=json.dumps(vm.json))
			print ("Response code is: ", code)

			# Do a put request to the VM with the VM nat object 

# Calls the main() function
if __name__ == '__main__':
	main()
			