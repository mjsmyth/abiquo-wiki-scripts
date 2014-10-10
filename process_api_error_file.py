#!/usr/bin/python2 -tt
## Process the APIErrors including the error codes
## 
##

import sys
import re
import os
import requests
import copy

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

	to_modify = {}
	for AEI, aeropl in enumerate(aero_physical_lines):
		aerobit = aeropl[:]
		# remove leading spaces, trailing spaces
		to_modify[AEI] = aerobit.strip()
	
		if AEI in to_modify.keys():
			aerobit = to_modify[AEI]

		# search for and remove leading comments and replace with header marks
		if re.search("^//",aerobit):
			to_modify[AEI] = "*******" + re.sub("^//","",aerobit) + " #######"

		if AEI in to_modify.keys():	
			aerobit = to_modify[AEI]

		# replace trailing comments	
		to_modify[AEI] = re.sub("//$","",aerobit)
		
		if AEI in to_modify.keys():	
			aerobit = to_modify[AEI]	
		# replace the semicolon at the end of the last record with a comma	
		to_modify[AEI] = re.sub(";$",",",aerobit)
	
		if AEI in to_modify.keys():	
			aerobit = to_modify[AEI]

	for AE in to_modify.keys():
		aero_physical_lines[AE] = to_modify[AE]

	# join the list again
	aero_whole = "".join(aero_physical_lines)
	#aero_codes = re.sub("\\(fromStatus\\(([0-9][0-9][0-9])\\)\s*\\+\s*","\1",aero_whole)
	#print aero_codes	
	
	status_code_line = re.finditer("fromStatus\\(([0-9][0-9][0-9])\\)\s*\\+*\s*",aero_whole)
	aero_poo = aero_whole.strip()
	if status_code_line:
		for scl in status_code_line:
			print "***" + scl.group(0) + "***"
			print "***" + scl.group(1) + "***"
			oldstring = scl.group(0).strip()
			newstring = scl.group(1).strip()
			aero_poo = aero_poo.replace(oldstring,newstring)
	print aero_poo



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