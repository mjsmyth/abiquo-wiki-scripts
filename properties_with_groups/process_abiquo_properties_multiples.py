#!/usr/bin/python2 -tt
#
# This script processes the Developers' properties file from github and uses a mustache template to create 
# a table in Confluence storage format for the Abiquo wiki. Delete existing the table, then go into storage 
# format editor
#
# It also creates four sample abiquo.properties files for the main platform servers 
# (at the time of writing: API, OA, RS and V2V)
# It supports group property descriptions
# Edit this file to set the date for the filenames. 
# Note that the images used in the  have a date from when they were created

import sys
import os
import json
import re
import collections
import pystache
import codecs
from copy import deepcopy

class filedetails:
	def __init__(self,aprefix,asuffix,adate,aiprefix,aisuffix):
		self.fprefix = aprefix
		self.fsuffix = asuffix
		self.fdate = adate
		self.iprefix = aiprefix
		self.isuffix = aisuffix

class prop:
	def __init__(self,apropName,apropProfiles,apropType,apropDescription,apropDefault,apropRange,apropEndings,apropGroupName):
		self.pName = apropName
		self.pDefault = apropDefault
		self.pDescription = apropDescription
		self.pRange = apropRange
		self.pProfiles = apropProfiles
		self.pType = apropType
		self.pEndings = apropEndings
		self.pGroupPropName = apropGroupName
		
	
	def pprint(self):
		prProfiles = " ".join(self.pProfiles)
		iEndings = [x[0] for x in self.pEndings]
		prEndings = " ".join(iEndings)
		iDefaults = [x[1] for x in self.pEndings]
		prDefaults = " ".join(iDefaults)
		print "| %s | %s | %s | %s | %s | %s | %s | %s |" % (self.pName,self.pDefault,self.pRange,self.pDescription,prProfiles,self.pType,prEndings,prDefaults)

def checkEqual1(iterator):
	try:
		iterator = iter(iterator)
		first = next(iterator)
		return all(first == rest for rest in iterator)
	except StopIteration:
		return True

def open_if_not_existing(filename):
	try:
		fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
	except:
		print ("File: %s already exists" % filename)
		return None
	fobj = os.fdopen(fd, "w")
	return fobj

def tree(): return collections.defaultdict(tree)

def wikiHeadings(profiles,filedetails):
	heading_links_list = []
	for prix, profile in profiles.items():
		header_profile_item = {}
		header_profile_item['ExampleFile'] = filedetails.fprefix + profile.lower() + "_" + filedetails.fdate + filedetails.fsuffix
		header_profile_item['ExampleImage'] = filedetails.iprefix + profile.lower() + filedetails.isuffix
		heading_links_list.append(header_profile_item)
	return heading_links_list

def getEnding(propNameSplit):
	property_end = propNameSplit[-1]		
	return property_end

def getCategory(propNameSplit):
	prop_cat = propNameSplit
	try: 
		property_cat = propNameSplit[1]
	except IndexError, e:
		property_cat = ""	 
	if prop_cat[0] == "workflow":
		property_cat = "workflow"
	if prop_cat[0] == "com":
		property_cat = "virtualfactory"
	if property_cat == "stale":
		property_cat = "stale sessions"
	if property_cat == "dvs":
		property_cat = "dvs and vcenter"
	if property_cat == "vi":
		property_cat = "virtual infrastructure"		
	if property_cat == "USE_SECURE_CHANNEL_LOGIN":
		property_cat = "client"
	if property_cat == "vi":
		property_cat = "virtual infrastructure"
	if property_cat == "m":
		property_cat == "m outbound api"	
	if property_cat == "pcrsyncpool":
		property_cat = "pcrsync"					
	return property_cat


def storeGroupProperty(propeName,propeDefault,propeType,propeNameList,propeEndingList):
# process multiple properties:
	# before calling this function test - if property_name: 
	# if a property name is set before we assign it in this function, then we know it's a group property
	# add it to a property name list
	# here we are really processing the previous item
	# put the names into an informal list for checking
	# note that we store mandatory/optional type here too
	propeNameList.append(propeName)
	# for the group, store a list of all the endings and their defaults and whether they are mandatory or not
	prop_split = propeName.split(".")
	prop_end = getEnding(prop_split)
	prop_End_Def = (prop_end,propeDefault,propeType)
	propeEndingList.append(prop_End_Def)
	return(propeNameList,propeEndingList)

