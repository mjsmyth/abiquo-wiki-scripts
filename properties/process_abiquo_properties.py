#!/usr/bin/python2 -tt
import sys
import json
import re
import collections

class filedetails:
	def __init__(self,aprefix,asuffix,adate,aiprefix,aisuffix):
		self.fprefix = aprefix
		self.fsuffix = asuffix
		self.fdate = adate
		self.iprefix = aiprefix
		self.isuffix = aisuffix

class prop:
	def __init__(self,apropName,apropCategories,apropType,apropDescription,apropDefault,apropRange):
		self.pName = apropName
		self.pDefault = apropDefault
		self.pDescription = apropDescription
		self.pRange = apropRange
		self.pCategories = apropCategories
		self.pType = apropType
		
	
	def pprint(self):
		prCategories = " ".join(self.pCategories)
		print "| %s | %s | %s | %s | %s | %s |" % (self.pName,self.pDefault,self.pRange,self.pDescription,prCategories,self.pType)


def tree(): return collections.defaultdict(tree)

def wikiProperty(rawProp,profiles,filedetails):
	property_entry['propertyName'] = rawProp.pName
	property_entry['propertyDefault'] = rawProp.pDefault
	property_entry['propertyRange'] = rawProp.pRange
	property_entry['propertyDescription'] = rawProp.pDescription
	property_entry['propertyProfiles'] = []

	fileName = filePrefix + "_"  + fileDate + "." + fileSuffix

	for profile in profiles:
		if profile in prCategories:
			property_profile_item = {}
			property_profile_item['profileExampleFile'] = filedetails.fprefix + filedetails.fdate + profile.lower() + filedetails.fsuffix
			property_profile_item['profileExampleImage'] = filedetails.iprefix + profile.lower + filedetails.isuffix
		else:
			property_profile_item = {}
			property_profile_item['profileExampleFile'] = ""
			property_profile_item['profileExampleImage'] = ""
		property_entry['propertyProfiles'].append(property_profile_item)	


def main():
	# Read git properties file line by line
	with open("abiquo.properties.txt") as f:
		content = f.readlines()
	
	fileDate = "_2015-03-31"
	filePrefix = "properties_"
	fileSuffix = ".txt"
	imagePrefix = "v26_symbol_"
	imageSuffix = "_transparent.png"
	fdetails = filedetails(fileDate,filePrefix,fileSuffix,imagePrefix,imageSuffix)

	property_description_list = []
	
	property_name = ""
	property_categories = []
	property_description = ""
	property_type = ""
	property_default = ""
	property_range = ""
	property_dict = tree()

	profiles = {"API": "SERVER","RS": "REMOTESERVICE","V2V": "V2VSERVICES","OA":"M OUTBOUND API"}

	for property_line in content:
		if re.match("\n", property_line):
#			print "space line"
			property_description_list = []
			property_name = ""
			property_description = ""
			property_type = ""
			property_default = ""
			property_range = ""
		
		elif re.match("#",property_line):
#			print "matched comment"
#			print  property_line
			if re.match("#####",property_line):
#				print "matched profiles"
				property_categories = []
				if re.search("MULTIPLE PROFILES",property_line):
					continue
				for profile in profiles:
					if re.search(profiles[profile],property_line):
						property_categories.append(profile)
			else:
#				print "no matched comment"
#				print property_line
				# 	search for a property name and optional default value
				property_match = re.search("([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)",property_line)
				if property_match:
#					print "matched an optional property"
					property_type = "optional"
					# the first group is the property name
					property_name = property_match.group(1)
					# the third group, if it exists, is the property default value
					if property_match.group(5):
#						print property_match.group(5)
						property_default = property_match.group(5)
					else:
						property_default = ""	
#					print "property name: %s" % property_name	
				else:	
#					print "property description added"
#					print "property_line 1: %s " % property_line[1:]
					property_description_list.append(property_line[1:].strip()) 
		else:	
#			search for a property name and optional default value
			property_match = re.search("([\w.]+?)([\s]*)([=]{1,1})([\s]*)([\S]*)",property_line)
			if property_match:
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
		if property_name:				
			property_description = " ".join(property_description_list)			
			property_range_search = re.search("(Range:[\s]*?)(.*)",property_description)
			if property_range_search:
				property_range = property_range_search.group(2) 
				property_description = re.sub(property_range_search.group(0),"",property_description)
			aproperty = prop(property_name,property_categories,property_type,property_description,property_default,property_range)

			aproperty.pprint()
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