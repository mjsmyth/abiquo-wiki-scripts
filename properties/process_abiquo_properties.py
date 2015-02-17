#!/usr/bin/python2 -tt
import re

class prop:
	def __init__(self,apropName,apropCategory,apropType,apropDescription,apropDefault,apropRange):
		self.pName = apropName
		self.pCategory = apropCategory
		self.pType = apropType
		self.pDescription = apropDescription
		self.pDefault = apropDefault
		self.pRange = apropRange
	
	def pprint(self):
		prCategory = " ".join(self.pCategory)
		print "| %s | %s | %s | %s | %s | %s |" % (self.pName,prCategory,self.pType,self.pDescription,self.pDefault,self.pRange)

class main():
	# Read git properties file line by line
	with open("abiquo.properties.txt") as f:
		content = f.readlines()
	
	property_description_list = []
	property_name = ""
	property_category = []
	property_description = ""
	property_type = ""
	property_default = ""
	property_range = ""

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
				property_category = []
				if re.search("MULTIPLE PROFILES",property_line):
					continue
				if re.search("SERVER",property_line):
					property_category.append("SERVER")
				if re.search("REMOTESERVICE",property_line):
					property_category.append("REMOTESERVICE")
				if re.search("V2VSERVICES",property_line):
					property_category.append("V2VSERVICES")
				if re.search("M OUTBOUND API",property_line):
					property_category.append("OUTBOUNDAPI")
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
			aproperty = prop(property_name,property_category,property_type,property_description,property_default,property_range)
			aproperty.pprint()
	
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