#!/usr/bin/python2 -tt
## Process the Configuration view options and print extra text from file
## TODO manually change the default view option from 0 to Home
## 
##
import sys
import re
import os
import json
import requests
import readline
 

def main():
	apiHeaders = {}
	td = "2018-12-20"

# Enter path in filesystem to a file with the UI tags for fields cloned from github
#	ui_path = input("Language file path: ").strip()
	input_subdir = "input_files"
	output_subdir = "output_files" 
	output_file_name = "wiki_config_view_" + td + ".txt"
	extra_text_file_name = 'process_config_view_extratext_' + td + '.txt'
	ui_path = "../platform/ui/app/"
	ui_path_lang = ui_path + "lang/"
	ui_path_html = ui_path + "modules/configuration/partials/"
 	apiAuth = raw_input("Enter API authorization, e.g. Basic XXXX: ")
 	apiIP = raw_input("Enter API address, e.g. api.abiquo.com: ")
# Get system properties data from the API of a fresh Abiquo	
#	apiAuth = input("Authorization: ").strip()
#	apiIP = input("API IP address: ").strip()
	apiUrl = 'http://' + apiIP + '/api/config/properties'
	print apiUrl
	apiAccept = 'application/vnd.abiquo.systemproperties+json'
	apiHeaders['Accept'] = apiAccept
	apiHeaders['Authorization'] = apiAuth
	r = requests.get(apiUrl, headers=apiHeaders, verify=False)
	sp_data = r.json()

	store_id = {}
	store_name = {}
	store_value = {}
	store_ui_key = {}
	store_ui_group = {}
	store_key = {}
	store_group = {}
	store_ui_label = {}
	store_extra_text = {}
	
	super_key = ""
	super_group = ""

	store_wiki = {}
	wiki = 0
	last_group = ""
	etkey = ""
	ettext = ""

	store_wiki_gui_order = []
	store_wiki_gui_group = {}
	store_gui_order = []
	store_gui_group = {}

	store_checkbox = {}
	value_output = " "
	lgs = " "
	tgs = " "

	check_last_group = "  "
	check_last_tab = "  "

# Read the system properties request from the API or from the file system
#	sp_json_data = open('v30rc3_api_get_system_properties.json')
#	sp_data = json.load(sp_json_data)
# The name is in format "client.applibrary.defaultTemplateRepository". 
# Process the name to give a super key value in lower case "defaulttemplaterepository"
# Store all the info with this key
# Also check and store if it is a wiki link, because it goes in a separate output section
# And there is no Notes field for wiki links 
	sp_data_keys = sorted (sp_data.keys())
	for spdk in sp_data_keys:
		if spdk == "collection":
			sp_collection = sp_data[spdk]
			for sp_item in sp_collection:
				sp_keys = sorted (sp_item.keys())
				for spk in sp_keys:
					if spk == "id":
						sp_id_value = sp_item[spk]
   						print ("sp_id: ",sp_id_value)
					elif spk == "name":
						sp_name_value = sp_item[spk]
   						print ("sp_name: ",sp_name_value)
						end_id_mixed_list = sp_name_value.split(".")
   						print ("eiml: ",end_id_mixed_list)
						end_id_mixed = end_id_mixed_list[-1]
						end_gp_mixed = end_id_mixed_list[-2]
						if end_id_mixed_list[-3] == "wiki":
							wiki = 1
						else:
							wiki = 0
	
						if end_id_mixed == "url":
							if end_gp_mixed == "logout":
								super_key = "logouturl"
								super_group = "main"	
						else:		
							if end_id_mixed == "manageDatastoreTiers":
								super_key = "datastoretiers"
							elif end_id_mixed == "manageBackupPolicies":
								super_key = "policies"
							elif end_id_mixed == "manageBackupPolicyProperties":
								super_key = "policyproperties"	
							else:	
								super_key = end_id_mixed.lower()
							super_group = end_gp_mixed.lower()  						
					elif spk == "value":
						sp_value_value = sp_item[spk]
   						print ("sp_value: ",sp_value_value)
				store_id[super_key] = sp_id_value
				store_name[super_key] = sp_name_value
				store_value[super_key] = sp_value_value
				store_group[super_key] = super_group
				store_key[super_key] = super_key
				store_wiki[super_key] = wiki

