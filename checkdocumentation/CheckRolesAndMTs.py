#CheckRoleAndMTss.py
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
#		print allFiles[-2:-1]
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
#	methodSearchString = '(?<=Synopsis).*?((DELETE|GET|POST|PUT){1,1}.*?)(<br|</li|</p|\?).*?((?:[A-Z]{1,})((?:[_]{1,1})(?:[A-Z]{1,}))+)'
#	wikiRoleSearchString = ((?:[A-Z]{1,})((?:[_]{1,1})(?:[A-Z]{1,}))+)
	methodSearchString = '(?<=Synopsis).*?(((DELETE|GET|POST|PUT){1,1}.*?)(?:<br|</li|</p|\?).*?((?:(?:(?:[A-Z]{1,})(?:(?:[_]{1,1})(?:[A-Z]{1,}))+)(?:\,|\s|"&nbsp;"|\n)*))+)'

	foundMethods = re.findall(methodSearchString,wikiContent,re.DOTALL)
#	if foundMethods:
#		print "Found method: %s" % str(foundMethods)
#	   sff = fnm.group(1)    
	return foundMethods

def searchForRoles(securityHttpBeansContent):
# Search for methods on the page
# Maybe it doesn't need to have ROLE
#	methodSearchString = '"Synopsis".*?(GET|PUT|POST|DELETE).*?(http://example.com/api)(.*?)<(.*?)"Roles Required|Roles required".*?(ROLE_([A-Z,_]).*?)<'
	roleSearchString = '(?<=pattern=")(.*?)\"\smethod=\"(.*?)\"[\s\n]*?access=\"(.*?)\"'
	foundRoles = ""  
	foundRoles = re.findall(roleSearchString,securityHttpBeansContent)
	for rawRoles in foundRoles:
		rawRoles = [y.replace("\n","") for y in rawRoles] 
		rawRoles = [x.replace("ROLE_","") for x in rawRoles] 
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

	securityHttpBeans = openContentFile("/home/mjsmyth/platform/api/src/main/resources/springresources/security/security-http-beans.xml")
	securityRolesList = searchForRoles(securityHttpBeans)

	securityRoleDict = {}
	for (url,option,roles) in securityRolesList:
		securityOptionUrl = option + " " + url
		securityRoleDict[securityOptionUrl] = roles

	roleFile = open("roleFile.txt", "w+")
	wikiMethodFile = open("wikiFile.txt", "w+")
	wikiCheckFile = open("wikiCheckFile.txt", "w+")
	docPresentFile = open("docPresentFile.txt","w+")

	for securityMethod,securityRoles in securityRoleDict.iteritems():
		roleString = "sMethod: " + securityMethod + " sRoles: " + securityRoles + "\n"
#		print "sMethod: %s sRoles: %s " % (securityMethod,securityRoles)
		roleFile.write(roleString)

	inputSubdir = "v4212pages"
	wikiFileList = []	
	wikiFileList = getContentFileNames(inputSubdir)
	wikiFileMethodDict = {}
	wikiMethodsSimpleList = []

	for wikiFile in wikiFileList:
		wikiContent = ""
		wikiContent = openContentFile(wikiFile)
		wikiFileMethodDict[wikiFile] = []
#		print ("wikiContent: %s" % wikiContent)
		restMethodsList = searchForMethods(wikiContent)
		for fullRestMethod in restMethodsList:
#			print "restOption: %s" % fullRestMethod[2]
#			print "restMethod: %s" % fullRestMethod[1]
			restOption = fullRestMethod[2]
			restMethod = fullRestMethod[1]
			fullRestMethodCopy = fullRestMethod[0][:]
			foundRolesInWiki = re.findall("(?:(?:((?:[A-Z]{1,})(?:(?:[_]{1,1})(?:[A-Z]{1,}))+)(?:\,|\s|'&nbsp;'|\n)*))+?",fullRestMethodCopy)
#			print("foundRolesInWiki: %s" % foundRolesInWiki)
			restMethod = cleanRestMethod(restMethod)
#			print "restMethod: %s" % restMethod
# Remove the http://blah.de.blah			
			restMethod = re.sub("DELETE|GET|POST|PUT","",restMethod)
			restMethod = restMethod.strip()
			restMethod = re.sub("http://.*?/api","",restMethod)
			restMethod = restMethod.strip()			
