#!/usr/bin/python2 -tt
#
# This script reads files from the input_files directory:
# - UI labels file (get from /UI/app/lang/lang_en_US_labels.json from current branch in your platform/ui repo
# - database privileges information (run process_privileges.sql on the latest Abiquo DB to create process_privileges_sql.txt)
# - an extra text file (process_privileges_extratext.txt)
# It creates wiki_privileges.txt - a wiki storage format table for pasting into Privileges page of the wiki
# NB: check that privs_processed which is written to standard out is equal to 
# the number of rows in privilege table in Abiquo DB
# select * from privilege;
#
import sys
import re
import json
import os
import collections
import pystache
import codecs
import logging
import requests

class rolec:
	def __init__(self,akey,aname,ainitials,aformat):
		self.rkey = akey
		self.rname = aname
		self.rinitials = ainitials
		self.rformat = aformat

class filedetails:
	def __init__(self,aprefix,asuffix,adate,aiprefix,aisuffix):
		self.fprefix = aprefix
		self.fsuffix = asuffix
		self.fdate = adate
		self.iprefix = aiprefix
		self.isuffix = aisuffix

class priv:
	def __init__(self,aprivCategory,aprivGuiLabel,aprivAppTag,aprivPrivilege,aprivRoles,aprivInfo):
		self.pCategory = aprivCategory
		self.pGuiLabel = aprivGuiLabel
		self.pAppTag = aprivAppTag
		self.pPrivilege = aprivPrivilege
		self.pRoles = aprivRoles
		self.pInfo = aprivInfo

	def pprint(self):
		prRoles = " ".join(self.pRoles)
		print "| %s | %s | %s | %s | %s | %s |" % (self.pCategory,self.pGuiLabel,self.pAppTag,self.pPrivilege,prRoles,self.pInfo)

def do_api_request(apiAuth,apiIP,apiUrl,apiAccept):
		print apiUrl
		apiHeaders = {}
		apiHeaders['Accept'] = apiAccept
		apiHeaders['Authorization'] = apiAuth
		r = requests.get(apiUrl, headers=apiHeaders, verify=False)
		r_data = r.json()
		return r_data

def get_api_privs(apiAuth,apiIP):
# Get role data from the API of a fresh Abiquo	
# First get roles and IDs, then get privileges of each role
	rol_data = {}
	roles_data = {}
# get all base role names and ID numbers
	apiUrl = 'http://' + apiIP + '/api/admin/roles/'  
	apiAccept = 'application/vnd.abiquo.roles+json; version=3.8'
	default_roles_response = do_api_request(apiAuth,apiIP,apiUrl,apiAccept)
	default_roles_list = []
	default_roles = {}
	default_roles_list = default_roles_response['collection']
# create a dictionary with the roles and their IDs	
	for dr in default_roles_list:
		default_roles[dr['name']] = dr['id']
# run through the dictionary and get the privileges for each role
	for drname, drid in default_roles.iteritems():
		apiUrl = 'http://' + apiIP + '/api/admin/roles/' + str(drid) + '/action/privileges'
		print apiUrl
		apiAccept = 'application/vnd.abiquo.privileges+json; version=3.8'
		default_privileges_response = do_api_request(apiAuth,apiIP,apiUrl,apiAccept)		
# create a list like the sql list
		default_privileges_list = []
		default_privileges_list = default_privileges_response['collection']
		for rp in default_privileges_list:
			pname = rp['name']
			if pname in roles_data:
				roles_data[pname].append(drname)
			else:
				roles_data[pname] = [drname]		 	
			for rrr in roles_data:
				print ("rrr: %s" % rrr)		
	return roles_data

