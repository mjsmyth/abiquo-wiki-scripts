#!/usr/bin/python3 -tt
# create a user table of the events and tracers that standard cloud users can see
import sys
import re

def main():
	entity_names = {}
	entity_actions = {}
	
	entity_actions_file = []
	user_entities = []
	tracer_messages_file = []
	
	tracer_keys = {}
	tracer_matched_keys = {}
	tracer_texts = {}
	tracer_messages = {}
	rest_of_keys = {}
	otherinfo = {}
	severities = {}
	error_msgs = {}
	extrabits = []
	tracers = {}
	eaindex = 0
	last_entity_name = " "
	
	entity_actions_file = [ea.strip() for ea in open('input_files/entity_action_list.txt')]	
	user_entities = [ue.strip() for ue in open('input_files/entity_users_list.txt')]
	tracer_messages_file = [tm.strip() for tm in open('v30x_tracer.properties.java')]


	for tmi in tracer_messages_file:
		if not re.search("\#",tmi):
			tracerSplit = tmi.split("=")
			if re.search("[A-Z]+",tracerSplit[0]):
				tracer_key = tracerSplit[0]
				tracer_keys[tracer_key] = tracer_key
				tracer_message = tracerSplit[1]
				tracer_message = re.sub("\[","",tracer_message);
				tracer_message = re.sub("\]","",tracer_message);
				tracer_message = re.sub("\{","",tracer_message);
				tracer_message = re.sub("\}","",tracer_message);		
				tracer_message = re.sub("\\\\:","",tracer_message);		
				tracer_message = re.sub("details.","",tracer_message);
				tracer_message = re.sub("entity.","",tracer_message);
				tracer_messages[tracer_key] = tracer_message

				otherinfo[tracer_key] = " "
				severities[tracer_key] = " "
				error_msgs[tracer_key] = " "
				for eai in entity_actions_file:
					eaSplit = eai.split(" ")
					eaTest = eaSplit[0] + "_" + eaSplit[1]
					checker = "^" + eaTest
					if re.search(checker,tracer_key):
						tracer_matched_keys[tracer_key] = tracer_key
						entity_names[tracer_key] = eaSplit[0]
						entity_actions[tracer_key] = eaSplit[1]
						rest_of_key = tracer_key
						rest_of_key = re.sub(checker,"",rest_of_key)
						rest_of_key = re.sub("_","",rest_of_key)
						extrabits = [" "," "]
						if re.search("INFO",rest_of_key):
							severities[tracer_key] = " (i) "
							extrabits = rest_of_key.split("INFO")
						if re.search("WARN",rest_of_key):
							severities[tracer_key] = " (!) "
							extrabits = rest_of_key.split("WARN")
						if re.search("ERROR",rest_of_key):	
							severities[tracer_key] = " (-) "
							extrabits = rest_of_key.split("ERROR")
						if len(extrabits) > 1:
							if re.search("[A-Z]+",extrabits[1]): 
								error_msgs[tracer_key] = extrabits[1]
							else:
								error_msgs[tracer_key] = " "
						else:
								error_msgs[tracer_key] = " "		
						if len(extrabits) >= 1:
							if re.search("[A-Z]+",extrabits[0]): 
								otherinfo[tracer_key] = extrabits[0]
							else:
								otherinfo[tracer_key] = " "
						else:
								otherinfo[tracer_key] = " "
	
	tki = sorted(tracer_matched_keys.keys())   

	with open("v30_entity_user_test.txt","w") as f:
		header = "|| Entity || Action || Severity || Tracer || Error No. || Info ||\n"
		f.write(header)
		for tk in tki:
			if entity_names[tk] in user_entities:
				if entity_names[tk] != last_entity_name:
					entity_space = "\n"
					f.write(entity_space)
					entity_header = "|| h6. " + entity_names[tk] + " || || || || || ||\n"
					f.write(entity_header)
					last_entity_name = entity_names[tk]
				outputline = "| " + entity_names[tk] + " | " + entity_actions[tk] + " " + otherinfo[tk] + " | " + severities[tk] + " | " + tracer_messages[tk] + " | " + error_msgs[tk] + " |\n"
				f.write(outputline)	
  
# Calls the main() function
if __name__ == '__main__':
	main()

