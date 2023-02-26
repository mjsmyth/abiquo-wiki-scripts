#!/usr/bin/python3 -tt

import sys
import re
import os

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

	td = "2015-04-30"
	indexed_messages = {}
	tkey_errors = {}
	tkey_severities = {}
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
	wiki_event_tracer_user_file = "wiki_event_tracer_user_" + td + ".txt"
	git_dir = "../platform/m/src/main/resources/messages"
	input_subdir = "input_files"

	user_file = "entity_user_list_"+ td + ".txt"
	prop_file = "tracer.properties"
	entity_action_file = "entity_action_list_" + td + ".txt"
	entity_actions_file = [ea.strip() for ea in open(os.path.join(input_subdir,entity_action_file))]
	header = "|| Entity || Action || Severity || Tracer || API Error ||\n"

	user_entities = [ue.strip() for ue in open(os.path.join(input_subdir,user_file))]
  
	tracer_messages = [tm.strip() for tm in open(os.path.join(git_dir,prop_file))]
	tracer_messages.sort()

#	for ue in user_entities:
#		print("User entity: ",ue)
    	
	for eai in entity_actions_file:
		print ("eai: ",eai)
		eaSplit = eai.split(".")
		print ("eaSplit: ",eaSplit)
		entity_compound = eaSplit[0] + "_" + eaSplit[1]
		entity_compounds.append(entity_compound)
		entity_names[entity_compound] = eaSplit[0].strip()
		entity_actions[entity_compound] = eaSplit[1]
	
		
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

	entity_compounds.sort()
	entity_compounds.sort(key=len, reverse=True)	

	tracer_keys.sort()
	tracer_keys.sort(key=len, reverse=True)

	for eck,eci in enumerate(entity_compounds):
		print ("eci: ",eci)
		ecix = "^" + eci
		for tki,tkey in enumerate(tracer_keys):
			if re.search(ecix,tkey):
				print ("tracer_keys: ",tkey)
				tracer_keys_matched.append(tkey)

				tkey_sub = re.sub(ecix,"",tkey)
				tkey_sub = re.sub("^_","",tkey_sub)
				tkey_sub = re.sub("_$","",tkey_sub)

				print ("tracer_keys_substitution: ",tkey_sub)
				extra_text[tkey] = " "
				extra_bit[tkey] = " "
				tkey_severities[tkey] = " " 
				tkey_errors[tkey] = " "
				info_split = [" "," "]

				if re.search("INFO",tkey_sub):
					info_split = tkey_sub.split("INFO")
					tkey_severities[tkey] = " (i) "
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
					tkey_error = info_split[1]
					tkey_error = re.sub("^_","",tkey_error)
					tkey_error = re.sub("_$","",tkey_error)
					tkey_errors[tkey] = tkey_error	
					extra_texts = info_split[0]
					extra_text[tkey] = re.sub("_$","",extra_texts)				
					extra_bit[tkey] = " "

				tkey_sub = re.sub("^_","",tkey_sub)
				tkey_sub = re.sub("_$","",tkey_sub)

				tracer_keys_subbed.append(tkey_sub)
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

	with open(os.path.join(out_subdir,wiki_event_tracer_user_file), 'w') as f:
		f.write(header)
		ol_keys = sorted(outputline.keys())
		for olk in ol_keys:
#			print ("olk: ",olk," \t| groupkey-olk: ",groupkey[olk]," \t | entity_names-g-o: ",entity_names[groupkey[olk]])
			if entity_names[groupkey[olk]] != previous_key:
				entity_name_fix_case = entity_names[groupkey[olk]]
				entity_name_fix_case_end = entity_name_fix_case[1:].lower()
				entity_name_fix_case_start = entity_name_fix_case[:1]
				entity_name_fix_case = entity_name_fix_case_start + entity_name_fix_case_end
				groupheader	= "|| h6. " + entity_name_fix_case + " || || || || || \n"
				if entity_names[groupkey[olk]] in user_entities:				
					f.write(groupheader)
				previous_key = entity_names[groupkey[olk]]
			if entity_names[groupkey[olk]] in user_entities:				
				f.write(outputline[olk])



