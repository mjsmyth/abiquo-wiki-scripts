#!/usr/bin/python2 -tt
# -*- coding: UTF-8 -*-
# Tenant setup script
# 0. Get a list of Datacenters
# 1. Create an enteprise
# 1a. Add a datacenter for the enterprise
# 2. Create a user for the enterprise
# 3. Create a VDC
import json
import requests


def createEntDCLimit(apiIP,apiAuth,enti,tenDC):

	# Create an enterprise datacenter limit
	apiUrl = 'http://' + apiIP + '/api/admin/enterprises' + enti + 'limits'
	apiContentType = 'application/vnd.abiquo.limit+json;version=3.6'
	apiAccept = 'application/vnd.abiquo.limit+json;version=3.6'
	apiHeaders = {}
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Content-Type'] = apiContentType
	apiHeaders['Authorization'] = apiAuth

	# Data of enterprise to create
	dclimit = {}
	dclimit['cpuCountHardLimit'] = 0
	dclimit['ramSoftLimitInMb'] = 0
	dclimit['vlansHard'] = 0
	dclimit['publicIpsHard'] = 0
	dclimit['publicIpsSoft'] = 0
	dclimit['ramHardLimitInMb'] = 0
	dclimit['vlansSoft'] = 0
	dclimit['cpuCountSoftLimit'] = 0
	dclimit['links'] =  []
	dclimit_item =  {}
	dclimit_item['href'] = 'http://' + apiIP + 'api/admin/datacenters/' + tenDC 
	dclimit_item['rel'] = location
	dclimit['links'].append(dclimit_item)


	jsonlmt = json.dumps(dclimit, ensure_ascii=False)
	# Request to create enterprise
	dcl = requests.post(apiUrl, headers=apiHeaders, verify=False, data=jsonlmt)
	dcl_data = dcl.json()
	dcl_data_keys = sorted (dcl_data.keys())
	dcl_id_value = ""
	
	for dclk in dcl_data_keys:
		if dclk == "id":
			dcl_id_value = dcl_data[dclk]
	
	return dcl_id_value



def createEnt(apiIP,apiAuth,tenName):

	# Create a tenant
	apiUrl = 'http://' + apiIP + '/api/admin/enterprises'
	apiContentType = 'application/vnd.abiquo.enterprise+json;version=3.6'
	apiAccept = 'application/vnd.abiquo.enterprise+json;version=3.6'
	apiHeaders = {}
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Content-Type'] = apiContentType
	apiHeaders['Authorization'] = apiAuth

	# Data of enterprise to create
	enterprise = {}
	enterprise['name'] = tenName

	enterprise['cpuCountHardLimit'] = 0 
	enterprise['diskHardLimitInMb'] = 0
	enterprise['ramSoftLimitInMb'] = 0 
	enterprise['vlansHard'] = 0
	enterprise['publicIpsHard'] = 0
	enterprise['publicIpsSoft'] = 0
	enterprise['ramHardLimitInMb'] = 0 
	enterprise['vlansSoft'] = 0 
	enterprise['cpuCountSoftLimit'] = 0 
	enterprise['diskSoftLimitInMb'] = 0

	jsonent = json.dumps(enterprise, ensure_ascii=False)
	# Request to create enterprise
	er = requests.post(apiUrl, headers=apiHeaders, verify=False, data=jsonent)
	ent_data = er.json()
	ent_data_keys = sorted (ent_data.keys())
	ent_id_value = ""
	ent_name_value = ""
	
	for enk in ent_data_keys:
		if enk == "id":
			ent_id_value = ent_data[enk]
		elif enk == "name":
			ent_name_value = ent_data[enk]	

	store_en = {}
	if not ent_id_value == "":
		store_en[ent_id_value] = (ent_id_value,ent_name_value)
	return store_en



def getDCs(apiIP,apiAuth):

	# Get the datacenter light list (ids and names and links) from the API of a fresh Abiquo	
	apiUrl = 'http://' + apiIP + '/api/admin/datacenters'
	apiAccept = 'application/vnd.abiquo.datacenterslight+json;version=3.6'
	apiHeaders = {}
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Authorization'] = apiAuth
	# You can restrict this for a scope
	apiParams = {'idScope': '1'}

	r = requests.get(apiUrl, headers=apiHeaders, verify=False, params=apiParams)
	dc_data = r.json()
	dc_data_keys = sorted (dc_data.keys())

	store_dc = {}

# Process the datacenter light list	
# For each datacenter get the ID, name and type
	for dck in dc_data_keys:
		dc_id_value = ""
		dc_name_value = ""
		dc_type_value = ""
		if dck == "collection":
			dc_collection = dc_data[dck]
			for dc_item in dc_collection:
				dc_keys = sorted (dc_item.keys())
				for dk in dc_keys:
					if dk == "idDatacenter":
						dc_id_value = dc_item[dk]
						print "dc_id %s " % dc_id_value
					elif dk == "name":
						dc_name_value = dc_item[dk].decode('utf-8')	
						print "dc_name %s " % dc_name_value
					elif dk == "links":
						dc_links = dc_item[dk]
						for dc_link_item in dc_links:
							dc_links_keys = sorted (dc_link_item.keys())
							for dlk in dc_links_keys:
								if dlk == "type":
									dc_type_value = dc_link_item[dlk]
									print "dc_type_value %s " % dc_type_value
				if not dc_id_value == "":
					print "Datacenter id: %s  \tName: %s  \tType: %s" % (dc_id_value,dc_name_value,dc_type_value)
					store_dc[dc_id_value] = (dc_id_value,dc_name_value,dc_type_value)
	return store_dc				


def main ():

	apiAuth = raw_input("Enter API authorization, e.g. Basic XXXX: ")
	apiIP = raw_input("Enter API address, e.g. api.abiquo.com: ")
	dcs = {}
	dcs = getDCs(apiIP,apiAuth)
	for dcok in dcs:
		(dci,dcn,dct) = dcs[dcok]
		print "Datacenter id: %s  \tName: %s  \tType: %s" % (dci,dcn,dct)


    tenName = raw_input("Please enter a tenant name, e.g. My Enterprise: ")

	ent = createTenant(apiIP,apiAuth,tenName)

	for enok in ent:
		(enti,entn) = ent[enok]
		print "Tenant id: %s  \tName: %s  " % (enti,entn)

		tenRawDC = raw_input("Enter datacenter ID that tenant can access, e.g. 1: ")
		tenDC = int(tenRawDC)
		if tenDC > 0:
			createEntDClimit(apiIP,apiAuth,enti,tenDC)	

# Calls the main() function
if __name__ == '__main__':
	main()
			