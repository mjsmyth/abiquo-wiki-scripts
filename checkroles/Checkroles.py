#Checkroles.py
'''<h4>Get allocation rules</h4>
<p>Get global rules or datacenter rules if the datacenter identifier is supplied.</p>
<p><strong>Synopsis:</strong> <span style="text-decoration: underline;">GET http://example.com/api/admin/rules</span> <br /> <strong>Roles Required:</strong> ROLE_PHYS_DC_RETRIEVE_DETAILS<br />

Read each file (or each file with name ending in Resource)?

Do a multi-line regex search for:

<h4>Title</h4> What are we going to do with this? 
<p><strong>Synopsis:</strong> <span style="text-decoration: underline;">GET http://example.com/api/admin/rules/fitPolicy/{fitPolicy}</span><br />
<strong>Roles Required:</strong> ROLE_PHYS_DC_RETRIEVE_DETAILS<br />


Search for '"Synopsis .*? (GET|PUT|POST|DELETE) .*? (http://example.com/api) (.*?)< (.*?) "Roles Required|Roles required" .*? (ROLE_([A-Z,_]))<'
print $0'''

import glob
import os
import re


def getContentFileNames(inputSubdir):
	# read all example files in the directory
	allFiles = {}
#	paths = {"Ex *","DELETE*","GET*","POST*","PUT*"}
	paths = {"*Resource-*"}
	allFiles = []
	for aPath in paths:
		aFullPath = ""
		print ("aPath: %s" % aPath) 
		aFullPath = inputSubdir + "/" + aPath
		allFiles.extend(glob.glob(aFullPath))
		print allFiles[-2:-1]
	return(allFiles) 


def openContentFile(contentFileName):
#	contentFileName = os.path.join(subdir,contentFileNameInput)
#	logging.info("c_file_name: %s " % c_file_name)
	newContent = ""
	try: 
		newContentFile = open(contentFileName,'r')	
		newContent = newContentFile.read()
#		logging.info("Read content file okay")
		newContentFile.close()
	except:
#		logging.info("Could not open content file %s " % c_file_name)
 		print("Could not open content file %s " % contentFileName)
	return newContent



def searchForMethods(wikiContent):
# Search for methods on the page
# Maybe it doesn't need to have ROLE
#	methodSearchString = '"Synopsis".*?(GET|PUT|POST|DELETE).*?(http://example.com/api)(.*?)<(.*?)"Roles Required|Roles required".*?(ROLE_([A-Z,_]).*?)<'
	methodSearchString = '(?<=Synopsis).*?((DELETE|GET|POST|PUT){1,1}.*?)<br'
	foundMethods = re.findall(methodSearchString,wikiContent,re.DOTALL)
	if foundMethods:
		print "Found %s" % str(foundMethods)
#	   sff = fnm.group(1)    
	return foundMethods

def cleanRestMethod(restMethod):
	stringsToClean = {"&nbsp;","<span.*?>","</span>","<u>","</u>","<a.*?>","</a.*?>",""}
	for stringClean in stringsToClean:
		restMethod = re.sub(stringClean,"",restMethod)
	return restMethod	


def main():
	inputSubdir = "v4210pages"
	wikiFileList = []	
	wikiFileList = getContentFileNames(inputSubdir)
	wikiFileMethodDict = {}
	for wikiFile in wikiFileList:
		wikiContent = ""
		wikiContent = openContentFile(wikiFile)
		wikiFileMethodDict[wikiFile] = []
#		print ("wikiContent: %s" % wikiContent)
		restMethodsList = searchForMethods(wikiContent)
		for restMethod in restMethodsList:
			print "restMethod: %s" % restMethod[0]
			wikiFileMethodDict[wikiFile].append(cleanRestMethod(restMethod[0]))
#		print "Method %s" % str(methodsList)
	for d in wikiFileMethodDict:
		print wikiFileMethodDict[d]
# Calls the main() function
if __name__ == '__main__':
	main()