def subPropertyDefault(rawDefault,rawName):
#	if re.search(r"{",rawDefault):
#		rawDefault = re.sub(r"{",r"\{",rawDefault) 
	if rawName == "abiquo.datacenter.id":
		rawDefault = re.sub("default","Abiquo",rawDefault)
	if rawName == "abiquo.kairosdb.host":
		rawDefault = re.sub("127.0.0.1","<KairosdbLoc>",rawDefault)	
	rawDefault = re.sub("127.0.0.1",r"<IP-repoLoc>",rawDefault)
	rawDefault = re.sub("localhost",r"127.0.0.1",rawDefault)
	rawDefault = re.sub("10.60.1.4",r"127.0.0.1",rawDefault);
	return rawDefault

def storeProperty(propeMatch,propeName,propeDefault,propeNameList):		
	# Process the current line
	# the first group is the property name
	propeName = propeMatch.group(1)
	# Check that it matches the previous group names
	proper_split = propeName.split(".")
	property_split = ".".join(proper_split[:-1])
	if propeNameList:
		if not re.match(property_split,propeNameList[-1]):
			print ("Error: property does not match group")
	# the fourth group, if it exists, is the property default value
	if propeMatch.group(4):
		propeDefault = propeMatch.group(4).strip()
		propeDefault = subPropertyDefault(propeDefault,propeName)
	else:
		propeDefault = ""
	return(propeName,propeDefault)				


def wikiProperty(rawProp,profiles,filedetails):
	# Create JSON for printing with mustache
	property_entry = {}
	property_entry['propertyName'] = rawProp.pName
	property_entry['propertyDefault'] = rawProp.pDefault
	property_entry['propertyRange'] = rawProp.pRange
	property_entry['propertyDescription'] = rawProp.pDescription
	property_entry['propertyProfiles'] = []
	
	for prix, profile in profiles.items():
		property_profile_item = {}
		property_profile_item['profile'] = {}
		if profile in rawProp.pProfiles:
			property_profile_item['profile']['profileExampleFile'] = filedetails.fprefix + profile.lower() + filedetails.fdate + filedetails.fsuffix
			property_profile_item['profile']['profileExampleImage'] = filedetails.iprefix + profile.lower() + filedetails.isuffix	
		property_entry['propertyProfiles'].append(property_profile_item.copy())	

	property_entry['propertyNameGroup'] = {}
	property_entry['propertyDefaultGroup'] = {}
	propGroupName = rawProp.pGroupPropName
	property_entry['groupPropertyName'] = rawProp.pGroupPropName

	if rawProp.pEndings:
		property_pre_entry = {}
		property_pre_entry_default = {}

		property_pre_entry['propertyGroups'] = []
		property_pre_entry_default['propertyGroupDefaults'] = []

		property_multiple_item = {}
		property_multiple_item_default = {}

		default_list = []

		for chkequal in rawProp.pEndings:
			default_list.append(chkequal[1])
		vale = checkEqual1(default_list)
		if vale == True:
			b = default_list.pop()
			property_entry['propertyDefault'] = b
		else:
			property_entry['propertyDefault'] = ""	

		for x in rawProp.pEndings:
			try:
				property_multiple_item['propertyGroupItem'] = x[0]
				property_pre_entry['propertyGroups'].append(property_multiple_item.copy())
			except:
				property_multiple_item['propertyGroupItem'] = ""
				property_pre_entry['propertyGroups'].append(property_multiple_item.copy())
			if property_entry['propertyDefault'] == "":	
				try:			
					property_multiple_item_default['propertyGroupItemName'] = x[0]
					property_multiple_item_default['propertyGroupItemDefault'] = x[1]
					property_pre_entry_default['propertyGroupDefaults'].append(property_multiple_item_default.copy())
				except:
					property_multiple_item_default['propertyGroupItemName'] = x[0]
					property_multiple_item_default['propertyGroupItemDefault'] = ""
					property_pre_entry_default['propertyGroupDefaults'].append(property_multiple_item_default.copy())
		
		property_entry['propertyNameGroup'] = property_pre_entry.copy()		
		if property_entry['propertyDefault'] == "":			
			property_entry['propertyDefaultGroup'] = property_pre_entry_default.copy()
		else:	
			property_entry['propertyDefaultGroup'] = []	
	return property_entry

