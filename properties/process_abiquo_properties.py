#!/usr/bin/python2 -tt
import sys
import os
import json
import re
import collections
import pystache
import codecs

class filedetails:
	def __init__(self,aprefix,asuffix,adate,aiprefix,aisuffix):
		self.fprefix = aprefix
		self.fsuffix = asuffix
		self.fdate = adate
		self.iprefix = aiprefix
		self.isuffix = aisuffix

class prop:
	def __init__(self,apropName,apropProfiles,apropType,apropDescription,apropDefault,apropRange):
		self.pName = apropName
		self.pDefault = apropDefault
		self.pDescription = apropDescription
		self.pRange = apropRange
		self.pProfiles = apropProfiles
		self.pType = apropType
		
	
	def pprint(self):
		prProfiles = " ".join(self.pProfiles)
		print "| %s | %s | %s | %s | %s | %s |" % (self.pName,self.pDefault,self.pRange,self.pDescription,prProfiles,self.pType)

def open_if_not_existing(filename):
	try:
		fd = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
	except:
		print ("File: %s already exists" % filename)
		return None
	fobj = os.fdopen(fd, "w")
	return fobj

def tree(): return collections.defaultdict(tree)

def wikiHeadings(profiles,filedetails):
	heading_links_list = []
	for prix, profile in profiles.items():
		header_profile_item = {}
		header_profile_item['ExampleFile'] = filedetails.fprefix + profile.lower() + "_" + filedetails.fdate + filedetails.fsuffix
		header_profile_item['ExampleImage'] = filedetails.iprefix + profile.lower() + filedetails.isuffix
		heading_links_list.append(header_profile_item)
	return heading_links_list
		

def getCategory(pName):
	prop_cat = pName.split(".")
	property_cat = prop_cat[1]
	if prop_cat[0] == "workflow":
		property_cat = "workflow"
	if prop_cat[0] == "com":
		property_cat = "virtualfactory"
	if property_cat == "stale":
		property_cat = "stale sessions"
	if property_cat == "dvs":
		property_cat = "dvs and vcenter"
	if property_cat == "vi":
		property_cat = "virtual infrastructure"		
	if property_cat == "USE_SECURE_CHANNEL_LOGIN":
		property_cat = "client"
	if property_cat == "vi":
		property_cat = "virtual infrastructure"
	if property_cat == "m":
		property_cat == "m outbound api"					
	return property_cat

def subPropertyDefault(rawDefault,rawName):
#	if re.search(r"{",rawDefault):
#		rawDefault = re.sub(r"{",r"\{",rawDefault) 
	if rawName == "abiquo.datacenter.id":
		rawDefault = re.sub("default","Abiquo",rawDefault)
	if rawName == "abiquo.kairosdb.host":
		rawDefault = re.sub("127.0.0.1","<KairosdbLoc>",rawDefault)	
	rawDefault = re.sub("127.0.0.1",r"<IP-repoLoc>",rawDefault)
	rawDefault = re.sub("localhost",r"127.0.0.1",rawDefault)
	rawDefault = re.sub("10.60.1.4",r"127.0.0.1",rawDefault);
	return rawDefault

def wikiProperty(rawProp,profiles,filedetails):
	property_entry = {}
	property_entry['propertyName'] = rawProp.pName
	property_entry['propertyDefault'] = rawProp.pDefault
	property_entry['propertyRange'] = rawProp.pRange
	property_entry['propertyDescription'] = rawProp.pDescription
	property_entry['propertyProfiles'] = []
	for prix, profile in profiles.items():
		property_profile_item = {}
		property_profile_item['profile'] = {}
		if profile in rawProp.pProfiles:
			property_profile_item['profile']['profileExampleFile'] = filedetails.fprefix + profile.lower() + filedetails.fdate + filedetails.fsuffix
			property_profile_item['profile']['profileExampleImage'] = filedetails.iprefix + profile.lower() + filedetails.isuffix	
		property_entry['propertyProfiles'].append(property_profile_item.copy())	
	return property_entry