# 				if eci != previous_key:
#					previous_key = eci
#					outputline	= " || " + entity_names[eci] + " || || || || || \n"
#				print ("| ",entity_names[eci]," | ",entity_actions[eci]," ",extra_text[tkey]," ",extra_bit[tkey]," | ",tkey_severities[tkey]," | ",tracer_texts[tki]," | ",tkey_errors[tkey]," | ")
					    	
			
			
	
#	sp_json_data = open('api_get_system_properties.json')
#	sp_data = simplejson.load(sp_json_data)
#	sp_data_keys = sorted (sp_data.keys())
#	for spdk in sp_data_keys:
#		if spdk == "collection":
#			sp_collection = sp_data[spdk]
#			for sp_item in sp_collection:
#				sp_keys = sorted(sp_item.keys())
#				for spk in sp_keys:
#					if spk == "id":
#						sp_id_value = sp_item[spk]
#						print ("sp_id: ", sp_id_value)#
#					elif spk == "name":
#						sp_name_value = sp_item[spk]
#						print ("sp_name: ", sp_name_value)
#						sp_name_list = sp_name_value.split(".")
#						if sp_name_list[1] == "wiki":
#							values_wiki[sp_id] = sp_id_value
#						else:
#							values_non_wiki[sp_id] = sp_id_value	
#					elif spk == "value":
#						sp_value_value = sp_item[spk]
#						print ("sp_value: ", sp_value_value)
#						
#    			
# 
#    grouporder = {1: 'general', 2: 'infrastructure', 3: 'network', 4: 'dashboard', 5: 'wikilinks', 6: 'licenses'}
#    groupmatch = {'general': 'client.main', 'infrastructure': 'client.infra', 'network': 'client.network', 'virtualAppliances': 'VAPP','appsLibrary': 'APPLIB', 'users': 'USERS', 'systemConfiguration': 'SYSCONFIG', 'events': 'EVENTLOG', 'pricing': 'PRICING'}
#    json_data = open('lang_en_US.json')
#    data = simplejson.load(json_data)
#    privlabels = {}
#    privnames = {}
#    privdescs = {}
#    privgroups = {}
#    labelkeys = sorted(data.keys())
#    for labelkey_orig in labelkeys: 
#        labelkey = labelkey_orig.split(".")
#        pg = labelkey[0]
#        if pg == "privilegegroup":
#            pgk = labelkey[1]
#            if pgk != "allprivileges":
#                privgroups[pgk] = data[labelkey_orig]
#                print ("privilege group: ", labelkey)
#        elif pg == "privilege":
#            pd = labelkey[1]
#            if pd == "description":
#                pdk = labelkey[2]
#                privdescs[pdk] = data[labelkey_orig]
#                print("privilege description: ", labelkey)
#            elif pd != "details":
#                privlabels[pd] = pd 
#                privnames[pd] = data[labelkey_orig] 
#                print("privilege: ", labelkey)

#    pgkeys = sorted(grouporder.keys())     
#    plkeys = sorted(privlabels.keys())
#    for pgk in pgkeys:
#        pgkordered = grouporder[pgk]
#        current_group = groupmatch[pgkordered]
#        privgroupindexed = privgroups[pgkordered]
#        print (privgroupindexed)
#        for plk_orig in plkeys:
#            plk = plk_orig.split("_")
#            if current_group == plk[0]:
#                print (privnames[plk_orig],": ",privdescs[plk_orig])
#                key_cloud_admin = plk_orig + "=CLOUD_ADMIN"
#                key_ent_admin = plk_orig + "=ENTERPRISE_ADMIN"
#                key_user = plk_orig + "=USER"
#                if key_cloud_admin in sqlroles:
#                    print ("CLOUD_ADMIN")
#                if key_ent_admin in sqlroles:
#                    print ("ENT_ADMIN")    
#                if key_user in sqlroles:
#                    print ("USER")                   
#	sp_json_data.close()

        
  
# Calls the main() function
if __name__ == '__main__':
	main()