def get_options_file():
	# Load properties for the scripts, including wiki properties that can't be stored in a public repo
	options = {}
	with open("../../scripts_properties.json.txt") as opfile:
		opt_file = opfile.read().replace('\n', '')	
		opt_file = opt_file.replace('\t', " ")
		options = json.loads(opt_file)
		for ick in (options):
			logging.info("Options: %s : %s " % (ick,options[ick]))
		input_subdir = options['input_subdir']
		output_subdir = options['output_subdir']	
		fileDate = options['fileDate']	
		filePrefix = options['filePrefix']
		fileSuffix = options['fileSuffix']
		imagePrefix = options['imagePrefix']
		imageSuffix = options['imageSuffix']
		fdetails = filedetails(filePrefix,fileSuffix,fileDate,imagePrefix,imageSuffix)
#		overwriteFiles = proc_strbool(owFiles)
		return (fdetails,input_subdir,output_subdir)
	# These are the details of the sample files and the images that link to the sample files on the wiki
	# fileDate = "_2015-03-28"
	# filePrefix = "properties_"
	# fileSuffix = ".txt"
	# imagePrefix = "v26_symbol_"
	# imageSuffix = "_transparent.png"

def processprivgroups(input_gitdir,privUIFile):
	groupswithprivs = collections.OrderedDict()
	privswithgroups = collections.OrderedDict()
	with codecs.open(os.path.join(input_gitdir,privUIFile), 'r', 'utf-8') as f:
		data=f.read().replace('\n', '')

	names = re.findall('\sis([\w]*?)\s{1,1}([^,]*?),',data,re.U) 

	for n in names:
		groupswithprivs[n[0]] = []
		print ("Event group: %s " % n[0])
		privs = re.findall("(?<=self.name.indexOf\(\')([\w_]*?)(\')",n[1],re.U)
		for p in privs:
			print("ho: %s" % p[0])
			groupswithprivs[n[0]].append(p[0])

	for x in groupswithprivs:
		for y in groupswithprivs[x]:
			print("x: %s" % x)
			print("privgroupnames: %s" % y)
			privswithgroups[y] = x
	return (groupswithprivs,privswithgroups)	

	
def open_if_not_existing(filename):
	try:
		fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
	except:
		print ("File: %s already exists" % filename)
		return None
	fobj = os.fdopen(fd, "w")
	return fobj

def getGroup(privswithgroups,privilege_key):
# First match keys with groups and if that doesn't work, match groups with keys
	priv_group = ""
	for p in privswithgroups:
		if re.search (privilege_key,p):	
			priv_group = privswithgroups[p]
			print ("my pg: %s " % priv_group)
	if not priv_group:
		for p in privswithgroups:		
			print ("my p: %s" % p)
			if re.search (p, privilege_key):
				priv_group = privswithgroups[p]	
				print ("my pp: %s " % priv_group)
				break
	if not priv_group:			
		priv_group = "error"
	return priv_group

def get_extra_text(input_subdir,extfile):
	extlines = (extline.rstrip() for extline in open(os.path.join(input_subdir,extfile)))
	extratext = {}
	for ext_orig in extlines:
		#print (ext_orig)
		extlist = ext_orig.split("|")
		extkey = extlist[0]
		extkey = extkey.strip()
		exttext = extlist[1]
		exttext = exttext.strip()
		extratext[extkey] = exttext
	return(extratext)	

def get_sql(input_subdir,sqlfile):
	sqllines = (sqlline.rstrip() for sqlline in open(os.path.join(input_subdir,sqlfile)))
	sqlroles = {}
# Apparently this will be a dictionary in the format {priv : [role, role, role], priv2 : [ role, role, role]}
	for sql_orig in sqllines:
		print ("sql_orig: %s" % sql_orig)
		sqllist = re.findall(r'([\w_]+)', sql_orig)
		print ("sql_list: %s" % sqllist)
		if sqllist[0] in sqlroles:
			sqlroles[sqllist[0]].append(sqllist[1])
		else:
			sqlroles[sqllist[0]] = [sqllist[1]]		 	
	for r in sqlroles:
		print ("r: %s" % r)		
	return sqlroles

def get_gui_labels(input_gitdir,UIlabelfile):
	privlabels = {}
	privnames = {}
	privdescs = {}
	privgroups = {}
	json_data = open(os.path.join(input_gitdir,UIlabelfile))
	data = json.load(json_data)
