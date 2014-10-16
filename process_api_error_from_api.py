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
from operator import itemgetter, attrgetter, methodcaller


class ApiErrorLine:
	def __init__(self,a_internal_message_id,a_message,a_label):
		self.label=a_label
		self.internal_message_id=a_internal_message_id
		self.message=a_message

	def string_admin(self):
		wiki_label = self.label
		wiki_internal_message_id = self.internal_message_id.strip("\"")
		wiki_message = self.message.strip("\"")
		wiki_message = re.sub("\|","\\\|",wiki_message)
		wiki_message = re.sub("-","\\\-",wiki_message)
	#	wiki_message = dowikimarkup(wiki_message)        
	#  	print("| ",wiki.internal_message_id," | ",wiki.message," | ",wiki.label," |")
		return '| %s | %s | %s | |' % (wiki_internal_message_id, wiki_message, wiki_label)

	def string_user(self):
		wiki_internal_message_id = self.internal_message_id.strip("\"")
		wiki_message = self.message.strip("\"")
		wiki_message = re.sub("\|","\\\|",wiki_message)
		wiki_message = re.sub("-","\\\-",wiki_message)
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

	error_msg_id = ""

	error_key_list = list(error_lines.keys()) 
#	print error_key_list
#	Fiddle with the list to put the status code at the top of the list	
	if "Status code" in error_key_list:
		error_key_list.remove("Status code")
	error_key_list = sorted(error_key_list)
	error_key_list.insert(0,"Status code")	

#	print error_key_list		

#	for x in error_key_list:
		# if re.match(x, "Status code"):
		# 	print "i found it!"
		# 	break
		# else:
		# 	x = None
##	new_error_lines = {}	
	for ee in error_key_list:
#		print "ss: " + ss
		# ab = re.sub("\D","",el)
		# print ab
		for hh in error_lines[ee]:
			hi = re.sub("\D(\d)$","-0\\1",hh.internal_message_id,1)
			print "hi: " + hi
		
#			new_error_lines.setdefault(ee, []).append(ApiErrorLine(padkey(gg),gg.message,gg.label))

		
		ss_interest = sorted(error_lines[ee], key=lambda XX: re.sub("\D(\d)$","-0\\1",XX.internal_message_id,1))
#		ss_interest = sorted(error_lines[ss], key=sort_api_errors(error_lines[ss].internal_message_id))
		print "|| h6. " + ee + " ||  ||  || ||"

		for ii in ss_interest:
			print ii.string_admin()
#			print ael.string_admin()
#			print ael.string_user()
#	sorted(sk,key=lambda str: re.sub("\D","",str))

#		ae_admin = aeline.string_admin()
#		ae_user = aeline.string_user()
	

def padkey(error_object):
	print error_object.internal_message_id
	error_msg_id = error_object.internal_message_id[:]
	number_of_occurrences =	len(re.findall("\d",error_msg_id))
	print "no: " + str(number_of_occurrences)

	if number_of_occurrences == 1:
		error_msg_id = re.sub("(\d)","0\\1",error_msg_id)
		print error_msg_id
	return error_msg_id


# Calls the main() function
if __name__ == '__main__':
	main()