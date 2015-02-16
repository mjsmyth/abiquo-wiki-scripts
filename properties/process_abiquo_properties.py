#!/usr/bin/python2 -tt
import re

# Read git properties file line by line

with open(abiquo.properties) as f:
	content = f.readlines()
property_type = []
comment = []

for property_line in content:
	if re.match("#",property_line):
		if re.match("#####",property_line):
			if re.search("MULTIPLE PROFILES",property_line):
				continue
			if re.search("SERVER",property_line):
				property_type.append("SERVER")
			if re.search("REMOTESERVICE",property_line):
				property_type.append("REMOTESERVICE",property_line)
			if re.search("V2VSERVICES",property_line):
				property_type.append("V2VSERVICES")
			if re.search("M OUTBOUND API",property_line):
				property_type.append("OUTBOUNDAPI")
		else:
	# 	Check for property name and value in an optional (commented property)
			if re.search("(\w"."+)("=")(\w)",property_type)
			# the first group is the property name
			# the third group, if it exists, is the property default value
			
			else:	
				comment.append(property_type[1:])
		
# Create a dictionary of properties
# Ask user what server profile they have
# Ask for IP address of server?
# Read user properties file
# Check it for extra spaces
# Check for any properties that are unknown
# Check for any values that are out of range
