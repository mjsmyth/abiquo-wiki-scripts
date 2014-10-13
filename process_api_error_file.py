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
	aero_copy = aero_whole.strip()
	#aero_codes = re.sub("\\(fromStatus\\(([0-9][0-9][0-9])\\)\s*\\+\s*","\1",aero_whole)
	#print aero_codes	
	status_code_line_with_more = re.finditer("fromStatus\\(([0-9][0-9][0-9])\\)\s*\\++\s*\"*",aero_whole)
	
	if status_code_line_with_more:
		for sclwm in status_code_line_with_more:
			print "sclwm ***" + sclwm.group(0) + "***"
			print "sclwm ***" + sclwm.group(1) + "***"
			oldstring = sclwm.group(0).strip()
			newstring = sclwm.group(1).strip()

#			converted_string = "\"" + convertstatuscode(newstring) 
			converted_string = "\"" + newstring
			print converted_string
			aero_copy = aero_copy.replace(oldstring,converted_string)


	status_code_line = re.finditer("fromStatus\\(([0-9][0-9][0-9])\\),",aero_whole)
	if status_code_line:
		for scl in status_code_line:
			print "***" + scl.group(0) + "***"
			print "***" + scl.group(1) + "***"
			oldstring = scl.group(0).strip()
			newstring = scl.group(1).strip()
#			converted_string = "\"" + convertstatuscode(newstring) + "\","
			converted_string = "\"" + newstring + "\","
			print converted_string
			aero_copy = aero_copy.replace(oldstring,converted_string)

# split into sections
	aero_sections = aero_copy.split("*******")
	print aero_sections
	for aeros in aero_sections:
		aero_headers_sections = aeros.split("#######")
		section_header = aero_headers_sections[0]
		section_header = section_header.strip()
		print section_header
		
		section = aero_headers_sections[1:]

		for rest_of_records in section:		
			one_record = re.split("(?<!'\(')(\),)",rest_of_records)
			print "OR: " + str(one_record)
			new_record = one_record[0::2]
			print "NR: " + str(new_record)

			for newr in new_record:
#				s = re.split(r',\s*(?=[^)]*(?:\(|$))', x)
				newrec = re.sub ("String.format\\(","String.format",newr)
				fields = re.split('\\(\\"',newrec)
				label = fields[0]
				label = label.strip()
				print label
				# Note this can be a heading ##
				if len(fields) > 1:
					id_message = fields[1]
					print id_message
					internal_message_id_message = re.split(',', id_message,1)
					internal_message_id = internal_message_id_message[0]
					internal_message_id = '"' + internal_message_id.strip()
					print internal_message_id
					message = internal_message_id_message[1]
					message = message.strip()
					if re.match("String.format\"",message):
						final_message =	re.sub (r'String.format"','"String.format("',message)
						message = final_message.strip() + ""+
					print message






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