# Process the language file which has keys and UI labels
# e.g. "configuration.systemproperties.infra.defaulttemplaterepository":"Default Abiquo template repo (will not be created if empty)",
# Store the lowercase key e.g. defaulttemplaterepository and the UI label
	ui_json = ui_path_lang + "lang_en_US_labels.json"		
	ui_json_data = open(ui_json)
	ui_data = json.load(ui_json_data)
	ui_keys = sorted(ui_data.keys())
	for uik in ui_keys:
		uik_split = uik.split(".")
		if uik_split[0] == "configuration" and uik_split[1] == "systemproperties":
			uikkey = uik_split[-1]
			uikkey = uikkey.strip()
			uikgroup = uik_split[-2]
			print ("uikkey: ",uikkey)
			print ("uikgroup: ",uikgroup)
			store_ui_key[uikkey] = uikkey
			store_ui_group[uikkey] = uikgroup
			store_ui_label[uikkey] = ui_data[uik]

# Process the text file with the wiki notes about the system properties. It has lower case keys
	with open(os.path.join(input_subdir,extra_text_file_name), 'r') as extra_text_file:
		extra_text_all = extra_text_file.read()
	extra_text_list = extra_text_all.split("\n\n")
	
	for et in extra_text_list:
		ettext = " "
		extra_text_split = et.split("=",1)
		print ("extra_text_split_0: ", extra_text_split[0])
		print ("extra_text_split_1: ", extra_text_split[1])
		etkeyall = extra_text_split[0]
		etkeyall = etkeyall.split(".")
		if etkeyall[-1].strip() == "url":
			etkey = "logouturl"
		else:
			etkey = etkeyall[-1]
		etkey = etkey.strip()
		etkey = etkey.lower()
		if re.search("[a-z]",etkey): 
			ettext = extra_text_split[1]
			ettext = ettext.strip()
			store_extra_text[etkey] = ettext



# Read in the UI app HTML files and concatenate them into one bloody great long string so as to get the order of stuff on each page
# TODO: store if value is a checkbox
	general_ui = ui_path_html + "generalform.html"
	with open(general_ui, 'r') as general_html_text_file:
		general_text_all = general_html_text_file.read()

	infra_ui = ui_path_html + "infrastructureform.html"
	with open(infra_ui, 'r') as infrastructure_html_text_file:
		infrastructure_text_all = infrastructure_html_text_file.read()

	network_ui = ui_path_html + "networkform.html"
	with open(network_ui, 'r') as network_html_text_file:
		network_text_all = network_html_text_file.read()

	dashboard_ui = ui_path_html + "dashboardform.html" 
	with open(dashboard_ui, 'r') as dashboard_html_text_file:
		dashboard_text_all = dashboard_html_text_file.read()

	password_ui = ui_path_html + "passwordform.html"
	with open(password_ui, 'r') as password_html_text_file:
		password_text_all = password_html_text_file.read()	

	wikilinks_ui = ui_path_html + "wikilinksform.html"
	with open(wikilinks_ui, 'r') as wikilinks_html_text_file:
		wikilinks_text_all = wikilinks_html_text_file.read()



	html_text_all = general_text_all.strip() + infrastructure_text_all.strip() + network_text_all.strip() + dashboard_text_all.strip() + password_text_all.strip() + wikilinks_text_all.strip() 

	# Process the UI order
	# search patterns
	group_code = "^mainmenu.button"
	gui_code = "^configuration.systemproperties"
	checkbox = "icon-ok"
	tab_code = "configuration.tab"

	current_tab = ""
	current_group = ""
	gui_prop = ""



	html_text_list = html_text_all.split("\'")
	for ht in html_text_list:
		if re.search(tab_code,ht):
			current_tab_all = ht.split(".")
			current_tab = current_tab_all[-1]

		if re.search(group_code,ht):
			current_group_full_name = ht.split(".")
			current_group = current_group_full_name[-1]


		if re.search(gui_code,ht):
			gui_prop_full_name = ht.split(".")
			gui_prop = gui_prop_full_name[-1]	

			if gui_prop_full_name[-3] == "wiki":
				store_wiki_gui_order.append(gui_prop)
				store_wiki_gui_group[gui_prop] = current_group
			else:	
				if gui_prop != "title":
					if gui_prop != "defaultprivatevlan":
						if gui_prop != "returntourl":
							store_gui_order.append(gui_prop)
							store_gui_group[gui_prop] = current_tab
						
		if re.search(checkbox,ht):
			store_checkbox[gui_prop] = 1	

	outfile = open(os.path.join(output_subdir,output_file_name), 'w')

	outfile.write ("h3. Configuration \n")
	group_sub_dict = {"applibrary":"Apps Library","infra":"Infrastructure","vdc":"Virtual datacenter","vm":"Virtual machine","config":"Configuration","virtual":"Virtual machines","apps":"Apps Library","wiki":"Wiki help"}
	

	for sp,su in enumerate(store_gui_order):
		extra_text_output = " "
		ui_label_output = " "
		value_output = " "

		check_last_tab = store_gui_group[su].strip()
		if tgs != check_last_tab:
			tgs = check_last_tab
			tgso = tgs[0].upper() + tgs[1:]
			if tgso == "Wikilinks":
				tgso = "Wiki links"
