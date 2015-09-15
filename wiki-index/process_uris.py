#!/usr/bin/python -tt

import sys
import re
import os


def main():

	pages_uris = "uris_pages.txt"

	with open(pages_uris, 'r') as pages_uris_file:
		puf = pages_uris_file.readlines()

	print ("|| Abiquo Main Resource URI || Resource Wiki Page Link ||")	

	for pu in puf:
		pageName = re.findall ('(?<=/)([A-Za-z0-9\s]*?)([\-])',pu)
		pageId = re.findall('(?<=\-)([0-9]*?)([:])',pu)
		uris = re.findall('(?<=:)(.*?)([<])',pu)
#		print pageId
#		print uris
		(pn,ns) = pageName[0]
		(pi,ps) = pageId[0]
		(ur,us) = uris[0]
		up = re.sub("\{","\\\{",ur)

		print "| %s | [%s] |" % (up,pn)
		# print ("|| h6. ", entityheader[s], " || || ||")

  
# Calls the main() function
if __name__ == '__main__':
	main()