#	labelkeys = sorted(data.keys())
#	remove sort
	labelkeys = data.keys()
	for labelkey_orig in labelkeys: 
		labelkey = labelkey_orig.split(".")
		pg = labelkey[0]
		if pg == "privilegegroup":
			pgk = labelkey[1]
			if pgk != "allprivileges":
				privgroups[pgk] = data[labelkey_orig]
				#print ("privilege group: ", labelkey)
		elif pg == "privilege":
			pd = labelkey[1]
			if pd == "description":
				pdk = labelkey[2]
				privdescs[pdk] = data[labelkey_orig]
				#print("privilege description: ", labelkey)
			elif pd != "details":
				privlabels[pd] = pd 
				privnames[pd] = data[labelkey_orig] 
				#print("privilege: ", labelkey)  
	return (privlabels,privnames,privdescs,privgroups)			


def createRoles():	
		# This could be read in from a file
	rollers = collections.OrderedDict()
 	# r = role(akey,aname,ainitials,aformat)
 	rollers["CLOUD_ADMIN"] = rolec("CLOUD_ADMIN","Cloud Admin","CA","warning")
 	rollers["ENTERPRISE_ADMIN"] = rolec("ENTERPRISE_ADMIN","Ent Admin","EA","note")
 	rollers["USER"] = rolec("USER","Ent User","EU","success")
 	rollers["OUTBOUND_API_EVENTS"] = rolec("OUTBOUND_API_EVENTS","Outbound API","OA","info")
 	rollers["ENTERPRISE_VIEWER"] = rolec("ENTERPRISE_VIEWER","Ent Viewer","EV","highlight")
 	return rollers

def createRoleHeader(rollers):
	roleheading = []
 	for rrr in rollers:
 		rhd = {}
 		rhd["roleheadform"]=rollers[rrr].rformat 
 		rhd["rolename"]=rollers[rrr].rname
 		roleheading.append(rhd)
 	return roleheading	

def newOrderByUItextFile(td):	
	uiOrder = collections.OrderedDict()
	catUI = ""
	orderFile = open('input_files/privilege_ui_order_' + td + ".txt")
	for line in orderFile:
		if not re.match("\s",line):
			catProcess=line.strip()
			catUI=re.sub("\s","",catProcess)
			if catUI not in uiOrder:
				uiOrder[catUI] = []
		else:
			if not re.match(" All privileges",line):
				privilege=line.strip()
				uiOrder[catUI].append(privilege)
#	for uiO in uiOrder:
#		print "uiO: %s" % uiO
#		print uiOrder[uiO]
	return uiOrder

def main():
	td = "2016-11-15"
	# use API to get default roles and privileges
	api_privs = {}
	apiAuth = raw_input("Enter API authorization, e.g. Basic XXXX: ")
	apiIP = raw_input("Enter API address, e.g. api.abiquo.com: ")
#	apiroles = get_api_privs(apiAuth,apiIP)
#	sqlroles_unsorted = get_api_privs(apiAuth,apiIP)
#	sqlroles = collections.OrderedDict(sorted(sqlroles_unsorted.items()))

	sqlroles = get_api_privs(apiAuth,apiIP)

	privUIFile = "privilegesMgr.js"
	thisscript = "privileges"

	(fdetails,input_subdir,output_subdir) = get_options_file()
	input_gitdir = '../../platform/ui/app/lang'
	input_gitdir2 = '../../platform/ui/app/js/services'
	input_subdir = 'input_files'
	output_subdir = 'output_files'
	groupswithprivis=collections.OrderedDict()
	priviswithgroups=collections.OrderedDict()

	(groupswithprivis,priviswithgroups) = processprivgroups(input_gitdir2,privUIFile)

	logging.basicConfig(filename='api_examples.log',level=logging.DEBUG)

	# infoprint = {}
	# infoprint["N"] = '<ac:emoticon ac:name="yellow-star"/>'
	# infoprint["C"] = '<ac:emoticon ac:name="warning"/>'
	# infoprint["D"] = '<ac:emoticon ac:name="minus"/>'

	rollers = createRoles()
	rheaders = createRoleHeader(rollers)

	input_gitdir = '../../platform/ui/app/lang'
	input_subdir = 'input_files'
	output_subdir = 'output_files'

	extfile = 'process_privileges_extratext.txt'   
	extratext = {}
	extratext = get_extra_text(input_subdir,extfile)