def wikiCategories(storage_dict):
	# categories for headers on the wiki (e.g. vsm)
	catkeydict = {}
	catkeys = {}
	catkeyorder = collections.OrderedDict()
	catdata = collections.OrderedDict()
	catkeydict = collections.OrderedDict()
	# sort properties by names in lower case
	for prop in sorted(storage_dict,key=lambda s: s.lower()):
		# create a dictionary of property names : categories
		pn = storage_dict[prop]['propertyName']
		prop_split = pn.split(".")
		property_category = getCategory(prop_split)
		catkeydict[pn] = property_category
	# from the above dictionary, go through the categories and make them the key to a new dictionary that stores the whole property
	for v,k in catkeydict.items(): 
		if k in catkeyorder:
			catkeyorder[k].append(storage_dict[v])
		else:
			catTemp = storage_dict[v]
			print "Hello catTemp %s" % catTemp
			catTemp['linkCategory'] = True	
			catkeyorder[k] = [catTemp]	
#			catkeyorder[k] = [storage_dict[v]]				
	catdata = [{'categoryName':k, 'entries':v} for k,v in (catkeyorder.items())]
	return catdata

def getSampleMessage(profile,version):
	# return a sample message for the sample files
	profile_print_info = {}
	profile_print_info["API"] = "API / SERVER / UI"
	profile_print_info["V2V"] = "V2V (REMOTE SERVICES)"
	profile_print_info["RS"] = "REMOTE SERVICES"
	profile_print_info["OA"] = "OUTBOUND API"
	sampleMessage = []
	swPrintStars = "################################################################################\n"
	swPrintIntro = "#### This is a sample abiquo.properties file for "  
	swPrintEnd =   "            ####\n"	
	swPrintLine = swPrintIntro + profile_print_info[profile] + swPrintEnd 
	sampleMessage.append(swPrintStars)
	sampleMessage.append(swPrintLine)
	sampleMessage.append(swPrintStars)
	return sampleMessage

def compileSampleProperty(pro_name,pro_default,pro_type):
	# eliminate repeated code
	if pro_type == "mandatory":	
		sam_property = pro_name + " = " + pro_default + "\n"	
	else:	
		sam_property = "#" + pro_name + " = " + pro_default + "\n"	
	return sam_property	


def storeProperties(content,property_regex_comment,property_regex_no_comment,range_regex,range_regex_bracket,profiles,fdetails,sample_files):
	# process the property file content
	wiki_property_dict = {}
	property_profiles = []
	property_description_list = []
	property_ending_list = []
	property_name_list = []
	property_name = "" 
	property_description = ""
	property_type = ""
	property_default = ""
	property_range = ""
	property_group = ""
#	property_count = 0
	group_property_name = ""


	for property_line in content:
		# a blank line may mark the end of a property
		if re.match("\n", property_line):
			if property_name:
				if property_ending_list:
					(property_name_list,property_ending_list) = storeGroupProperty(property_name,property_default,property_type,property_name_list,property_ending_list)
					
				# create a sample_files dictionary organised by profile names
				# sample file is similar to the main input file but it only contains properties of one profile
				for pro in property_profiles:
					sample_property = ""
					if pro in sample_files:
						for pd in property_description_list:
							pk = "# " + pd + "\n"
							sample_files[pro].append(pk)
					else:
						sample_files[pro] = []	
						for pd in property_description_list:
							pk = "# " + pd + "\n"							
							sample_files[pro].append(pk)
											
					# if there's a group, process each property with default and type
					if property_ending_list:
#						print "property_ending_list: %s" % property_ending_list[:]
						pnlist = property_name.split(".")
						pnfront = ".".join(pnlist[:-1])
						for ending_item in property_ending_list:
							pna = pnfront + "." + deepcopy(ending_item[0])
							pde = deepcopy(ending_item[1]) 
							pma = deepcopy(ending_item[2])
							sam_property = compileSampleProperty(pna,pde,pma)
							sample_files[pro].append((sam_property))
					else:
						sample_property = compileSampleProperty(property_name,property_default,property_type)
						sample_files[pro].append(sample_property)	
					sample_files[pro].append(("\n"))		


				# prepare for wiki				
					property_description = " ".join(property_description_list)	
		#			re.sub('^#','',property_description)		
		#			search for Range: x-x type info in wiki properties and store it separately
					property_range_search = range_regex.search(property_description)
					if property_range_search:
						property_range = property_range_search.group(2) 
						property_description = re.sub(property_range_search.group(0),"",property_description)
					# Support Albert's Range [x, y, z] format	
					property_range_search_bracket = range_regex_bracket.search(property_description)
					if property_range_search_bracket:
#						rep_string = property_range_search_bracket.group(0)
		#				print "property_description before: %s " % property_description 
						property_range = property_range_search_bracket.group(2) 
						property_description = property_description.replace(property_range_search_bracket.group(0),"")
		#				print "property_description after: %s " % property_description

