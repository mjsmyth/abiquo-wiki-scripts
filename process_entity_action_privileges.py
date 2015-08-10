#!/usr/bin/python3 -tt

import sys
import re
import os

# create a set of tables of entities + actions + details + the privileges required to see each event
# 
# Input file should be platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations/EntityAction.java
#
# Output file 1 should be output_files/wiki_entity_action_privileges_ + date + .txt
# - use this file to create the "Events View" page of this wiki
#
# Output file 2 should be input_files/entity_list_ + date + .txt, which is an input to the file tracer processing file
# Output file 3 should be input_files/entity_action_list_ + date + .txt, which is an input to the file tracer processing file
#
# Note that this program has a basic mechanism to skip the java surrounding the enumerations!
# If there are any problems: it uses RS = Master, and checks for * in records, and doesn't print headers or details of the first record and last two records! 
# 
# 
#
#

def main():
	FS="new KEYS"
	RS="public static final class|public static final Action|Master"
	KeyTotal = " "
	NRSave = 0
	EntityName = ""
	ActionName = ""
	startout = {}
	entityout = {}
	endout = {}
	entityheader = {}
	entity_space_action = {}
	entity_underscore_actions = {}
	entity_for_users = {}
	KeyInfo = {}
	KeySplit = {}
	keyHappy = " "
	event_list_with_privileges = {}
	td = "2015-08-06"


	git_events_security_dir = "../platform/api/src/main/resources/events"
	events_security_privileges_file = "events-security.properties"
	events_security_file = [es.strip() for es in open(os.path.join(git_events_security_dir,events_security_privileges_file))]

	entity_action_list_git_dir = "../platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations"
	entity_action_git_file = "EntityAction.java"

	entity_list = "entity_list_" + td + ".txt"
	entity_action_list = "entity_action_list_" + td + ".txt"
	input_subdir = "input_files"
	out_subdir = "output_files"
	wiki_entity_action_privileges_file = "wiki_entity_action_privileges_" + td + ".txt"

#	Events security file in format: APPLIB_MANAGE_CATEGORIES= CATEGORY.CREATE, CATEGORY.DELETE, CATEGORY.MODIFY
	# make a list of entities for printing
	entity_entity = {}
	entity_action = {}

	for esi in events_security_file:
#		print ("esi: ",esi)
		esSplit = esi.split("=")
		es_privilege = esSplit[0]
		es_privilege = es_privilege.strip()
		es_event_list = esSplit[1]
		elSplit = es_event_list.split(",")
		for els in elSplit:		
			elsa = els.strip()		
#			write the entity_action to a file
			entity_action[elsa] = elsa			
#			substitute the dot for an underscore
			event_list_event = re.sub("\.","_",els)
			event_list_event = event_list_event.strip()

			# Replace with setdefault when have time?
			if event_list_event not in event_list_with_privileges:
				event_list_with_privileges[event_list_event] = [es_privilege]
			else:
				if es_privilege not in event_list_with_privileges[event_list_event]:
					event_list_with_privileges[event_list_event].append(es_privilege)



	with open (os.path.join(entity_action_list_git_dir,entity_action_git_file), "r") as eafile:
		eadata=eafile.read().replace('\n', '')

	ea_records = re.split(RS,eadata)


	for NR,ear in enumerate(ea_records):
#		print ("NR: ", NR)
		NRSave = NR
		ea_fields = re.split(FS,ear)
		if re.match ("\*",ear):
#			print ("ear: ",ear)
			break

		if len(ea_fields) > 1:
			EntityAction = ea_fields[0].split("=")
			EntityActionNames = EntityAction[0].split(" ")
			EntityName = EntityActionNames[0]

			EntityName = re.sub("\<","",EntityName)
			EntityName = re.sub("\>","",EntityName)

			# Create a dictionary of entities for output as list
			entity_entity[EntityName] = EntityName + ""

			ActionName = EntityActionNames[1]
			entity_space_action[NR] = EntityName + " " + ActionName
			entity_underscore_actions[NR] = EntityName + "_" + ActionName
			entity_underscore_action = EntityName + "_" + ActionName

			if entity_underscore_action in event_list_with_privileges:
				privilege_list = event_list_with_privileges[entity_underscore_action]
				privilege_list_string = ', '.join(privilege_list)
			else:
				privilege_list_string = " "

#			print ("EntityName: ", EntityName)
#			print ("ActionName: ", ActionName)

			mykeysstring = " ".join((ea_fields))
#			print ("mykeysstring: ",mykeysstring)

			thekeys = re.findall('(?<=KEYS\.)[A-Z_]*',mykeysstring)
			if thekeys:
#				print(thekeys)
				thekeystring = ', '.join(thekeys)
			else:
				thekeystring = " "
			
			
			startout[NR] = "| " 
			endout[NR] =  " | " + ActionName + " | " + thekeystring + " | " + privilege_list_string + " |" 
#			print("endout[NR]: ",endout[NR])



		if len(ea_fields) == 1:
			eIndex = NR + 1
			ENameHeading = ea_fields[0]
			ENameHeading = re.sub("\{","",ENameHeading)
			ENameHeading = re.sub ("\n","",ENameHeading)
			entityout[eIndex] = ENameHeading
			entity_for_users[NR] = ENameHeading
			entityheader_fixcase = ENameHeading
			entityheader_fixcase = re.sub ("_"," ",entityheader_fixcase)
			entityheader_fixcase = entityheader_fixcase.lower()
			capital_letter = entityheader_fixcase[:2]
			capital_letter = capital_letter.upper()
			rest_of_letters = entityheader_fixcase[2:]
			entityheader_for_sub = capital_letter + rest_of_letters
			entityheader_for_sub = re.sub("ip","IP",entityheader_for_sub)
			entityheader_for_sub = re.sub ("Ssl","SSL",entityheader_for_sub)
			entityheader_for_sub = re.sub ("ldap","LDAP",entityheader_for_sub)
			entityheader[NR] = entityheader_for_sub


	with open(os.path.join(input_subdir,entity_list), 'w') as g: 
		for eno in sorted(entity_entity):
			EntityNameOut = eno + "\n"
			g.write(EntityNameOut)

	with open(os.path.join(input_subdir,entity_action_list), 'w') as h: 
		for eao in sorted(entity_action):
			if re.match("[A-Z]",eao):
				EntityActionOut = eao + "\n"
				h.write(EntityActionOut)		

	with open(os.path.join(out_subdir,wiki_entity_action_privileges_file), 'w') as f:
		header = "|| Entity || Action || Additional Information || Privileges for Event || \n"
		f.write(header)	 		
		NRI = NRSave - 2
		for s in range(1, NRI): 
			if s in endout:
				if s in entityout:
					outline = startout[s] + entityout[s] + endout[s] + "\n"
					f.write(outline)

				else:
					outline = startout[s] + endout[s] + "\n"
					f.write(outline)
			else:
				outline = "|| h6. " + entityheader[s] + " || || || ||\n"
				f.write(outline)

  
# Calls the main() function
if __name__ == '__main__':
	main()