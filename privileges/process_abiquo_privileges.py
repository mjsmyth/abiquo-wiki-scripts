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
	
def open_if_not_existing(filename):
	try:
		fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
	except:
		print ("File: %s already exists" % filename)
		return None
	fobj = os.fdopen(fd, "w")
	return fobj

def getCategory(labelmatch,plk_orig):
	if plk_orig in labelmatch.keys():
		plk = labelmatch[plk_orig]
	else:	
		plk_split = plk_orig.split("_")
		plk = plk_split[0]
	return plk	

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
	labelkeys = sorted(data.keys())
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
 	return rollers

def createRoleHeader(rollers):
	roleheading = []
 	for rrr in rollers:
 		rhd = {}
 		rhd["roleheadform"]=rollers[rrr].rformat 
 		rhd["rolename"]=rollers[rrr].rname
 		roleheading.append(rhd)
 	return roleheading	


def main():
	infoprint = {}
	infoprint["N"] = '<ac:emoticon ac:name="yellow-star"/>'
	infoprint["C"] = '<ac:emoticon ac:name="warning"/>'
	infoMarkDep = '<ac:emoticon ac:name="minus"/>'

	rollers = createRoles()
	rheaders = createRoleHeader(rollers)

	input_gitdir = '../../platform/ui/app/lang'
	input_subdir = 'input_files'
	output_subdir = 'output_files'

	extfile = 'process_privileges_extratext.txt'   
	extratext = {}
	extratext = get_extra_text(input_subdir,extfile)

	sqllabels = {}
	sqlroles = {}
	sqlfile = 'process_privileges_sql_2014-10-21.txt'

	sqlroles = get_sql(input_subdir,sqlfile)

 	
 	groupmatch = collections.OrderedDict()
 	gmatch = collections.OrderedDict()
	#grouporder = {1: 'home', 2: 'infrastructure', 3: 'virtualDatacenters', 4: 'virtualAppliances', 5: 'appsLibrary', 6: 'users', 7: 'systemConfiguration', 8: 'events', 9: 'pricing'}

	groupord = {'home','infrastructure','virtualDatacenters','virtualAppliances','appsLibrary','users','systemConfiguration','events','pricing'}
	groupheaders = {'home': 'Home', 'infrastructure': 'Infrastructure', 'virtualDatacenters': 'Virtual datacenters', 'virtualAppliances': 'Virtual appliances','appsLibrary': 'Apps library', 'users': 'User', 'systemConfiguration': 'Configuration', 'events': 'Events', 'pricing': 'Pricing'}

	gmatch = {'ENTERPRISE':'home','PHYS':'infrastructure','VDC':'virtualDatacenters','VAPP':'virtualAppliances','APPLIB':'appsLibrary','USERS':'users','SYSCONFIG':'systemConfiguration','EVENTLOG':'events','PRICING':'pricing'}

	groupmatch = {'home': 'ENTERPRISE', 'infrastructure': 'PHYS', 'virtualDatacenters': 'VDC', 'virtualAppliances': 'VAPP','appsLibrary': 'APPLIB', 'users': 'USERS', 'systemConfiguration': 'SYSCONFIG', 'events': 'EVENTLOG', 'pricing': 'PRICING'}

	labelmatch = {'VM_PROTECT_ACTION': 'VAPP', 'MANAGE_LOADBALANCERS': 'VDC', 'MANAGE_FIREWALLS': 'VDC', 'MANAGE_FLOATINGIPS': 'VDC', 'WORKFLOW_OVERRIDE': 'VAPP', 'MANAGE_HARD_DISKS': 'VAPP', 'ASSIGN_LOADBALANCERS': 'VAPP', 'ASSIGN_FIREWALLS': 'VAPP', 'APPLIB_VM_COST_CODE': 'PRICING'}

	vapp_privs = {'VM_PROTECT_ACTION', 'WORKFLOW_OVERRIDE', 'MANAGE_HARD_DISKS', 'ASSIGN_LOADBALANCERS','ASSIGN_FIREWALLS', }
	vdc_privs = {'MANAGE_LOADBALANCERS', 'MANAGE_FIREWALLS', 'MANAGE_FLOATINGIPS'}

	UIlabelfile = 'lang_en_US_labels.json'
	(privlabels,privnames,privdescs,privgroups) = get_gui_labels(input_gitdir,UIlabelfile)

	print ("privdescs assign_firewalls: %s " % privdescs["ASSIGN_FIREWALLS"])
	print ("privnames assign_firewalls: %s " % privnames["ASSIGN_FIREWALLS"])
	for pi in privlabels:
		print ("privlabels: %s" % pi)
	for pg in privgroups:
		print ("privgroups: %s" % pg)

	categories = []

	# output_file_name = 'wiki_privileges_2014-10-21.txt'
	# out_file = open(os.path.join(output_subdir,output_file_name), 'w')
	# out_file.close()

 	priv_cats = {}
	ppdict = {}
	for pp in sqlroles:
		print ("pp: %s" % pp)
	for pp in sqlroles:	
		# create a privilege data object
		if pp in privdescs:
		 	priv_desc = privdescs[pp]
		if pp in extratext:
			priv_desc = priv_desc + extratext[pp]  
	 	roleslist = []
		for ro in rollers:
			if ro in sqlroles[pp]:
	 			roleslist.append(ro)
	 	info = ""

	 	priv_group = getCategory(labelmatch,pp)
	 	print ("group: %s" % priv_group)


	 	group = gmatch[priv_group]
	 	print ("priv_group: %s" % priv_group)

		privo = priv(priv_group,privnames[pp],pp,priv_desc,roleslist,info)
	 	privo.pprint()
	 	
	 	if priv_group in priv_cats:
			priv_cats[priv_group].append(pp)
		else:
			priv_cats[priv_group] = [pp]

		for poo in priv_cats:
			boo = priv_cats[poo]
			print("boo: %s " % boo)	

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




	# process all the groups in order
	for g in groupord:
		gr = groupmatch[g]
		gh = groupheaders[g]
		category = {}
		category["category"] = gh
		category["roleheader"] = rheaders
		category['entries'] = []
		for p in priv_cats[gr]:
			category["entries"].append(ppdict[p])	
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
	ef = open_if_not_existing("privileges_out.txt")
	if ef:
		ef.write(efo)
		ef.close()	  

  
# Calls the main() function
if __name__ == '__main__':
  main()
