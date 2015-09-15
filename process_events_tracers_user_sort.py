#!/usr/bin/python3 -tt
#
# Use to create table on page "Events+Table"
# 
# Requires a list of entities and actions for splitting the tracer codes up 
# entity_action_list.txt
# And a separate list of entities for filtering the output to the file - input_files/entity_list_ + date + .txt
# A user version of the same file can be created for "Events+View+for+Cloud+Users"
# Using a list of user entities, which are the only ones that users will be working with
# 
#
import sys
import re
import os
import operator
from collections import OrderedDict

def main():
	entity_actions_file = []
	entity_names = {}
	entity_actions = {}
	entity_compounds = []

	user_entities = []
	tracer_keys = []
	tracer_texts = []

	tracer_keys_matched = []
	tracer_keys_subbed = []


	tracer_messages = []
	tracers = []

	indexed_messages = {}
	tkey_errors = {}
	tkey_severities = {}
	tkey_sev = {}
	eaindex = 0
	tmindex = 0
	tindex = 0
	extra_text = {}
	extra_bit = {}
	outputline = {}
	group_key_change =  {}
	groupkey = {}
	previous_key = " "
	out_subdir = "output_files"
	td = "2015-08-11"
	wiki_event_tracer_all_file = "wiki_event_tracer_user_" + td + ".txt"
	git_dir = "../platform/m/src/main/resources/messages"
	input_subdir = "input_files"
	input_date = "2015-08-11"
	entity_file = "entity_list_user_" + input_date + ".txt"
	prop_file = "tracer.properties"
	entity_action_file = "entity_action_list_user_" + input_date + ".txt"
	entity_actions_file = [ea.strip() for ea in open(os.path.join(input_subdir,entity_action_file))]
	header = "|| Entity || Action || Severity || Tracer || API Error ||\n"

	entities = [ue.strip() for ue in open(os.path.join(input_subdir,entity_file))]
  
	tracer_messages = [tm.strip() for tm in open(os.path.join(git_dir,prop_file))]

#	for ue in user_entities:
#		print("User entity: ",ue)
	enco = []	
	for eai in entity_actions_file:
		print ("eai: ",eai)
		# using entitites from events file instead of old file, so splitting on "."
		eaSplit = eai.split(".")
		print ("eaSplit: ",eaSplit)
		entity_compound = eaSplit[0] + "_" + eaSplit[1]
		entity_compounds.append(entity_compound)
		entity_names[entity_compound] = eaSplit[0].strip()
		entity_actions[entity_compound] = eaSplit[1]

		# create a dictionary of the entity_compound with a tuple including the entity and the action 
		enco.append((entity_compound,eaSplit[0],eaSplit[1]))
	sorted(enco, key=operator.itemgetter(1,2))
	for ec in enco:
		print ("ec: ",ec)
	addtmi = 0	

	for tmi in tracer_messages:
		if not re.search("^\#",tmi):
			if re.search("=",tmi):
				tracerSplit = tmi.split("=")
				tracer_keys.append((tracerSplit[0]).strip())
				tracer_text = tracerSplit[1].strip()
				tracer_text = re.sub("\{","",tracer_text)
				tracer_text = re.sub("\}","",tracer_text)
				tracer_text = re.sub("details\.","",tracer_text)
				tracer_text = re.sub("entity\.","",tracer_text)
				tracer_text = re.sub("\\\\:",":",tracer_text)
				tracer_text = re.sub("details","",tracer_text)
				tracer_text = re.sub("\[","(",tracer_text)
				tracer_text = re.sub("\]",")",tracer_text)
#				tracer_text = re.sub("\'\.","\'",tracer_text)
#     gsub(/{/,"",n); gsub(/}/,"",n); gsub(/\[/,"(",n); gsub(/\]/,")",n); gsub(/(\\)(n)/,"- ",n); gsub(/(\\)(:)/,":",n); gsub("details.","",n); gsub("entity.","",n);
				tracer_texts.append(tracer_text)
				midex = tracerSplit[0].strip()
#				indexed_messages[midex]=tracer_text
				indexed_messages[midex]=tracer_text
				addtmi = addtmi + 1
	print("addtmi: ", addtmi)
	entity_compounds.sort()
	entity_compounds.sort(key=len, reverse=True)	

	tracer_keys.sort()
	tracer_keys.sort(key=len, reverse=True)

	thesorter = []
	added = 0
	for eck,eci in enumerate(entity_compounds):
#		print ("eci: ",eci)
		ecix = "^" + eci
		for tki,tkey in enumerate(tracer_keys):
			if re.search(ecix,tkey):
				print ("tracer_keys: ",tkey)
				tracer_keys_matched.append(tkey)
				print ("tracer_keys_matched: ",tkey," name:",entity_names[eci]," action: ",entity_actions[eci])

				added = added + 1
				tkey_sub = re.sub(ecix,"",tkey)
				tkey_sub = re.sub("^_","",tkey_sub)
				tkey_sub = re.sub("_$","",tkey_sub)

#				print ("tracer_keys_substitution: ",tkey_sub)
				extra_text[tkey] = " "
				extra_bit[tkey] = " "
				tkey_severities[tkey] = " " 
				tkey_errors[tkey] = " "
				info_split = [" "," "]

				if re.search("INFO",tkey_sub):
					info_split = tkey_sub.split("INFO")
					tkey_severities[tkey] = " (i) "
					tkey_sev[tkey] = 2
					if re.search("[A-Z]+",info_split[0]):
						extra_texts = info_split[0]
						extra_text[tkey] = re.sub("_$","",extra_texts)
					if re.search("[A-Z]+",info_split[1]):	
						extra_bits = info_split[1]
