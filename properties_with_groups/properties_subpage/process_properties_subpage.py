#!/usr/bin/python2 -tt
#
# This script processes a properties subpage (in table format, found under the Include pages hierarchy in the wiki)
# It reads the fwg json version of the main properties file
# It finds any property names in the table and checks they are in the main properties file
# It presents the property descriptions from both locations and offers the chance to replace one or the other
#
# TODO: retrieve file from wiki and replace file in wiki?
#
import sys
import os
import json
import re
import collections
import pystache
import codecs
from copy import deepcopy

def main():
	td = "2016-09-28"
	fwgFile = "fwg.json." + td
	cnfFile = "OpenIDConnectProperties" + ".txt"
	inputDir = "/home/mjsmyth/abiquo-wiki-scripts/properties_with_groups/properties_subpage/"
	# Open the fwg file	
#	with codecs.open(fwgFile, 'r', 'utf-8') as fwg:
#		fwg_content = fwg.read()
	fwg = json.load(codecs.open(fwgFile, 'r', 'utf-8'))

	# Open the Confluence file
	with codecs.open(cnfFile, 'r', 'utf-8') as cnf:
		cnf_input = cnf.readlines()	
	print cnf_input
	cfn = []
	for cfi in cnf_input:
		cfi = cfi.rstrip("\n")
		cfi = cfi.lstrip()
		cfn.append(cfi)
	cnf_content = "".join(cfn)	
	print cnf_content

	# Find all property names in the confluence file - assumed to be all bold non-header table cells
	property_refs = re.findall("<tr><td><strong>(.*?)</strong></td><td>(.*?)</td></tr>",cnf_content)
	print (property_refs)

	for (prop,desc) in property_refs:
		desc = desc.strip('<p>')
		desc = desc.strip('</p>')
		if prop in fwg:
			print "prop %s \n L %s \n W %s" % (prop, desc, fwg[prop]['propertyDescription'])


# Calls the main() function
if __name__ == '__main__':
	main()