#					print "property description NOW: %s" % str(property_description)
					# check for "for each XXXX (YY)", create a group property name with (YY) on the end

					# This currently works for any kind of braces (not square brackets) 
					# But when I get a chance to modify the file, I will remove all except curly braces
					property_multiple_search_braces = re.search('for each.*?\{([^}]+?)\}',property_description)
					property_multiple_search = re.search('for each.*?\(([^)]+?)\)',property_description)
					property_multiple_search_angles = re.search('for each.*?\<([^>]+?)\>',property_description)

					if property_multiple_search_braces:
						property_multiple_braces = "{" + property_multiple_search_braces.group(1) + "}"
#						print "property_multiple_braces: %s" % property_multiple_braces
						pnam_work = property_name.split(".")
						pnam_work = pnam_work[:-1]
						pnam_work.append(deepcopy(property_multiple_braces))
						group_property_name = ".".join(pnam_work)
#						print "multiple_name_angles: %s" % group_property_name
						group_property_name = deepcopy(group_property_name)
					elif property_multiple_search:	
						property_multiple_plain = "{" + property_multiple_search.group(1) + "}"
#						print "property_multiple: %s" % property_multiple_plain
						pnam_work = property_name.split(".")
						pnam_work = pnam_work[:-1]
						pnam_work.append(deepcopy(property_multiple_plain))
						group_property_name = ".".join(pnam_work)
#						print "multiple_name: %s" % group_property_name
						group_property_name = deepcopy(group_property_name)
					elif property_multiple_search_angles:
						property_multiple_angles = "{" + property_multiple_search_angles.group(1) + "}"
#						print "property_multiple_angles: %s" % property_multiple_angles
						pnam_work = property_name.split(".")
						pnam_work = pnam_work[:-1]
						pnam_work.append(deepcopy(property_multiple_angles))
						group_property_name = ".".join(pnam_work)
#						print "multiple_name_angles: %s" % group_property_name
						group_property_name = deepcopy(group_property_name)
						group_property_name = ""
					else:
						group_property_name = ""

#					group_property_name = "" + group_property_name_plain + group_property_name_braces + group_property_name_angles
					aproperty = prop(property_name,property_profiles,property_type,property_description,property_default,property_range,property_ending_list,group_property_name)
#					aproperty.pprint()
					property_wiki = wikiProperty(aproperty,profiles,fdetails)		
					wiki_property_dict[property_name] = property_wiki.copy()


			del property_description_list [:]
			# property endings are, for example, [vmx_04,hyperv_301]			
			del property_ending_list [:]
			del property_name_list [:]	
			property_name = "" 
			property_description = ""
			property_type = ""
			property_default = ""
			property_range = ""
			# property group is, for example, (HV)			
			property_group = ""
			property_count = 0


		# if there is a commented out line
		elif re.match("#",property_line):
			# Lots of hashes means a server profile specification
			if re.match("#####",property_line):
#				print "matched profiles"
				del property_profiles [:]
				# Multiple profiles comment is for users editing the file
				if re.search("MULTIPLE PROFILES",property_line):
					continue
				# set up the profiles for this section of properties	
				else:
					for profile in profiles:
						if re.search(profile,property_line):
							property_profiles.append(profiles[profile])

			else:
			# 	search for a property name and optional default value
				property_match_comment = property_regex_comment.match(property_line)
				if property_match_comment:
					property_type = "optional"
					# this is an optional property that is commented out.
					# now substitute and make it effectively a "mandatory property" in order to use same indices, etc.
					property_line = re.sub("^#[\s]*?","",property_line)

					property_match = property_regex_no_comment.match(property_line)
					if property_match:
						if property_name:
					# if property_name:
					# 	# if the property name is set before we assign it in this loop, then we know it's a group property
					# 	# store a list of all names and store a list of all endings and defaults
							(property_name_list,property_ending_list) = storeGroupProperty(property_name,property_default,property_type,property_name_list,property_ending_list)
						
						(property_name,property_default) = storeProperty(property_match,property_name,property_default,property_name_list)							
				else:	
					#	add property description to a list
						property_description_current_line = property_line[len(property_ending_list):].strip()
						property_description_current_line = (re.sub("^#[\s]*?"," ",property_description_current_line))	
						property_description_current_line = property_description_current_line.strip()
						property_description_list.append(property_description_current_line)
#						property_description_list.append(re.sub("^#[\s]*?"," ",property_description_current_line))	
		else:	
