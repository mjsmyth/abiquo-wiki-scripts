#!/usr/bin/python2 -tt
# read the privilegesMgr.js file
# get the list of privilegeGroups and 
# self.clientData

import os
import codecs
import re
import collections

def main():
	privgroupnames = collections.OrderedDict()

	inputDir = "input_files"
	privUIFile = "privilegesMgr.js"
	with codecs.open(os.path.join(inputDir,privUIFile), 'r', 'utf-8') as f:
		data=f.read().replace('\n', '')

	names = re.findall('\sis([\w]*?)\s{1,1}([^,]*?),',data,re.U) 

	for n in names:
		privgroupnames[n[0]] = []
		print ("Event group: %s " % n[0])
		privs = re.findall("(?<=self.name.indexOf\(\')([\w_]*?)(\')",n[1],re.U)
		for p in privs:
			print("ho: %s" % p[0])
			privgroupnames[n[0]].append(p[0])

	for x in privgroupnames:
		print("x: %s" % x)
		print("privgroupnames: %s" % privgroupnames[x])

# Calls the main() function
if __name__ == '__main__':
  main()