#						extra_bit[tkey] = re.sub("_$","",extra_bits)
						extra_bits = re.sub("_$","",extra_bits)											
						extra_bits = re.sub("^_","",extra_bits)
						tkey_errors[tkey] = extra_bits

				if re.search("WARN",tkey_sub):
					info_split = tkey_sub.split("WARN")
					tkey_severities[tkey] = " (!) "
					tkey_sev[tkey] = 1
					if re.search("[A-Z]+",info_split[0]):
						extra_texts = info_split[0]
						extra_text[tkey] = re.sub("_$","",extra_texts)				
					if re.search("[A-Z]+",info_split[1]):	
						extra_bits = info_split[1]
						extra_bits = re.sub("_$","",extra_bits)
						extra_bits = re.sub("^_","",extra_bits)						
						tkey_errors[tkey] = extra_bits


				if re.search("ERROR",tkey_sub):
					info_split = tkey_sub.split("ERROR")
					tkey_severities[tkey] = " (-) "
					tkey_sev[tkey] = 0
					tkey_error = info_split[1]
					tkey_error = re.sub("^_","",tkey_error)
					tkey_error = re.sub("_$","",tkey_error)
					tkey_errors[tkey] = tkey_error	
					extra_texts = info_split[0]
					extra_text[tkey] = re.sub("_$","",extra_texts)				
					extra_bit[tkey] = " "

				tkey_sub = re.sub("^_","",tkey_sub)
				tkey_sub = re.sub("_$","",tkey_sub)
				thesorter.append ((tkey,entity_names[eci],entity_actions[eci],extra_text[tkey],tkey_sev[tkey],indexed_messages[tkey]))
				tracer_keys_subbed.append(tkey_sub)
				print ("tkey_sub: ",tkey_sub)
#				print ("eci: ",eci," \t | tkey: ",tkey," \t |",tki) 
#				print ("eneci: ***",entity_names[eci],"*** \t" )
#				print ("tkey: ****",tkey,"****")
#				outputline[tkey] = "|  | " + entity_actions[eci] + " " + extra_text[tkey] + " | " + tkey_severities[tkey] + " | " + indexed_messages[tkey] + " | "  + tkey_errors[tkey]  + " | \n"						
#				print("entity_names.eci: *****",entity_names[eci],"*****")					
#				print("entity_actions.eci: *****",entity_actions[eci],"*****")
#				print("extra_text.tkey: *****",extra_text[tkey],"*****")					
#				print("tkey_severities.tkey: *****",tkey_severities[tkey],"*****")					
#				print("indexed_messages.tkey: *****",indexed_messages[tkey],"*****")					
#				print("tkey_errors.tkey: *****",tkey_errors[tkey],"*****")
				outputline[tkey] = "| " + entity_names[eci] + " | " + entity_actions[eci] + " " + extra_text[tkey] + " | " + tkey_severities[tkey] + " | " + indexed_messages[tkey] + " | "  + tkey_errors[tkey]  + " | \n"
#				print ("tkey: ***",tkey.strip(),"***")
#				else:
#					outputline[tkey] = "|  | " + entity_actions[eci] + " " + extra_text[tkey] + " | " + tkey_severities[tkey] + " | " + indexed_messages[tkey] + " | "  + tkey_errors[tkey]  + " | \n"						
#				outputline[tkey] = "| " + entity_names[eci] + " | " + entity_actions[eci] + " " + extra_text[tkey] + " " + extra_bit[tkey] + " | " + tkey_severities[tkey] + " | " + indexed_messages[tkey] + " | "  + tkey_errors[tkey]  + " | \n"
#				outputline[tkey] = "| " + entity_names[eci] + " | " + entity_actions[eci] + " " + extra_text[tkey] + " " + extra_bit[tkey] + " | " + tkey_severities[tkey] + " | " + tracer_texts[tki] + " | "  + tkey_errors[tkey]  + " | \n"
				groupkey[tkey] = eci

	print("added: ",added)
	with open(os.path.join(out_subdir,wiki_event_tracer_all_file), 'w') as f:
# This is a terrible mess but I don't have time to fix it right now

		f.write(header)
		tot = 0
		for si in thesorter:
			print("thesorter: ",si)
			tot = tot + 1
		print("tot:",tot)	
		thesorted = []
		thesorted =	sorted(thesorter, key=operator.itemgetter(1,2,3,4))
		tots = 0
		for s in thesorted:
			print("sorted: ",s)
			tots = tots + 1
		print("tots: ",tots)	
		mysorted = []	
		mysorted = [x[0] for x in thesorted]
		print("mysorted: ",len(mysorted))
		ok = list(OrderedDict.fromkeys(mysorted))
		print("lengthok",len(ok))
		for olk in ok:
#			print ("olk: ",olk," \t| groupkey-olk: ",groupkey[olk]," \t | entity_names-g-o: ",entity_names[groupkey[olk]])
			if entity_names[groupkey[olk]] != previous_key:
				entity_name_fix_case = entity_names[groupkey[olk]]
				entity_name_fix_case_end = entity_name_fix_case[1:].lower()
				entity_name_fix_case_start = entity_name_fix_case[:1]
				entity_name_fix_case = entity_name_fix_case_start + entity_name_fix_case_end
				groupheader	= "|| h6. " + entity_name_fix_case + " || || || || || \n"
				if entity_names[groupkey[olk]] in entities:				
					f.write(groupheader)
				previous_key = entity_names[groupkey[olk]]
			if entity_names[groupkey[olk]] in entities:				
				f.write(outputline[olk])


        
  
# Calls the main() function
if __name__ == '__main__':
	main()

