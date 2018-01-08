#!/usr/bin/python -tt

import sys
import re
import os


def main():

	list_dtos = "v421_data_media_types_list.txt"

	with open(list_dtos, 'r') as list_dtos_file:
		ldto = list_dtos_file.readlines()

	print ("|| Abiquo Data Media Type File || Data Media Type ||")	

	ldtop = []
	for dto in ldto:
#		dtoName = re.findall ('(?=\.java)([A-Za-z]*)',dto)
		dtoName = re.findall ('([A-Za-z]*?)(\.java)',dto)
		dtoId = re.findall('(?<=\")(.+)(\")',dto)
#		uris = re.findall('(?<=:)(.*?)([<])',pu)
#		print pageId
#		print uris
		(dn,dndd) = dtoName[0]
		(di,didd) = dtoId[0]
#		(ur,us) = uris[0]
#		up = re.sub("\{","\\\{",ur)
		ldtop.append((dn,di))
	sldtop = sorted(ldtop)
	for sdtop in sldtop:
		print "| %s | %s |" % (sdtop[0],sdtop[1])
		# print ("|| h6. ", entityheader[s], " || || ||")
	
  
# Calls the main() function
if __name__ == '__main__':
	main()
