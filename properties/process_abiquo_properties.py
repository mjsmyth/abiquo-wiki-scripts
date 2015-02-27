#!/usr/bin/python2 -tt
import sys
import os
import json
import re
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

class prop:
	def __init__(self,apropName,apropProfiles,apropType,apropDescription,apropDefault,apropRange):
		self.pName = apropName
		self.pDefault = apropDefault
		self.pDescription = apropDescription
		self.pRange = apropRange
		self.pProfiles = apropProfiles
		self.pType = apropType
		
	
	def pprint(self):
		prProfiles = " ".join(self.pProfiles)
		print "| %s | %s | %s | %s | %s | %s |" % (self.pName,self.pDefault,self.pRange,self.pDescription,prProfiles,self.pType)

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
	for prix, profile in profiles.viewitems():
#		print "prix %s profile %s " % (prix, profile)
		header_profile_item = {}
		header_profile_item['ExampleFile'] = filedetails.fprefix + profile.lower() + filedetails.fdate + filedetails.fsuffix
		header_profile_item['ExampleImage'] = filedetails.iprefix + profile.lower() + filedetails.isuffix
		heading_links_list.append(header_profile_item)
	return heading_links_list
		

def getCategory(pName):
	prop_cat = pName.split(".")
	property_cat = prop_cat[1]
	return property_cat

def wikiProperty(rawProp,profiles,filedetails):
	property_entry = {}
	property_entry['propertyName'] = rawProp.pName
	property_entry['propertyDefault'] = rawProp.pDefault
	property_entry['propertyRange'] = rawProp.pRange
	property_entry['propertyDescription'] = rawProp.pDescription
	property_entry['propertyProfiles'] = []
#	prtProfiles = " ".join(rawProp.pProfiles)
#	print ("categories: %s" % prtCategories) 
	for prix, profile in profiles.viewitems():
#		print "prix %s profile %s " % (prix, profile)
		property_profile_item = {}
		property_profile_item['profile'] = {}
		if profile in rawProp.pProfiles:
#			print ("Found profile: %s " % profile)
			property_profile_item['profile']['profileExampleFile'] = filedetails.fprefix + profile.lower() + filedetails.fdate + filedetails.fsuffix
			property_profile_item['profile']['profileExampleImage'] = filedetails.iprefix + profile.lower() + filedetails.isuffix	
		property_entry['propertyProfiles'].append(property_profile_item.copy())	
	return property_entry


def wikiCategories(storage_dict):
	catkeydict = {}
	catkeys = {}
	catkeyorder = collections.OrderedDict()
	catdata = collections.OrderedDict()
	catkeydict = collections.OrderedDict()

	for prop in sorted(storage_dict,key=lambda s: s.lower()):
#		print ("prop: %s" % prop)
		pn = storage_dict[prop]['propertyName']
		property_category = getCategory(pn)
		catkeydict[pn] = property_category
	# build a list of categories and property names
	for v,k in catkeydict.items(): 
		if k in catkeyorder:
			catkeyorder[k].append(storage_dict[v])
		else:
			catkeyorder[k] = [storage_dict[v]]				
	catdata = [{'categoryName':k, 'entries':v} for k,v in (catkeyorder.items())]
	return catdata

	

def storeProperties(content,property_regex_comment,property_regex_no_comment,range_regex,profiles,fdetails):
	wiki_property_dict = {}
	property_profiles = []
	property_description_list = []
	property_name = "" 
	property_description = ""
	property_type = ""
	property_default = ""
	property_range = ""

	for property_line in content:

		# a blank line may mark the end of a property
		if re.match("\n", property_line):
#			print "space line"
			del property_description_list [:]
 	#		property_description_list = []
			property_name = "" 
			property_description = ""
			property_type = ""
			property_default = ""
			property_range = ""
	
		# if you get a comment line
		elif re.match("#",property_line):
#			print "matched comment"
#			print  property_line
			# Lots of hashes means a server specification
			if re.match("#####",property_line):
#				print "matched profiles"
				del property_profiles [:]
#				property_profiles = []
				# Multiple profiles is for users editing the file
				if re.search("MULTIPLE PROFILES",property_line):
					continue
				# set up the profiles for this section of properties	
				else:
					for profile in profiles:
						if re.search(profile,property_line):
							property_profiles.append(profiles[profile])
			else:
			# 	search for a property name and optional default value