# 	sqlroles = {}
#	sqlfile = 'process_privileges_sql_2015-08-04.txt'

#	sqlroles = get_sql(input_subdir,sqlfile)

 	
 	groupmatch = collections.OrderedDict()
 	gmatch = collections.OrderedDict()
	#grouporder = {1: 'home', 2: 'infrastructure', 3: 'virtualDatacenters', 4: 'virtualAppliances', 5: 'appsLibrary', 6: 'users', 7: 'systemConfiguration', 8: 'events', 9: 'pricing'}

	groupord = {'home','infrastructure','virtualDatacenters','virtualAppliances','appsLibrary','users','systemConfiguration','events','pricing'}

#	groupheaders = {'home': 'Home', 'infrastructure': 'Infrastructure', 'virtualDatacenters': 'Virtual datacenters', 'virtualAppliances': 'Virtual appliances','appsLibrary': 'Apps library', 'users': 'User', 'systemConfiguration': 'Configuration', 'events': 'Events', 'pricing': 'Pricing'}
	groupheaders = {'Home': 'Home', 'Infrastructure': 'Infrastructure', 'VirtualDatacenter': 'Virtual datacenter', 'VirtualAppliance': 'Virtual appliance','AppsLibrary': 'Apps library', 'Users': 'User', 'SystemConfiguration': 'System configuration', 'Pricing': 'Pricing', 'Events': 'Event'}

	gmatch = {'ENTERPRISE':'home','PHYS':'infrastructure','VDC':'virtualDatacenters','VAPP':'virtualAppliances','APPLIB':'appsLibrary','USERS':'users','SYSCONFIG':'systemConfiguration','EVENTLOG':'events','PRICING':'pricing'}

	groupmatch = {'home': 'ENTERPRISE', 'infrastructure': 'PHYS', 'virtualDatacenters': 'VDC', 'virtualAppliances': 'VAPP','appsLibrary': 'APPLIB', 'users': 'USERS', 'systemConfiguration': 'SYSCONFIG', 'events': 'EVENTLOG', 'pricing': 'PRICING'}

	labelmatch = {'MANAGE_FIREWALLS': 'VDC', 'MANAGE_LOADBALANCERS': 'VDC', 'MANAGE_FLOATINGIPS': 'VDC', 'WORKFLOW_OVERRIDE': 'VAPP', 'MANAGE_HARD_DISKS': 'VAPP', 'USERS_SHOW_VM_METRICS':'VAPP', 'USERS_ENABLE_DISABLE_VM_METRICS':'VAPP', 'ASSIGN_FIREWALLS':'VAPP', 'ASSIGN_LOADBALANCERS': 'VAPP', 'VM_PROTECT_ACTION': 'VAPP', 'APPLIB_VM_COST_CODE': 'PRICING'}


#	grouplist['virtualAppliances'] = {'VAPP_','VM_PROTECT_ACTION', 'WORKFLOW_OVERRIDE', 'MANAGE_HARD_DISKS', 'ASSIGN_LOADBALANCERS','ASSIGN_FIREWALLS'}
	vdc_privs = {'MANAGE_LOADBALANCERS', 'MANAGE_FIREWALLS', 'MANAGE_FLOATINGIPS'}

	UIlabelfile = 'lang_en_US_labels.json'
	(privlabels,privnames,privdescs,privgroups) = get_gui_labels(input_gitdir,UIlabelfile)

