#!/usr/bin/python3 -tt

import sys
import re
import os
import codecs

def main():
	en_properties = {}
	es_properties = {}

	property_names = {}
	property_texts = {}
	properties = {}

	oen_properties = {}
	oes_properties = {}
	text = ""
	text_es = ""

	out_subdir = "output_files"
	out_en_properties = "UI_p.en_US.properties"
	out_es_properties = "UI_p.es_ES.properties"

	git_dir = "../clientui/swf/src/main/locales"
	spanish_file = "UI_es_ES.properties"
	english_file = "UI_en_US.properties"

	
	en_props = [enp.strip() for enp in codecs.open(os.path.join(git_dir,english_file),'r',encoding="utf-8")]
	es_props = [esp.strip() for esp in codecs.open(os.path.join(git_dir,spanish_file),'r',encoding="utf-8")] 

   	
	for enpi in en_props:
		if not re.search("^\#",enpi):
			if re.search("[A-Z][a-z]",enpi):
				print ("enpi: ",enpi)
				enSplit = enpi.split("=")
				print ("enSplit: ",enSplit)
				name = enSplit[0].strip()
				text = enSplit[1].strip()
				en_properties[name] = text

	for espi in es_props:
		if not re.search("^\#",espi):
			if re.search("[A-Z][a-z]",espi):
				print ("espi: ",espi)
				esSplit = espi.split("=")
				print ("esSplit: ",esSplit)
				name_es = esSplit[0].strip()
				text_es = esSplit[1].strip()
				es_properties[name_es] = text_es	
		

	with codecs.open(os.path.join(out_subdir,out_en_properties), 'w',"utf-8") as enf:
		with codecs.open(os.path.join(out_subdir,out_es_properties), 'w',"utf-8") as esf:
			for enk in sorted(en_properties.keys()):
				if enk in (es_properties.keys()):
					if en_properties[enk] != es_properties[enk]:
						enfo = enk + "=" + en_properties[enk] + "\n"
						print ("enfo: ", enfo)
						esfo = enk + "=" + es_properties[enk] + "\n"
						print ("esfo: ", esfo)
						enf.write(enfo)
						esf.write(esfo)
        
  
# Calls the main() function
if __name__ == '__main__':
	main()

