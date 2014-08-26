#!/usr/bin/python3 -tt

import sys
import re
import os

# create a set of tables of events and actions 
# Input file should be platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations/EntityAction.java
# Output file should be output_files/wiki_events.txt
# Note that I have hacked this program to make it leave out the java muck surrounding the enumerations!
# If there are any problems: it uses RS = Master, and checks for * in records, and doesn't print headers or details of the first record and last two records! 
# NOTE that this script produces two other output files - entity_action_list.txt, which is an input to the tracer processing scripts
# and entity_list.txt which is a list of all entities as a starting point for the events and tracer tables for users... 
# actually now I think about it, the user events have "USER" maybe this isn't necessary... aagh
# ./process_events.sh ../platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations/EntityAction.java output_files/wiki_events.txt
#
# Note that the following comments are out of date:
# Convert EventType.java to Confluence Wiki Format
# Note that it is best to cut the java code from the beginning and end of the file as that is not included in the scope of this script
# Read EventType.java file $1 and write to wiki output $2
# Mark comments starting with // as header records
# Strip whitespace in the file
# Set the record separator as "), "
# Print the first field of lines with one field beginning with // as h5. in wiki format after stripping non-numerics, then print header table row with first letter only in caps
# If header record, print header 
# Note that the last record is not processed properly because of EOF or something
# Print normal error message lines separated by | for wiki format
## replace {} with ""
## replace [] with ()
# Leaves other // comments in file - check for these

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
	entity_underscore_action = {}
	entity_for_users = {}
	KeyInfo = {}
	KeySplit = {}
	keyHappy = " "
	event_list_with_privileges = {}

	git_events_security_dir = "../platform/api/src/main/resources/events"
	events_security_privileges_file = "events-security.properties"
	events_security_file = [es.strip() for es in open(os.path.join(git_events_security_dir,events_security_privileges_file))]

	entity_action_list_git_dir = "../platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations"
	entity_action_git_file = "EntityAction.java"

	entity_list = "input_files/entity_list.txt"

	for esi in events_security_file:
		print ("esi: ",esi)
		esSplit = esi.split("=")
		es_privilege = esSplit[0]
		es_privilege = es_privilege.strip()
		es_event_list = esSplit[1]
		elSplit = es_event_list.split(",")
		for els in elSplit:		
#			substitute the dot for an underscore
			event_list_event = re.sub("\.","_",els)
			event_list_event = event_list_event.strip()
			if event_list_event not in event_list_with_privileges:
				event_list_with_privileges[event_list_event] = [es_privilege]
			else:
				if es_privilege not in event_list_with_privileges[event_list_event]:
					event_list_with_privileges[event_list_event].append(es_privilege)


	with open (os.path.join(entity_action_list_git_dir,entity_action_git_file), "r") as eafile:
		eadata=eafile.read().replace('\n', '')

	ea_records = re.split(RS,eadata)

	for NR,ear in enumerate(ea_records):
		print ("NR: ", NR)
		NRSave = NR
		ea_fields = re.split(FS,ear)
		if re.match ("\*",ear):
			print ("ear: ",ear)
			break

		if len(ea_fields) > 1:
			EntityAction = ea_fields[0].split("=")
			EntityActionNames = EntityAction[0].split(" ")
			EntityName = EntityActionNames[0]

			EntityName = re.sub("\<","",EntityName)
			EntityName = re.sub("\>","",EntityName)

			ActionName = EntityActionNames[1]
			entity_space_action[NR] = EntityName + " " + ActionName
			entity_underscore_action[NR] = EntityName + "_" + ActionName

			print ("EntityName: ", EntityName)
			print ("ActionName: ", ActionName)

			mykeysstring = " ".join((ea_fields))
			print ("mykeysstring: ",mykeysstring)

			thekeys = re.findall('(?<=KEYS\.)[A-Z_]*',mykeysstring)
			if thekeys:
				print(thekeys)

			thekeysstring = ', '.join(thekeys)

			# for MyKey in range(1,4):
			# 	print ("ea_fieldsMK: ",ea_fields[MyKey])
			# 	if re.match ("KEYS",ea_fields[MyKey]):
			# 		KeyInput = ea_fields[MyKey]
			# 		KeyInput = re.sub("KEYS.","",KeyInput)
			# 		KeyInput = re.sub("\\[","",KeyInput)
			# 		KeyInput = re.sub("\]","",KeyInput)
			# 		KeyInput = re.sub("\{","",KeyInput)
			# 		KeyInput = re.sub("\}","",KeyInput)
			# 		KeyInput = re.sub("\);","",KeyInput)
			# 		KeyInput = re.sub("\n","",KeyInput)
			# 		KeyInput = re.sub("\*","",KeyInput)
			# 		KeyInfo[MyKey] = copy(KeyInput)
			# 	else:
			# 		KeyInfo[MyKey] = " "
			# print ("KeyInfo: ", str(KeyInfo))
			# for mk in KeyInfo:	
			# 	KeyTotal = KeyTotal + KeyInfo[mk] 
			# print ("KeyTotal: ",KeyTotal)	
			# KeySplit = KeyTotal.split ("\,|[ \t\n]+")
			# keyHappy = " ";
			# for KeyItem in KeySplit:
			# 	if re.match("/[A-Z][a-z]/",KeyItem):
			# 		if re.match("/[A-Z][a-z]/",keyHappy):
			# 			keyHappy = keyHappy + ", " + KeyItem
			# 		else:
			# 			keyHappy = copy(KeyItem)
			
			startout[NR] = "| " 
			endout[NR] =  " | " + ActionName + " | " + thekeysstring + " |" 
			print("endout[NR]: ",endout[NR])
	 
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
	 		

	print ("|| Entity || Action || Additional Information ||")
	NRI = NRSave - 2
	for s in range(1, NRI): 
		if s in endout:
			if s in entityout:
				print (startout[s], entityout[s], endout[s])
			else:
				print (startout[s], endout[s])	
		else:
			print ("|| h6. ", entityheader[s], " || || ||")

  
# Calls the main() function
if __name__ == '__main__':
	main()