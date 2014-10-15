#!/usr/bin/python2 -tt
## Process the APIErrors including the error codes
#
# Convert APIError in wiki format to a nice table
#
# For user's guide and developer's guide
#
# replace {} with ""
# replace [] with ()
#
# read the sections file
# put the error messages into a dict in sections
# sort the sections based on the last part of the id
# print a header for each section
# note: also need to compare with previous version's table and mark changed lines and print a diff file
#
#
import sys
import getopt
import re
import os
import requests
import copy
import json


class ApiErrorLine:
	def __init__(self,a_internal_message_id,a_message,a_label):
		self.label=a_label
		self.internal_message_id=a_internal_message_id
		self.message=a_message

	def string_admin(self):
		wiki_label = self.label
		wiki_internal_message_id = self.internal_message_id.strip("\"")
		wiki_message = self.message.strip("\"")
	#	wiki_message = dowikimarkup(wiki_message)        
	#  	print("| ",wiki.internal_message_id," | ",wiki.message," | ",wiki.label," |")
		return '| %s | %s | %s | |' % (wiki_internal_message_id, wiki_message, wiki_label)

	def string_user(self):
		wiki_internal_message_id = self.internal_message_id.strip("\"")
		wiki_message = self.message.strip("\"")
	#	wiki_message = dowikimarkup(wiki_message)        
	# 	print("| ",wiki.internal_message_id," | ",wiki.message," |")
		return '| %s | %s | |' % (wiki_internal_message_id, wiki_message)

def main():
	input_subdir = "input_files"
	output_subdir = "output_files"
	api_error_input_file = "API_error_formats.txt"
	FS = "|"
	error_lines = {}
	error_sorted = {}
	section_header = ""

	api_error_file_user = "wiki_api_error_user_guide_2014-10-13.txt"
	api_error_file_admin = "wiki_api_error_user_guide_2014-10-13.txt"

	print "|| Internal Message ID {color:#efefef}__________________{color}|| Message {color:#efefef}____________________________________________________________{color} ||  Label || Info ||"; 

	sections_json = "apierror_sections.json"		
	api_error_sections_data = open(os.path.join(input_subdir,sections_json))
	section_data = json.load(api_error_sections_data)
	section_keys = sorted(section_data.keys())

	apie_error_formats = [ae.strip() for ae in open(os.path.join(input_subdir,api_error_input_file))]
	count_records = 0
	count_matches = 0

	for apierr in apie_error_formats:
#		count_records = count_records + 1	
		apierr_replaced = apierr.replace("{","(")
		apierr_replaced = apierr_replaced.replace("}",")")
		apierr_replaced = apierr_replaced.replace("[","(")		
		apierr_replaced = apierr_replaced.replace("]",")")
#		if re.match("=|",apierr_replaced):
		apierr_line = re.split('(?<!=)\|',apierr_replaced)

#		print "apierr_line[1]" + apierr_line[1]
#		print "apierr_line[2]" + apierr_line[2]
#		print "apierr_line[3]" + apierr_line[3]
		
		ae_id = apierr_line[1].strip()
		ae_msg = apierr_line[2].strip()
		ae_lab = apierr_line[3].strip()

		aeline = ApiErrorLine(ae_id,ae_msg,ae_lab)
		for skey in section_keys:
			if re.match(section_data[skey],ae_id):
				error_lines.setdefault(skey, []).append(aeline)
#				print "section_data[skey]: " + section_data[skey] + " skey: " + skey + " ae_id: " + ae_id


	for ss in sorted(error_lines):
#		print "ss: " + ss
		# ab = re.sub("\D","",el)
		# print ab
#		for hh in error_lines[ss]:
#			hi = re.sub("\D","",hh.internal_message_id)
#			print "hi: " + hi
		ss_interest = sorted(error_lines[ss], key=lambda XX: int("0" + (re.sub("\D","",XX.internal_message_id))))
#		ss_interest = sorted(error_lines[ss], key=sort_api_errors(error_lines[ss].internal_message_id))
		print "|| h6. " + ss + " ||  ||  || ||"

		for ael in ss_interest:
			print ael.string_admin()
#			print ael.string_user()
#	sorted(sk,key=lambda str: re.sub("\D","",str))

#		ae_admin = aeline.string_admin()
#		ae_user = aeline.string_user()





# Calls the main() function
if __name__ == '__main__':
	main()