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
import copy


def switchEnt(adUserID,entID):
	# You need to switch to the enterprise to create the VDC
	# You will need to supply the ID of your user - default cloud admin is 1
	# Get the user that you are using to access the API 	
	apiUrl = 'http://' + apiIP + '/api/admin/users/' + adUserID
	apiAccept = 'application/vnd.abiquo.user+json;version=3.6'
	apiHeaders = {}
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Authorization'] = apiAuth
	# You can restrict this for a scope
#	apiParams = {'idScope': '1'}
	r = requests.get(apiUrl, headers=apiHeaders, verify=False)
#	r = requests.get(apiUrl, headers=apiHeaders, verify=False, params=apiParams)
	aur_data = r.json()
	aur_data_keys = sorted (aur_data.keys())

	store_aur = {}

	

def createVDC(apiIP,apiAuth,tenantDCID,entID,hyper,vdcName):

	# Create a VDC
	apiUrl = 'http://' + apiIP + '/api/cloud/virtualdatacenters'
	apiContentType = 'application/vnd.abiquo.virtualdatacenter+json;version=3.6'
	apiAccept = 'application/vnd.abiquo.virtualdatacenter+json;version=3.6'
	apiHeaders = {}
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Content-Type'] = apiContentType
	apiHeaders['Authorization'] = apiAuth

	vdc = {}

	vdc['name'] = vdcName

	vdc['cpuCountHardLimit'] = 0
	vdc['ramSoftLimitInMb'] = 0
	vdc['vlansHard'] = 0
	vdc['publicIpsHard'] = 0
	vdc['publicIpsSoft'] = 0
	vdc['ramHardLimitInMb'] = 0
	vdc['vlansSoft'] = 0
	vdc['cpuCountSoftLimit'] = 0

	vdc['vlan'] = {}
	vdc['vlan']['defaultNetwork'] = False
	vdc['vlan']['name'] = 'Default Network'
	vdc['vlan']['links'] = []
	vdc['vlan']['secondaryDNS'] = '8.8.4.4'
	vdc['vlan']['mask'] = '24'
	vdc['vlan']['strict'] = False
	vdc['vlan']['ipv6'] = False
	vdc['vlan']['primaryDNS'] = '8.8.0.0'
	vdc['vlan']['gateway'] = '192.168.0.1'
	vdc['vlan']['address'] = '192.168.0.0'
	vdc['vlan']['type'] = "INTERNAL"

#	vdc['vlan'] = vdcvlan

  	vdc['hypervisorType'] =  hyper

	vdc['links'] = []
	vdc_dc_item =  {}
	vdc_dc_item['href'] = 'http://' + apiIP + '/api/cloud/locations/' + tenantDCID
	vdc_dc_item['type'] = 'application/vnd.abiquo.datacenter+json'
	vdc_dc_item['rel'] = 'location'
	vdc['links'].append(vdc_dc_item)

	vdc_ent_item =  {}
	vdc_ent_item['href'] = 'http://' + apiIP + '/api/admin/enterprises/' + "1"
	vdc_ent_item['rel'] = 'enterprise'
	vdc['links'].append(vdc_ent_item)

	jsonvdc = json.dumps(vdc, ensure_ascii=False)
	# Request to create vdc
	try:
	    uvdc = requests.post(apiUrl, headers=apiHeaders, verify=False, data=jsonvdc)
	except requests.exceptions.RequestException as e:    # This is the correct syntax
	    print e
	    sys.exit(1)

	vdc_data = uvdc.json()
	vdc_data_keys = sorted (vdc_data.keys())
	vdc_id_value = ""
	vdc_name_value = ""
	
	for vk in vdc_data_keys:
		if vk == "id":
			vdc_id_value = vdc_data[vk]
		elif vk == "name":
			vdc_name_value = vdc_data[vk]	

	store_vdc = {}
	if not vdc_id_value == "":
		print "Created VDC: %s " % vdc_name_value 
		store_vdc[vdc_id_value] = (vdc_id_value,vdc_name_value)
	return store_vdc