def wikiCategories(storage_dict):
	catkeydict = {}
	catkeys = {}
	catkeyorder = collections.OrderedDict()
	catdata = collections.OrderedDict()
	catkeydict = collections.OrderedDict()
	# sort properties by names in lower case
	for prop in sorted(storage_dict,key=lambda s: s.lower()):
		# create a dictionary of property names : categories
		pn = storage_dict[prop]['propertyName']
		property_category = getCategory(pn)
		catkeydict[pn] = property_category
	# from the above dictionary, go through the categories and make them the key to a new dictionary that stores the whole property
	for v,k in catkeydict.items(): 
		if k in catkeyorder:
			catkeyorder[k].append(storage_dict[v])
		else:
			catkeyorder[k] = [storage_dict[v]]				
	catdata = [{'categoryName':k, 'entries':v} for k,v in (catkeyorder.items())]
	return catdata

def getSampleMessage(profile,version):
	profile_print_info = {}
	profile_print_info["API"] = "API / SERVER / UI"
	profile_print_info["V2V"] = "V2V (REMOTE SERVICES)"
	profile_print_info["RS"] = "REMOTE SERVICES"
	profile_print_info["OA"] = "OUTBOUND API"
	sampleMessage = []
	swPrintStars = "################################################################################\n"
	swPrintIntro = "#### This is a sample abiquo.properties file for "  
	swPrintEnd =   "            ####\n"	
	swPrintLine = swPrintIntro + profile_print_info[profile] + swPrintEnd 
	sampleMessage.append(swPrintStars)
	sampleMessage.append(swPrintLine)
	sampleMessage.append(swPrintStars)
	return sampleMessage


def storeProperties(content,property_regex_comment,property_regex_no_comment,range_regex,profiles,fdetails,sample_files):
	wiki_property_dict = {}
	property_profiles = []
	property_description_list = []
	property_name = "" 
	property_description = ""
	property_type = ""
	property_default = ""
	property_range = ""

	for property_line in content:
		# a blank line may mark the end of a property
		if re.match("\n", property_line):
			del property_description_list [:]
			property_name = "" 
			property_description = ""
			property_type = ""
			property_default = ""
			property_range = ""
	
		# if you get a comment line
		elif re.match("#",property_line):
			# Lots of hashes means a server profile specification
			if re.match("#####",property_line):
#				print "matched profiles"
				del property_profiles [:]
				# Multiple profiles comment is for users editing the file
				if re.search("MULTIPLE PROFILES",property_line):
					continue
				# set up the profiles for this section of properties	
				else:
					for profile in profiles:
						if re.search(profile,property_line):
							property_profiles.append(profiles[profile])
			else:
			# 	search for a property name and optional default value
				property_match = property_regex_comment.match(property_line)
				if property_match:
					property_type = "optional"
					# the third group is the property name
					property_name = property_match.group(3)
					# the sixth group, if it exists, is the property default value
					if property_match.group(6):
						property_default = property_match.group(6).strip()
						property_default = subPropertyDefault(property_default,property_name)
					else:
						property_default = ""
				else:	
	#				add property description to a list
					property_description_list.append(property_line[1:].strip()) 
		else:	
#			mandatory property name and optional default value, commented out - note may have space after comment
			property_match = property_regex_no_comment.match(property_line)
			if property_match:
				property_type = "mandatory"
				# the first group is the property name
				property_name = property_match.group(1)
				# the fourth group, if it exists, is the property default value
				if property_match.group(4):
					property_default = property_match.group(4).strip()
					property_default = subPropertyDefault(property_default,property_name)
				else:
					property_default = ""	
		property_category = ""
		if property_name:		
			# create a sample_files dictionary organised by profile names
			# sample file is similar to the main input file but it only contains properties of one profile
			for pro in property_profiles:
				sample_property = ""
				if pro in sample_files:
					for pd in property_description_list:
						pk = "# " + pd + "\n"
						sample_files[pro].append(pk)
				else:
					sample_files[pro] = []	
					for pd in property_description_list:
						pk = "# " + pd + "\n"							
						sample_files[pro].append(pk)
				if property_type == "mandatory":			
					sample_property = "#" + property_name + " = " + property_default + "\n\n"	
				else:	
					sample_property = property_name + " = " + property_default + "\n\n"	
				sample_files[pro].append(sample_property)

			# prepare for wiki	
				property_description = " ".join(property_description_list)			
	#			search for Range: x-x type info in wiki properties and store it separately
				property_range_search = range_regex.search(property_description)
				if property_range_search:
					property_range = property_range_search.group(2) 
					property_description = re.sub(property_range_search.group(0),"",property_description)
				aproperty = prop(property_name,property_profiles,property_type,property_description,property_default,property_range)
	#			aproperty.pprint()
				property_wiki = wikiProperty(aproperty,profiles,fdetails)		
				wiki_property_dict[property_name] = property_wiki.copy()
	return (wiki_property_dict,sample_files)		


