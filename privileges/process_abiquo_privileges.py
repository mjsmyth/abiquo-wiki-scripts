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

class role:
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

def get_extra_text(input_subdir,extfile):
	extlines = (extline.rstrip() for extline in open(os.path.join(input_subdir,extfile)))
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
		#print (sql_orig)
		sqllist = re.findall(r'([\w_]+)', sql_orig)
	for sq in sqllist:
		if sq[0] in sqlroles:
			sqlroles[sq[0]].append(sq[1])
		else
			sqlroles[sq[0]] = [sq[1]]
	return sqlroles

def get_gui_labels(input_gitdir,UIlabelfile):
	json_data = open(os.path.join(input_gitdir,UIlabelfile))
	data = simplejson.load(json_data)
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
 	rollers["CLOUD_ADMIN"] = role("CLOUD_ADMIN","Cloud Admin","CA","warning")
 	rollers["ENTERPRISE_ADMIN"] = role("ENTERPRISE_ADMIN","Ent Admin","EA","note")
 	rollers["USER"] = role("USER","Ent User","EU","success")
 	rollers["OUTBOUND_API_EVENTS"] = role("OUTBOUND_API_EVENTS","Outbound API","OA","info")
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

	sql_total = 0
	privs_processed = 0

	input_gitdir = '../platform/ui/app/lang'
	input_subdir = 'input_files'
	output_subdir = 'output_files'

	extfile = 'process_privileges_extratext.txt'   
	extratext = {}
	extratext = get_extra_text(input_subdir,extfile)

	sqllabels = {}
	sqlroles = {}
	sqlfile = 'process_privileges_sql_2014-10-21.txt'

	sqlroles = get_sql(input_subdir,sqlfile)


	#orderlabels = {}
	#orderroles = {}
	#orderfile = 'order_brief.txt'
	#orderlines = (orderline.rstrip() for orderline in open(orderfile))
	#for order_orig in orderlines:
		#print (sql_orig)
	#	ordernum = re.search(r'([\d_]+)', order_orig)
	#	orderkey = re.search(r'([\w_]+)', order_orig)
	#	orderlist_joinkey = ordernum + "=" + orderkey[1]
	#	orderlabels[orderlist_joinkey] = ordernum
	#	orderroles[orderlist_joinkey] = orderkey
 
	grouporder = {1: 'home', 2: 'infrastructure', 3: 'virtualDatacenters', 4: 'virtualAppliances', 5: 'appsLibrary', 6: 'users', 7: 'systemConfiguration', 8: 'events', 9: 'pricing'}
	groupmatch = {'home': 'ENTERPRISE', 'infrastructure': 'PHYS', 'virtualDatacenters': 'VDC', 'virtualAppliances': 'VAPP','appsLibrary': 'APPLIB', 'users': 'USERS', 'systemConfiguration': 'SYSCONFIG', 'events': 'EVENTLOG', 'pricing': 'PRICING'}
	
	labelmatch = {'MANAGE_LOADBALANCERS': 'VDC', 'MANAGE_FIREWALLS': 'VDC', 'MANAGE_FLOATINGIPS': 'VDC', 'WORKFLOW_OVERRIDE': 'VAPP', 'MANAGE_HARD_DISKS': 'VAPP', 'ASSIGN_LOADBALANCERS': 'VAPP', 'ASSIGN_FIREWALLS': 'VAPP', 'APPLIB_VM_COST_CODE': 'PRICING'}

	privlabels = {}
	privnames = {}
	privdescs = {}
	privgroups = {}
	UIlabelfile = 'lang_en_US_labels.json'
	(privlabels,privnames,privdescs,privgroups) = get_gui_labels(input_gitdir,UIlabelfile)


	output_file_name = 'wiki_privileges_2014-10-21.txt'
	out_file = open(os.path.join(output_subdir,output_file_name), 'w')

	pgkeys = collections.OrderedDict()
	plkeys = collections.OrderedDict()
	pgkeys = sorted(grouporder.keys())	 
	plkeys = sorted(privlabels.keys())

	privjson = {}
	privcatlist = []
	privlist = []

	entries = []
	categories = []
	
	for pgk in pgkeys:
		pgkordered = grouporder[pgk]
		current_group = groupmatch[pgkordered]
		privgroupindexed = privgroups[pgkordered]

		category = {}

		# write a header
		category["category"]=	privgroupindexed
		category["roleheaders"] = rheaders


		for plk_orig in plkeys:
			plk = getCategory(plk_orig)

			if current_group == plk:			
				# create a privilege data object
				priv_desc = privdescs[plk_orig]
				if plk_orig in extratext:
					priv_desc = priv_desc + extratext[plk_orig])   
				roleslist = []
				for ro in rollers:
					if ro in sqlroles[plk_orig]:
						roleslist.append(ro)
				info = ""
				privo = priv(current_group,privnames[plk_orig],plk_orig,privdescs,roleslist,info)

				# create a privilege json
				privi = {}
				privi["guiLabel"] = privo.pGuiLabel
				privi["appTag"] = privo.pAppTag
				privi["privilege"] = privo.pPrivilege
				for rx in rollers:
					rolex = {}
					rolex["roleformat"] = rollers[rx].rformat
					if rx in privo.pRoles:
						rolex["rolehas"] = "X"
					privi["roles"].append(rolex) 
				privi["info"] = {}	

				# add the entry to the list of entries for the category
				entries.append(privi)

		category["category"] = entries
		categories.append(category)
	privilout = {}
	privilout["categories"] = categories

	# write a json file with the privileges for the mustache render
	js = open_if_not_existing("cats.json")
	if js:
		json.dump(privilout, js)
		js.close

	# do the mustache render
	mustacheTemplate = codecs.open("wiki_privileges_template.mustache", 'r', 'utf-8').read()
	efo = pystache.render(mustacheTemplate, privilout).encode('utf8', 'xmlcharrefreplace')
	ef = open_if_not_existing("privileges_out.txt")
	if ef:
		ef.write(efo)
		ef.close()	  

  
# Calls the main() function
if __name__ == '__main__':
  main()