#	print ("privdescs assign_firewalls: %s " % privdescs["ASSIGN_FIREWALLS"])
#	print ("privnames assign_firewalls: %s " % privnames["ASSIGN_FIREWALLS"])
	# for pi in privlabels:
	# 	print ("privlabels: %s" % pi)
	# for pg in privgroups:
	# 	print ("privgroups: %s" % pg)

	categories = []

	# output_file_name = 'wiki_privileges_2014-10-21.txt'
	# out_file = open(os.path.join(output_subdir,output_file_name), 'w')
	# out_file.close()

	newUiOrder = collections.OrderedDict()
	newUiOrder = newOrderByUItextFile(td)


 	priv_cats = {}
	ppdict = {}
	# for pp in sqlroles:
	# 	print ("pp: %s" % pp)
	# Note these now come from the API
	for pp in sqlroles:	
		# create a privilege data object
		if pp in privdescs:
		 	priv_desc = privdescs[pp]
		if pp in extratext:
			priv_desc = priv_desc + ". " + extratext[pp]  
	 	roleslist = []
		for ro in rollers:
			if ro in sqlroles[pp]:
	 			roleslist.append(ro)
	 	info = ""

		priv_group = getGroup(priviswithgroups,pp)
#		print ("pp:  %s  | group: %s" % (pp,priv_group))


	 	# group = gmatch[priv_group]
	 	# print ("priv_group: %s" % priv_group)

		privo = priv(priv_group,privnames[pp],pp,priv_desc,roleslist,info)
	 	privo.pprint()
	 	
	 	if priv_group in priv_cats:
			priv_cats[priv_group].append(pp)
		else:
			priv_cats[priv_group] = [pp]

		for blah in priv_cats:
			boo = priv_cats[blah]
			print("blah: %s boo: %s " % (blah,boo))	

		# create a privilege json
		privi = {}
		privi["guiLabel"] = privo.pGuiLabel
		privi["appTag"] = privo.pAppTag
		privi["privilege"] = privo.pPrivilege
		privi["roles"] = []
		for rx in rollers:
			role = {}
			role['role'] = {}
			rolex = {}
			rolex["roleformat"] = rollers[rx].rformat
			roleMark = {}
			if rx in privo.pRoles:
				roleMark["roleMark"] = "X"
				rolex["rolehas"] = roleMark
			role['role'] = rolex	
			privi["roles"].append(role)		
		privi["info"] = {}	
		ppdict[pp] = privi

		# get the guiLabel = privo.pGuiLabel
		# get the appTab = privo.pAppTag
		# get the group = priv_group
		newUIO = 0
		# get the label position in the ui order list
		newUIO = newUiOrder[priv_group].index(privo.pGuiLabel)
		print "NEW UI ORDER: %d" % newUIO
		# put the record in the label position

	# process all the groups in order
	for g in groupswithprivis:
#		print ("g: %s" % g)
		gh = groupheaders[g]
		category = {}
		category["category"] = gh
		category["roleheader"] = rheaders
		category['entries'] = []
		for p in priv_cats[g]:
#			category["entries"].append(ppdict[p])	
			category["entries"].insert((newUIO+1),ppdict[p])			
		categories.append(category)		

	privilege_out = {}		
	privilege_out["categories"] = categories

	# write a json file with the privileges with the privilege key as the index
	js = open_if_not_existing("cats.json")
	if js:
	 	json.dump(ppdict, js)
	 	js.close

	# write a json file with the privileges for the mustache render
	jm = open_if_not_existing("camu.json")
	if jm:
	 	json.dump(categories, jm)
	 	jm.close


	# do the mustache render
	mustacheTemplate = codecs.open("wiki_privileges_template.mustache", 'r', 'utf-8').read()
	efo = pystache.render(mustacheTemplate, privilege_out).encode('utf8', 'xmlcharrefreplace')

	ef = open_if_not_existing(os.path.join(output_subdir,"privileges_out_" + td + ".txt"))
	if ef:
		ef.write(efo)
		ef.close()	 

  
# Calls the main() function
if __name__ == '__main__':
  main()