#			subheader = "h4. " + tgso + " properties")	
			subheader = "|| h6. " + tgso + " || Default || Notes || Info || \n"
			outfile.write (subheader)
			if tgso == "Network":
				subheader_network_extra = "||  " + tgso + "|| || Default private VLAN for virtual datacenters  || || \n"
				outfile.write(subheader_network_extra)

		su = su.strip()	
		if su in store_extra_text:
			extra_text_output = store_extra_text[su]
			print ("store_extra_text: ",store_extra_text[su])
		else:
			extra_text_output = "-"	
		if su in store_ui_label:
			ui_label_output = store_ui_label[su]	
			print ("store_ui_label: ",store_ui_label[su])
		if su in store_value:
			value_output = store_value[su]
			print ("store_value: ",store_value[su])
			if su in store_checkbox:
				print ("su: ",su,"store_value[su]: ",store_value[su])
				if store_checkbox[su] == 1:
					if value_output == "1":
						value_output = ("(/)")
					if value_output == "0":
						value_output = ("(x)")	
		sp = str(sp + 1)
		table_line = "|   " + ui_label_output + " | " + value_output + " | " + extra_text_output + " | | \n"
		outfile.write(table_line)
				
#				print ("| " + store_key[su] + " | " + store_group[su] + " | " + store_ui_label[su] + " | " + store_value[su] + " |") 
	outfile.write (" \n")
	outfile.write (" \n")
	outfile.write ("h3. Wiki links list\n")

	for sgp,swgg in enumerate(store_wiki_gui_order):
		check_last_group = store_wiki_gui_group[swgg].strip()
		if lgs != check_last_group:
			lgs = check_last_group		
			lgso = lgs[0].upper() + lgs[1:]
			if lgso == "Infraestructure":
				lgso = "Infrastructure"
			if lgso == "Virtualdatacenters":
				lgso = "Virtual datacenters"
			if lgso == "Apps_library":
				lgso = "Apps library"		
			subheader_wiki_links =  "|| h6. " + lgso + " || Default || Info || \n"
			outfile.write (subheader_wiki_links)
		sgp = str(sgp + 1)
		wiki_link_output = "|  "+store_ui_label[swgg]+" | "+store_value[swgg]+" | | \n"
		outfile.write (wiki_link_output)


#	sp_json_data.close()
	ui_json_data.close()
	outfile.close()
  
# Calls the main() function
if __name__ == '__main__':
	main()