#			mandatory property name and optional default value, commented out - note may have space after comment
			property_match = property_regex_no_comment.match(property_line)
			if property_match:
				property_type = "mandatory"			
				property_match_no_comment = property_regex_no_comment.match(property_line)
				if property_match_no_comment:
					if property_name:
					# if property_name:
					# 	# if the property name is set before we assign it in this loop, then we know it's a group property
					# 	# store a list of all names and store a list of all endings and defaults
						(property_name_list,property_ending_list) = storeGroupProperty(property_name,property_default,property_type,property_name_list,property_ending_list)
						
					(property_name,property_default) = storeProperty(property_match,property_name,property_default,property_name_list)			

	return (wiki_property_dict,sample_files)		


def main():

	sample_files = {}
	wiki_output = {}
	categories = []

	# prevWikiVersion = "ABI32"
	wikiVersion = "ABI38"
	# # Directories and file names

 #    input_subdir = 'input_files'
 #    output_subdir = 'output_files'

 #    compFile = prevWikiVersion + output_subdir
    # inputDir = wikiVersion + "/" + input_subdir
    # outputDir = wikiVersion + "/" + output_subdir
	td = "2016-09-28"

#    inputDir = '~/platform/system-properties/src/main/resources'
	propertyFile = 'abiquo.properties_' + td

    
	# These are the details of the sample files and the images that link to the sample files on the wiki
	filePrefix = "properties_"
	fileSuffix = ".txt"
	imagePrefix = "v26_symbol_"
	imageSuffix = "_transparent.png"
	fdetails = filedetails(filePrefix,fileSuffix,td,imagePrefix,imageSuffix)

	property_description_list = []
#	property_regex_multiple = re.compile('for each',re.S)
	property_regex_comment = re.compile('([#]{1,1})([\s]*?)([\w.\-]+?)([\s]*)([=]{1,1})(.*)',re.S)

	property_regex_no_comment = re.compile('([\w.\-]+?)([\s]*?)([=]{1,1})(.*)',re.S)
	range_regex = re.compile('(Range:[\s]*?)([\w\-\,\s\<\>\.]*)')
	range_regex_bracket = re.compile('(Range[\s]*?[[])([^\]]*?)[\]]')
	storage_dict = {}

	profiles = collections.OrderedDict()
	profiles["SERVER"] = "API"
	profiles["REMOTESERVICE"] = "RS"
	profiles["V2VSERVICES"] = "V2V"
	profiles["M OUTBOUND API"] ="OA"

	# Read git properties file line by line
#	with codecs.open(os.path.json(inputDir,propertyFile), 'r', 'utf-8') as f:
	with codecs.open(propertyFile, 'r', 'utf-8') as f:
		content = f.readlines()
	# Prepare the properties for wiki output and sample files	
	(storage_dict,sample_files) = storeProperties(content,property_regex_comment,property_regex_no_comment,range_regex,range_regex_bracket,profiles,fdetails,sample_files)

	# Reorganise the storage dict by categories for the wiki
	categories = wikiCategories(storage_dict)

	# output the sample files
	for pf in profiles:
		pf_sample = fdetails.fprefix + profiles[pf].lower() + "_" + fdetails.fdate + fdetails.fsuffix	
		ps = open_if_not_existing(pf_sample)
		if ps:
			sample_message_list = getSampleMessage(profiles[pf],wikiVersion)
			for sw in sample_message_list:
				ps.write(sw)
			ps.write("\n")
			for pl in sample_files[profiles[pf]]:
				ps.write(pl.encode('utf8'))
			ps.close

	# output a storage dict with the properties indexed by property name		
	js = open_if_not_existing("fwg.json." + td)
	if js:
		json.dump(storage_dict, js)
		js.close

	# prepare the json dict for mustache output	
	wiki_output['headingLinks'] = wikiHeadings(profiles,fdetails)			
	wiki_output['categories'] = categories		

	# output a json file with the full mustache format
	jwf = open_if_not_existing("fwp.json." + td)
	if jwf:
		json.dump(wiki_output, jwf)
		jwf.close
	#tfilepath = os.path.join(adminSubdir,template)
	
	# Render the wiki file with mustache
	mustacheTemplate = codecs.open("wiki_properties_template_multiples.mustache", 'r', 'utf-8').read()
	efo = pystache.render(mustacheTemplate, wiki_output).encode('utf8', 'xmlcharrefreplace')
	pof = "properties_out_" + td + ".txt"
	ef = open_if_not_existing(pof)
	if ef:
		ef.write(efo)
		ef.close()		


# Calls the main() function
if __name__ == '__main__':
	main()
