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
		

def wikiProperty(rawProp,profiles,filedetails):
	property_entry = {}
	property_entry['propertyName'] = rawProp.pName
	property_entry['propertyDefault'] = rawProp.pDefault
	property_entry['propertyRange'] = rawProp.pRange
	property_entry['propertyDescription'] = rawProp.pDescription
	property_entry['propertyProfiles'] = []
	prtCategories = " ".join(rawProp.pProfiles)
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

def main():
	# Read git properties file line by line
#	codecs.open("wiki_properties_template.mustache", 'r', 'utf-8').read()
	with codecs.open("abiquo.properties.txt", 'r', 'utf-8') as f:
		content = f.readlines()

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
	
	property_regex_comment = re.compile('([#])?([\s]*)([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)')
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
	profiles = {"SERVER": "API","REMOTESERVICE": "RS","V2VSERVICES": "V2V","M OUTBOUND API":"OA"}

	for ix, property_line in enumerate(content):
		# a blank line may mark the end of a property
		if re.match("\n", property_line):
#			print "space line"
				del property_description_list [:]
#			property_description_list = []
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
	#				if re.search(r'.',property_match):
#					print "matched an optional property"
					property_type = "optional"
					# the first group is the property name
					property_name = property_match.group(3)
					# the third group, if it exists, is the property default value
					if property_match.group(7):
#						print property_match.group(5)
						property_default = property_match.group(7)
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
			aproperty.pprint()
			property_wiki = wikiProperty(aproperty,profiles,fdetails)
			
			wiki_property_dict[property_name] = property_wiki.copy()

			property_category_list = property_name.split(".")
			if property_category_list[1]:
#				print ("property_category_list: %s " % property_category_list[1])
				property_category = property_category_list[1][:]
	
			if not last_category:
#				print ("first run: %s" % property_category[:])
				last_category = property_category[:]
				# first run - create a new entry
				pwcopy = property_wiki.copy()
				category_entries.append(pwcopy)
			elif last_category == property_category:
#				print ("Matched category: %s " % property_category)
				# accumulate entries until end of category
#				category_entries.append(property_wiki)
				pwcopy = property_wiki.copy()
				category_entries.append(pwcopy)
				property_category_main = property_category[:]
			else:
#				print ("New category: %s" % property_category)
				# append category to categories
				category['categoryName'] = last_category[:]
				category['entries'] = category_entries[:]

				catcopy = category.copy()
				if catcopy:
					categories.append(catcopy)
				# start new category
					del category_entries[:]
				# append existing entry to category
				if property_wiki:
#					print ("Adding to category_entries: %s " % property_wiki['propertyName'])
					pwcopy = property_wiki.copy()
					category_entries.append(pwcopy)
#					category_entries.append(property_wiki)
				# reset the last category
					last_category = property_category[:]
					property_category_main = property_category[:]
	print ("last_category: %s " % last_category)
	print ("property_category_main: %s " % property_category_main)				
	
	category['categoryName'] = last_category[:]
	category['entries'] = category_entries[:]
	catcopy = category.copy()
	if catcopy:
		categories.append(catcopy)
#
	wiki_output['headingLinks'] = wikiHeadings(profiles,fdetails)			
	wiki_output['categories'] = categories[:]		

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