#			print "restMethod: %s" % restMethod
# Replace the names with asterisks / stars			
			restMethod = re.sub("\{.*?\}","*",restMethod)	
			restMethod = re.sub(" ","",restMethod)
#			restMethod = re.sub("<strong>Roles Required:.*?</strong>","",restMethod)
			restMethod = re.sub("<strong>Roles required:","",restMethod)
			restMethod = re.sub("<strong>Roles Required:","",restMethod)
			restMethod = re.sub("</strong>","",restMethod)

#Wiki: /cloud/virtualdatacenters/1/virtualappliances/1/virtualmachines/1/action/relocatecandidates
#Wiki: /cloud/virtualdatacenters/1/virtualappliances/1/virtualmachines/1/action/relocate
#Wiki: /cloud/virtualdatacenters/\*/virtualappliances/*/virtualmachines/*/action/clone]


			restMethod = re.sub("\\\\\\*","*",restMethod)
			restMethod = re.sub("1","*",restMethod)
			restMethod = re.sub("]","",restMethod)


			print "restMethod: %s" % restMethod
# Discard weird stuff
			if '<' in restMethod or '>' in restMethod or '_' in restMethod or ':'  in restMethod:
				wikiResultString = "Discarded: " + restMethod + "\n"
				wikiCheckFile.write(wikiResultString)
				continue	
			checkNotRoleList = {'ROUND_ROBIN' , 'LEAST_CONNECTIONS' , 'SOURCE_IP' , 'IP_HASH' , 'LEAST_CONN'} 		
			if any (x in str(foundRolesInWiki) for x in checkNotRoleList):
				wikiResultString = "Discarded: " + restMethod + "\n"
				wikiCheckFile.write(wikiResultString)
				continue
	
			wikiResultString = "Wiki: " + restMethod + "\n"	
			wikiCheckFile.write(wikiResultString)
			restOptionMethodList = []
			restOptionMethodList.append(restOption)
			restOptionMethodList.append(restMethod)
			restOptionMethodList.append(foundRolesInWiki)
			print "restOption processed: %s" % restOption
			print "restMethod processed: %s" % restMethod
			print "Rolesfound processed: %s" % foundRolesInWiki
			wikiFileMethodDict[wikiFile].append(restOptionMethodList)
#		print "Method %s" % str(methodsList)
	
	for wikiFileName in wikiFileMethodDict:
		print "d: %s " % wikiFileName 
		wikiFileNameString = "File: " + wikiFileName + "\n"
		wikiMethodFile.write(wikiFileNameString)
		wikiFileMethodList = wikiFileMethodDict[wikiFileName]
		for wikiMethod in wikiFileMethodList:
			print "wikiMethod: %s " % wikiMethod
			wikiOptionUrl = " ".join(wikiMethod[0:2])
			print "wikiOptionURL: %s " % wikiOptionUrl
			wikiRoleString = str(wikiMethod[2])
			print "wikiRoleString: %s " % wikiRoleString
			wikiMethodsSimpleList.append(wikiOptionUrl)
			securityString = ""
			if wikiOptionUrl in securityRoleDict:
				securityString = "IN: " + wikiOptionUrl + " : " + securityRoleDict[wikiOptionUrl] + " "
#				print "DONE: %s : %s" % (wikiOptionUrl,securityRoleDict[wikiOptionUrl])
			else:
				securityString = "NO: " + wikiOptionUrl + " "
#				print "NOT: %s " % (wikiOptionUrl)	
			wikiMethodFile.write(securityString + " " + wikiRoleString + "\n")	
#			wikiMethodFile.write(wikiRoleString)

# Audit the documentation
	docPresentString = ""
	for wikiOptionUrl in securityRoleDict:
		if wikiOptionUrl in wikiMethodsSimpleList:
			docPresentString = "Found: " + wikiOptionUrl + "\n"
		else:
			docPresentString = "Nodoc: " + wikiOptionUrl + "\n"	
		docPresentFile.write(docPresentString)	

	wikiMethodFile.close()
	wikiCheckFile.close()
	roleFile.close()	
	docPresentFile.close()

# Calls the main() function
if __name__ == '__main__':
	main()