def createUser(apiIP,apiAuth,enti):

	# Create a user
	apiUrl = 'http://' + apiIP + '/api/admin/enterprises/' + enti + '/users'
	apiContentType = 'application/vnd.abiquo.user+json;version=3.6'
	apiAccept = 'application/vnd.abiquo.user+json;version=3.6'
	apiHeaders = {}
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Content-Type'] = apiContentType
	apiHeaders['Authorization'] = apiAuth


	userFirstName = raw_input("Please enter a user first name, e.g. John: ")		
	userSurname = raw_input("Please enter a user surname, e.g. Smith: ")
	userNick = raw_input("Please enter a username, e.g. johnsmith: ")
	userEmail = raw_input("Please enter a user email, e.g. johnsmith@example.com: ")
	userPassword = raw_input("Please enter user password 8 characters, e.g. johnsmithpw: ")
	userRole = raw_input("Please enter a user role (1 = cloud, 2 = user, 3 = ent admin): ")

	# Data of user to create
	user = {}
	user['name'] = userFirstName
	user['surname'] = userSurname
	user['nick'] = userNick
	user['locale'] = "EN"
	user['firstLogin'] = True
	user['active'] = True
	user['locked'] = False
	user['password'] = userPassword
	user['email'] = userEmail
	user['description'] = "user description"

	user['links'] = []
	user_item =  {}
	user_item['href'] = 'http://' + apiIP + '/api/admin/roles/' + str(userRole)
	user_item['rel'] = 'role'
	user['links'].append(user_item)


	jsonuser = json.dumps(user, ensure_ascii=False)
	# Request to create user
	ur = requests.post(apiUrl, headers=apiHeaders, verify=False, data=jsonuser)
	user_data = ur.json()
	user_data_keys = sorted (user_data.keys())
	user_id_value = ""
	user_username_value = ""
	
	for urk in user_data_keys:
		if urk == "id":
			user_id_value = user_data[urk]
		elif urk == "nick":
			user_username_value = user_data[urk]	

	store_user = {}
	if not user_id_value == "":
		store_user[user_id_value] = (user_id_value,user_username_value)
	return store_user



def createEntDCLimit(apiIP,apiAuth,enti,tenantDCID):

	# Create an enterprise datacenter limit

	apiUrl = 'http://' + apiIP + '/api/admin/enterprises/' + enti + '/limits'
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
	dclimit['links'] = []
	dclimit_item =  {}
	dclimit_item['href'] = 'http://' + apiIP + '/api/admin/datacenters/' + tenantDCID
	dclimit_item['rel'] = 'location'
	dclimit['links'].append(dclimit_item)


	jsonlmt = json.dumps(dclimit, ensure_ascii=False)
	# Request to create enterprise datacente rlimit
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
	ent = createEnt(apiIP,apiAuth,tenName)

	for enok in ent:
		(enti,entn) = ent[enok]
		print "Tenant id: %s  \tName: %s  " % (enti,entn)

		tenRawDC = raw_input("Enter datacenter ID that tenant can access, e.g. 1: ")
		tenDC = int(tenRawDC)
		if tenDC > 0:
			tenantDCID = str(tenDC)
			entID = str(enti)
			tenDCLimitID = createEntDCLimit(apiIP,apiAuth,entID,tenantDCID)	
			print "Tenant limit id: %s" % tenDCLimitID

			dcuser = createUser(apiIP,apiAuth,entID)	

			for uk in dcuser:
				(uid,uun) = dcuser[uk]
				print "User id: %s  \tUsername: %s  \t" % (uid,uun)

			print "Create a VDC"	
			print "Assuming we are working with datacenter: %s " % tenantDCID
			print "And tenant: %s " % entID
			vdcName = raw_input("Enter name for VDC: ")
			hyper = raw_input("Enter hypervisorType for VDC, e.g. KVM, VMX_04: ")

			tenVDC = createVDC(apiIP,apiAuth,tenantDCID,entID,hyper,vdcName)

			if tenVDC:
				for vdk in tenVDC:
					(vid,vna) = tenVDC[vdk]
					print "VDC id: %s  \tVDC name: %s  \t" % (vid,vna)


# Calls the main() function
if __name__ == '__main__':
	main()
			