#				property_match = re.search("([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)",property_line)
				property_match = property_regex_comment.match(property_line)
				if property_match:
					property_type = "optional"
					# the third group is the property name
					property_name = property_match.group(2)
					print ("Optional prop: %s" % property_name)
					# the third group, if it exists, is the property default value
					if property_match.group(6):
						property_default = property_match.group(6)
					else:
						property_default = ""	
#					print "property name: %s" % property_name	
				else:	
	#				print "property description added"
	#				print "property_line 1: %s " % property_line[1:]
					property_description_list.append(property_line[1:].strip()) 
		else:	
#			mandatory property name and optional default value
#			property_match = re.search("([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)",property_line)
			property_match = property_regex_no_comment.match(property_line)
			if property_match:
			#	if re.search(r'.',property_match):
#				print "matched a mandatory property"
				property_type = "mandatory"
				# the first group is the property name
				property_name = property_match.group(1)
				print ("Mandatory prop: %s " % property_name)
				# the fourth group, if it exists, is the property default value
				if property_match.group(5):
#					print property_match.group(5)
					property_default = property_match.group(5)
				else:
					property_default = ""	
#				print property_name
		property_category = ""
		if property_name:				
			property_description = " ".join(property_description_list)			
#			property_range_search = re.search("(Range:[\s]*?)(.*)",property_description)
			property_range_search = range_regex.search(property_description)
			if property_range_search:
				property_range = property_range_search.group(2) 
				property_description = re.sub(property_range_search.group(0),"",property_description)
			aproperty = prop(property_name,property_profiles,property_type,property_description,property_default,property_range)
#			aproperty.pprint()
			property_wiki = wikiProperty(aproperty,profiles,fdetails)		
			wiki_property_dict[property_name] = property_wiki.copy()
	return wiki_property_dict		


def main():
	# Read git properties file line by line
#	codecs.open("wiki_properties_template.mustache", 'r', 'utf-8').read()

	wiki_output = {}
	categories = []
	category = {}
	last_category = ""
	property_category_main = ""
	category_entries = []	

	fileDate = "_2015-03-30"
	filePrefix = "properties_"
	fileSuffix = ".txt"
	imagePrefix = "v26_symbol_"
	imageSuffix = "_transparent.png"
	fdetails = filedetails(filePrefix,fileSuffix,fileDate,imagePrefix,imageSuffix)

	property_description_list = []
	
	property_regex_comment = re.compile('([#]{1,1})([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)')
	property_regex_no_comment = re.compile('([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)')
	range_regex = re.compile('(Range:[\s]*?)(.*)')
	property_name = ""
	property_profiles = []
	property_description = ""
	property_type = ""
	property_default = ""
	property_range = ""
	property_wiki = {}
	wiki_property_dict = {}

	storage_dict = {}

	profiles = {"SERVER": "API","REMOTESERVICE": "RS","V2VSERVICES": "V2V","M OUTBOUND API":"OA"}

	with codecs.open("abiquo.properties.txt", 'r', 'utf-8') as f:
		content = f.readlines()

	storage_dict = storeProperties(content,property_regex_comment,property_regex_no_comment,range_regex,profiles,fdetails)
	
	categories = wikiCategories(storage_dict)

	js = open_if_not_existing("stg.json")
	# dump json
	if js:
		json.dump(storage_dict, js)
		js.close
# 
	
#
	wiki_output['headingLinks'] = wikiHeadings(profiles,fdetails)			
	wiki_output['categories'] = categories		

#	fwp = os.path.join(sbdir,filename)
	jwf = open_if_not_existing("fwp.json")
	# dump json
	if jwf:
		json.dump(wiki_output, jwf)
		jwf.close

	#tfilepath = os.path.join(adminSubdir,template)
	mustacheTemplate = codecs.open("wiki_properties_template.mustache", 'r', 'utf-8').read()
	efo = pystache.render(mustacheTemplate, wiki_output).encode('utf8', 'xmlcharrefreplace')
	ef = open_if_not_existing("properties_out.txt")
	if ef:
		ef.write(efo)
		ef.close()		

			
				# Use mustache
	# Create a table like in the wiki
	

	# Create a dictionary of properties
	# Ask user what server profile they have
	# Ask for IP address of server?
	# Read user properties file
	# Check it for extra spaces
	# Check for any properties that are unknown
	# Check for any values that are out of range

# Calls the main() function
if __name__ == '__main__':
	main()