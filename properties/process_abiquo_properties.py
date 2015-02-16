#!/usr/bin/python2 -tt
import re

class prop:
	def __init__(self,apropName,apropCategory,apropType,apropDescription,apropDefault):
		self.pName = apropName
		self.pCategory = apropCategory
		self.pType = apropType
		self.pDescription = apropDescription
		self.pDefault = apropDefault
	
	def pprint(self):
		prCategory = " ".join(self.pCategory)
		print "| %s | %s | %s | %s | %s |" % (self.pName,prCategory,self.pType,self.pDescription,self.pDefault)

class main():
	# Read git properties file line by line
	with open("abiquo.properties.txt") as f:
		content = f.readlines()

	for property_line in content:
		if re.match("\n", property_line):
			continue
		property_name = ""
		property_category = []
		property_description_list = []
		property_description = ""
		property_type = ""
		property_default = ""
	
		if re.match("#",property_line):
			if re.match("#####",property_line):
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
		# 	Check for property name and value in an optional (commented property)
				property_match = re.search("(\w\.+?)(=)(\w)",property_line)
				if property_match:
					property_type = "optional"
					# the first group is the property name
					property_name = property_match.group(1)
					# the third group, if it exists, is the property default value
					if property_match.group(3):
						property_default = property_match.group(3)
					else:
						property_default = ""	
				else:	
					property_description_list.append(property_type[1:])
		else:
			property_description = " ".join(property_description_list)			
#			property_match = re.search("(\w\.+)(\=)(\S+)",property_line)
			property_match = re.search("(\w\.+?)(=)(\w)",property_line)
			if property_match:
				property_type = "mandatory"
				# the first group is the property name
				property_name = property_match.group(1)
				# the third group, if it exists, is the property default value
				if property_match.group(3):
					property_default = property_match.group(3)
				else:
					property_default = ""	
		aproperty = prop(property_name,property_category,property_type,property_description,property_default)
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