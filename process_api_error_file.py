#!/usr/bin/python2 -tt
## Process the APIErrors including the error codes
## 
##

import sys
import re
import os
import requests

# DATACENTER.CREATE.addErrorkeys(new KEYS[] {KEYS.INITIATORIQN})),
# http.client.responses[http.client.my_status_code] 
# final HttpStatus status = HttpStatus.valueOf(statusCode);
# return status.toString().toUpperCase().replaceAll("\\s", "-"); 

def main():
	api_error_git_dir = "/home/mjsmyth/platform/api/src/main/java/com/abiquo/api/exceptions"
	api_error_file_raw = "APIError.java"
	RS="(Internal error code)|(AbiquoError)"

	# Read the whole file into a single string
	with open (os.path.join(api_error_git_dir,api_error_file_raw), "r") as aefile:
			aedata=aefile.read()

	# Split the file by the stuff at the top and bottom of the API error file			
	ae_main_records = re.split(RS,aedata)
	# Check this periodically to make sure that all the API errors are included
	# Select the bit with the error messages
	aero = ae_main_records[6]

	# Split the list on \n
	aero_physical_lines = aero.split("\n")

	# search for items with leading comments and add ******** to front and end of line
	for aerobit in aero_physical_lines:
		if re.search("^\s*//",aerobit):
			aerobit = "*******" + re.sub("^\s*//","",aerobit) + " *******"
			print aerobit
	# search for items with trailing comments and remove trailing comments
		if re.search("//\s*$",aerobit):
			aerobit = re.sub("//\s*$","",aerobit)
			print aerobit
		if re.search(";\s*$",aerobit):
			aerobit = re.sub(";\s*$",",",aerobit)
			print aerobit	
	# join the list again
	aero_whole = "".join(aero_physical_lines)
	
	# print aero_whole

	pp = convertstatuscode(300)
	print pp

def convertstatuscode(status_code):	
	# Convert status code into status code + status description
	headers = {'content-type': 'text/html'}
	httpstat_url = "http://httpstat.us/" 
	url_code = httpstat_url + str(status_code)
	r = requests.get(url_code, headers=headers)
	s = r.text.upper()
	s = re.sub("\s","-",s)
	return s


# Calls the main() function
if __name__ == '__main__':
	main()