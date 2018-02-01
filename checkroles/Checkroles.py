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
	methodSearchString = '(?<=Synopsis).*?((DELETE|GET|POST|PUT){1,1}.*?)(<br)'	
	foundMethods = re.findall(methodSearchString,wikiContent,re.DOTALL)
	if foundMethods:
		print "Found method: %s" % str(foundMethods)
#	   sff = fnm.group(1)    
	return foundMethods

def searchForRoles(securityHttpBeansContent):
# Search for methods on the page
# Maybe it doesn't need to have ROLE
#	methodSearchString = '"Synopsis".*?(GET|PUT|POST|DELETE).*?(http://example.com/api)(.*?)<(.*?)"Roles Required|Roles required".*?(ROLE_([A-Z,_]).*?)<'
	roleSearchString = '(?<=pattern=")(.*?)\"\smethod=\"(.*?)\"\saccess=\"(.*?)\"'
	foundRoles = ""
	foundRoles = re.findall(roleSearchString,securityHttpBeansContent)
	print foundRoles
#	if foundRoles:
#	print "Found role: %s" % foundRoles[0]
#	   sff = fnm.group(1)    
	return foundRoles


def cleanRestMethod(restMethod):
# Get rid of HTML poo and XML poo	
	stringsToClean = {"<span.*?>","</span>","<u>","</u>","<a.*?>","</a.*?>"}
	for stringClean in stringsToClean:
		restMethod = re.sub(stringClean,"",restMethod)
		restMethod = re.sub("&nbsp;"," ",restMethod)
	return restMethod	


def main():

	securityHttpBeans = openContentFile("security-http-beans.txt")
	securityRolesList = searchForRoles(securityHttpBeans)

	securityRoleDict = {}
	for (url,option,roles) in securityRolesList:
		securityOptionUrl = option + " " + url
		securityRoleDict[securityOptionUrl] = roles

	for poo,poopoo in securityRoleDict.iteritems():
		print "poo: %s poopoo: %s " % (poo,poopoo)		


	inputSubdir = "v4210files"
	wikiFileList = []	
	wikiFileList = getContentFileNames(inputSubdir)
	wikiFileMethodDict = {}

	for wikiFile in wikiFileList:
		wikiContent = ""
		wikiContent = openContentFile(wikiFile)
		wikiFileMethodDict[wikiFile] = []
#		print ("wikiContent: %s" % wikiContent)
		restMethodsList = searchForMethods(wikiContent)
		for fullRestMethod in restMethodsList:
			print "restOption: %s" % fullRestMethod[1]
			print "restMethod: %s" % fullRestMethod[0]
			restOption = fullRestMethod[1]
			restMethod = fullRestMethod[0]
			restMethod = cleanRestMethod(restMethod)
			print "restMethod: %s" % restMethod
# Remove the http://blah.de.blah			
			restMethod = re.sub("DELETE|GET|POST|PUT","",restMethod)
			restMethod = restMethod.strip()
			restMethod = re.sub("http://.*?/","/",restMethod)
			restMethod = restMethod.strip()			
			print "restMethod: %s" % restMethod
# Replace the names with asterisks / stars			
			restMethod = re.sub("\{.*?\}","*",restMethod)	
			print "restMethod: %s" % restMethod
# Discard weird stuff
			if '<' in restMethod or '>' in restMethod or '_' in restMethod or ':'  in restMethod:
				continue		
		
			restOptionMethodList = []
			restOptionMethodList.append(restOption)
			restOptionMethodList.append(restMethod)			
			wikiFileMethodDict[wikiFile].append(restOptionMethodList)
#		print "Method %s" % str(methodsList)
	
	for wikiFileName in wikiFileMethodDict:
		print "d: %s " % wikiFileName
		wikiFileMethodList = wikiFileMethodDict[wikiFileName]
		for wikiMethod in wikiFileMethodList:
#			print "wm: %s " % wikiMethod
			wikiOptionUrl = " ".join(wikiMethod)
			print "wo: %s " % wikiOptionUrl

			if wikiOptionUrl in securityRoleDict:
				print "DONE: %s : %s" % (wikiOptionUrl,securityRoleDict[wikiOptionUrl])





# Calls the main() function
if __name__ == '__main__':
	main()