def main():

	sample_files = {}
	wiki_output = {}
	categories = []

	# prevWikiVersion = "ABI32"
	wikiVersion = "ABI36"
	# # Directories and file names

 #    input_subdir = 'input_files'
 #    output_subdir = 'output_files'

 #    compFile = prevWikiVersion + output_subdir
    # inputDir = wikiVersion + "/" + input_subdir
    # outputDir = wikiVersion + "/" + output_subdir
	td = "2015-08-11"

#    inputDir = '~/platform/system-properties/src/main/resources'
	propertyFile = 'abiquo.properties_' + td

    
	# These are the details of the sample files and the images that link to the sample files on the wiki
	filePrefix = "properties_"
	fileSuffix = ".txt"
	imagePrefix = "v26_symbol_"
	imageSuffix = "_transparent.png"
	fdetails = filedetails(filePrefix,fileSuffix,td,imagePrefix,imageSuffix)

	property_description_list = []
	
	property_regex_comment = re.compile('([#]{1,1})([\s]*)([\w.]+?)([\s]*)([=]{1,1})(.*)',re.S)
	property_regex_no_comment = re.compile('([\w.]+?)([\s]*)([=]{1,1})(.*)',re.S)
	range_regex = re.compile('(Range:[\s]*?)(.*)')

	storage_dict = {}

	profiles = collections.OrderedDict()
	profiles["SERVER"] = "API"
	profiles["REMOTESERVICE"] = "RS"
	profiles["V2VSERVICES"] = "V2V"
	profiles["M OUTBOUND API"] ="OA"

	# Read git properties file line by line
#	with codecs.open(os.path.json(inputDir,propertyFile), 'r', 'utf-8') as f:
	with codecs.open(propertyFile, 'r', 'utf-8') as f:
		content = f.readlines()
	# Prepare the properties for wiki output and sample files	
	(storage_dict,sample_files) = storeProperties(content,property_regex_comment,property_regex_no_comment,range_regex,profiles,fdetails,sample_files)

	# Reorganise the storage dict by categories for the wiki
	categories = wikiCategories(storage_dict)

	# output the sample files
	for pf in profiles:
		pf_sample = fdetails.fprefix + profiles[pf].lower() + "_" + fdetails.fdate + fdetails.fsuffix	
		ps = open_if_not_existing(pf_sample)
		if ps:
			sample_message_list = getSampleMessage(profiles[pf],wikiVersion)
			for sw in sample_message_list:
				ps.write(sw)
			ps.write("\n")
			for pl in sample_files[profiles[pf]]:
				ps.write(pl.encode('utf8'))
			ps.close

	# output a storage dict with the properties indexed by property name		
	js = open_if_not_existing("fwg.json")
	if js:
		json.dump(storage_dict, js)
		js.close

	# prepare the json dict for mustache output	
	wiki_output['headingLinks'] = wikiHeadings(profiles,fdetails)			
	wiki_output['categories'] = categories		

	# output a json file with the full mustache format
	jwf = open_if_not_existing("fwp.json")
	if jwf:
		json.dump(wiki_output, jwf)
		jwf.close
	#tfilepath = os.path.join(adminSubdir,template)
	
	# Render the wiki file with mustache
	mustacheTemplate = codecs.open("wiki_properties_template.mustache", 'r', 'utf-8').read()
	efo = pystache.render(mustacheTemplate, wiki_output).encode('utf8', 'xmlcharrefreplace')
	pof = "properties_out_" + td + ".txt"
	ef = open_if_not_existing(pof)
	if ef:
		ef.write(efo)
		ef.close()		


# Calls the main() function
if __name__ == '__main__':
	main()