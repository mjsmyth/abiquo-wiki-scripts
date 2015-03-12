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
	for sql_orig in sqllines:
		#print (sql_orig)
		sqllist = re.findall(r'([\w_]+)', sql_orig)
		sqllist_joinkey = sqllist[0] + "=" + sqllist[1]
		sqllabels[sqllist_joinkey] = sqllist[0]
		sqlroles[sqllist_joinkey] = sqllist[1]
	return (sqllabels,sqlroles)

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

def main():
	infoMarkNew = '<ac:emoticon ac:name="yellow-star"/>'
	infoMarkCha = '<ac:emoticon ac:name="warning"/>'
	infoMarkDep = '<ac:emoticon ac:name="minus"/>'

	infoNew = "N"
	infoCha = "C"
	infoDep = "D"

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

	(sqllabels,sqlroles) = get_sql(input_subdir,sqlfile)


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

    prioo = {}


	for pgk in pgkeys:
		pgkordered = grouporder[pgk]
		current_group = groupmatch[pgkordered]
		privgroupindexed = privgroups[pgkordered]

		for plk_orig in plkeys:
			plk = getCategory(plk_orig)
                # create a category json entry
                
			if current_group == plk:

                # create a privilege object

                # write a privilege json entry

				output_row = "<tr> \n <td> \n " + privnames[plk_orig] + "</td> \n <td> \n " + plk_orig + "</td> \n <td> \n " + privdescs[plk_orig] 
				out_file.write (output_row)
				privs_processed = privs_processed + 1
				#print (privnames[plk_orig],": ",privdescs[plk_orig])
				if plk_orig in extratext:
					out_file.write (". " + extratext[plk_orig])   
				out_file.write ("</td>\n")	
				key_cloud_admin = plk_orig + "=CLOUD_ADMIN"
				key_ent_admin = plk_orig + "=ENTERPRISE_ADMIN"
				key_user = plk_orig + "=USER"
				key_muser = plk_orig + "=OUTBOUND_API_EVENTS"
				outroles = {}
				oca = " "
				oea = " "
				oeu = " "
				omu = " "
				if key_cloud_admin in sqlroles:
					#print ("CLOUD_ADMIN")
					oca = "X"
				if key_ent_admin in sqlroles:
					#print ("ENT_ADMIN")  
					oea = "X"  
				if key_user in sqlroles:
					#print ("USER")				   
					oeu = "X"
				if key_muser in sqlroles:
					omu = "X"

				outroles[1] = "<td class=\"highlight warning\" data-highlight-class=\"warning\"> <p> " + oca + " </p> </td>\n"
				outroles[2] = "<td class=\"highlight note\" data-highlight-class=\"note\"> <p> " + oea + " </p> </td>\n"
				outroles[3] = "<td class=\"highlight success\" data-highlight-class=\"success\"> <p> " + oeu + " </p> </td> \n"
				outroles[4] = "<td class=\"highlight info\" data-highlight-class=\"info\"> <p> " + omu + " </p> </td> \n"
				outroles[5] = "<td > </td></tr>\n"
				#okeys = sorted(outroles.keys())
				#for okey in okeys:
				for okey in range (1, 6):
					out_file.write (outroles[okey])
	out_file.write ("</tbody>\n</table>\n")
	print("privs_processed: ",privs_processed)

	mustacheTemplate = codecs.open("wiki_privileges_template.mustache", 'r', 'utf-8').read()
	efo = pystache.render(mustacheTemplate, wiki_output).encode('utf8', 'xmlcharrefreplace')
	ef = open_if_not_existing("privileges_out.txt")
	if ef:
		ef.write(efo)
		ef.close()	  

	json_data.close()
	out_file.close()

		
  
# Calls the main() function
if __name__ == '__main__':
  main()
