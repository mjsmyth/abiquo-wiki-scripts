#ParseComments.py
'''<h4>Get allocation rules</h4>
<p>Get global rules or datacenter rules if the datacenter identifier is supplied.</p>
<p><strong>Synopsis:</strong> <span style="text-decoration: underline;">GET http://example.com/api/admin/rules</span> <br /> <strong>Roles Required:</strong> ROLE_PHYS_DC_RETRIEVE_DETAILS<br />

Read each file (or each file with name ending in Resource)?

Do a multi-line regex search for:

<h4>Title</h4> Description 
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
#		print ("aPath: %s" % aPath) 
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



def searchForHeadingsAndComments(wikiContent):
# Search for all headings with text after them on the page
	mainHeadingSearchString = '<h[1-3]>(.*?)</h[1-3]>(.*?)(?=<h)'
	headingAndCommentSearchString = '(?:(?<=<h4>)|(?<=<h5>))(.*?)(?:</h5>|</h4>)(.*?)(?:Synopsis).*?(((DELETE|GET|POST|PUT){1,1}.*?)(?:<br|</li|</p|\?).*?((?:(?:(?:[A-Z]{1,})(?:(?:[_]{1,1})(?:[A-Z]{1,}))+)(?:\,|\s|"&nbsp;"|\n)*))+)'
	foundMainHeadings = re.findall(mainHeadingSearchString,wikiContent,re.DOTALL)
	foundHeadingsAndComments = re.findall(headingAndCommentSearchString,wikiContent,re.DOTALL)
#	if foundMethods:
#		print "Found method: %s" % str(foundMethods)
#	   sff = fnm.group(1)    
	return (foundMainHeadings,foundHeadingsAndComments)


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
#	print foundRoles
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

def cleanWikiStorageFormat(descriptionText):
# Get rid of Wiki storage format poo
	linkString = "<ac:link(?: ac:anchor=\"(.*?)\")?>.*?<ri:page ri:content-title=\"(.*?)\"/>.*?</ac:link>"
#	linkString2 = "<ac:link ac:anchor=\"(.*?)\">.*?<ri:page ri:content-title=\"DatacenterRepositoryResource\"/>"
# <p>This method works with paging. Check out <ac:link><ri:page ri:content-title="Basic Behaviors"/></ac:link> for information about how it works</p>
	linksInString = re.findall(linkString,descriptionText)
	linkStringInMarkdown = ""
	if linksInString:
		for wikiFormatLink in linksInString:
# if no anchor text, make it the page name			
			anchorText = wikiFormatLink[2][:]
			anchorText = wikiFormatLink[1][:]
			pageName = wikiFormatLink[2][:]
			if not re.match("Resource$",pageName): 
				pageNameWordList = pageName.split(" ")
				pageNamePlus = "+".join(pageNameWordList)	
				pageLink = "https://wiki.abiquo.com/display/doc/" + pageNamePlus
				# [I'm an inline-style link with title](https://www.google.com "Google's Homepage")
				LinkStringInMarkdown = "[" + anchorText + "] (" + pageLink + " \"" + "Abiquo wiki" + "\""
			else:
				LinkStringInMarkdown = "[" + anchorText + "] (" + anchorText + " \"" + "Abiquo API docs" + "\")"
			descriptionText = re.sub(wikiFormatLink,linkStringInMarkdown,descriptionText,count=1)	
	stringsToClean = {"<ac:.*?>","</ac:.*?>","<ri:.*?>"}
	for stringClean in stringsToClean:
		descriptionText = re.sub(stringClean,"",descriptionText)
		descriptionText = re.sub("&nbsp;"," ",descriptionText)
	return descriptionText	


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
#	docPresentFile = open("docPresentFile.txt","w+")

	for securityMethod,securityRoles in securityRoleDict.iteritems():
		roleString = "sMethod: " + securityMethod + " sRoles: " + securityRoles + "\n"
#		print "sMethod: %s sRoles: %s " % (securityMethod,securityRoles)
		roleFile.write(roleString)

	inputSubdir = "v44wikiexport"
	wikiFileList = []	
	wikiFileList = getContentFileNames(inputSubdir)
	wikiFileCommentDict = {}
	wikiFileHeaderDict = {}
	wikiMethodsSimpleList = []
	wikiPageLinkDict = {}

	for wikiFile in wikiFileList:
		wikiContent = ""
		wikiContent = openContentFile(wikiFile)
		wikiFileCommentDict[wikiFile] = []
		wikiPageLink = wikiContent.split("**")
		wikiPageLinkDict[wikiFile] = wikiPageLink[1] 
#		print ("wikiContent: %s" % wikiContent)
		(mainHeadingList,headingCommentList) = searchForHeadingsAndComments(wikiContent) 
		# PROCESS THE HEADING - first text under a heading 1-3 before another heading
#		print "Method %s" % str(methodsList)
		resourceHeading = []
		if (len(mainHeadingList) > 0): 
			resourceHeading = mainHeadingList[0]
# 			print "mainHeadingList[0]: %s" % resourceHeading[0]			
		resourceDescription = ''
		if len(resourceHeading) > 1:
			resourceDescription = resourceHeading[1]
#			print "resourceDescription: %s" % str(resourceDescription)	
		wikiFileHeaderDict[wikiFile] = resourceDescription[:]

		for fullRestMethod in headingCommentList:
#			print "restOption: %s" % fullRestMethod[2]
#			print "restMethod: %s" % fullRestMethod[1]
			methodHeader = fullRestMethod[0]
			methodDescription = fullRestMethod[1]
			restOption = fullRestMethod[4]
			restMethod = fullRestMethod[3]
			fullRestMethodCopy = fullRestMethod[2][:]
			foundRolesInWiki = re.findall("(?:(?:((?:[A-Z]{1,})(?:(?:[_]{0,1})(?:[A-Z]{1,}))+)(?:\,|\s|'&nbsp;'|\n)*))+?",fullRestMethodCopy)
#			print("foundRolesInWiki: %s" % foundRolesInWiki)
			restMethod = cleanRestMethod(restMethod)
			methodHeader = cleanRestMethod(methodHeader)
			methodDescription = cleanRestMethod(methodDescription)
			methodDescription = cleanWikiStorageFormat(methodDescription)

#Wiki: /cloud/virtualdatacenters/1/virtualappliances/1/virtualmachines/1/action/relocatecandidates
#Wiki: /cloud/virtualdatacenters/1/virtualappliances/1/virtualmachines/1/action/relocate
#Wiki: /cloud/virtualdatacenters/\*/virtualappliances/*/virtualmachines/*/action/clone]

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
			restMethod = re.sub("\\\\\\*","*",restMethod)
			restMethod = re.sub("1","*",restMethod)
			restMethod = re.sub("]","",restMethod)

			methodHeader = re.sub("</strong>","",methodHeader)	
			methodDescription = re.sub("<p><strong>","",methodDescription)


#			print "Header: %s" % methodHeader
#			print "Description: %s" % methodDescription
#			print "restMethod: %s" % restMethod
# Discard weird stuff
 			if '<' in restMethod or '>' in restMethod or '_' in restMethod or ':'  in restMethod:
				wikiResultString = "Discarded: " + restMethod + "\n"
				wikiCheckFile.write(wikiResultString)
				continue	
			checkNotRoleList = {'ROUND_ROBIN' , 'LEAST_CONNECTIONS' , 'SOURCE_IP' , 'IP_HASH' , 'LEAST_CONN'} 		
#			if any (x in str(foundRolesInWiki) for x in checkNotRoleList):
#				wikiResultString = "Discarded: " + restMethod + "\n"
#				wikiCheckFile.write(wikiResultString)
#				continue
	
			wikiResultString = "Wiki: " + restMethod + "\n"	
			wikiCheckFile.write(wikiResultString)
			restOptionMethodList = []
			restOptionMethodList.append(restOption)
			restOptionMethodList.append(restMethod)
			restOptionMethodList.append(methodHeader)
 			restOptionMethodList.append(methodDescription)
	#		restOptionMethodList.append(foundRolesInWiki)
	#		print "restOption processed: %s" % restOption
	#		print "restMethod processed: %s" % restMethod
	#		print "Rolesfound processed: %s" % foundRolesInWiki
			wikiFileCommentDict[wikiFile].append(restOptionMethodList)



	
	for wikiFileName in wikiFileCommentDict:
		print "\n%s " % wikiFileName 
		wikiFileNameString = "File: " + wikiFileName + "\n"
		wikiMethodFile.write(wikiFileNameString)
		wikiPageLinkString = wikiPageLinkDict[wikiFileName]
		print "\n%s " % wikiPageLinkString
		wikiMethodFile.write(wikiPageLinkString)
		wikiMainHeader = ""
		wikiFileMethodList = wikiFileCommentDict[wikiFileName]
		print "\n\t %s \n" % wikiFileHeaderDict[wikiFileName]
		for wikiMethod in wikiFileMethodList:
#			print "wikiMethod: %s " % wikiMethod
			wikiOptionUrl = " ".join(wikiMethod[0:2])
			print "\t %s " % wikiOptionUrl
			wikiHeaderString = str(wikiMethod[2])
			print "\t\t %s " % wikiHeaderString
			wikiDescriptionString = str(wikiMethod[3])
 			print "\t\t %s \n" % wikiDescriptionString
			wikiMethodsSimpleList.append(wikiOptionUrl)
#			securityString = ""
#			if wikiOptionUrl in securityRoleDict:
#				securityString = "IN: " + wikiOptionUrl + " : " + securityRoleDict[wikiOptionUrl] + " "
#				print "DONE: %s : %s" % (wikiOptionUrl,securityRoleDict[wikiOptionUrl])
#			else:
#				securityString = "NO: " + wikiOptionUrl + " "
#				print "NOT: %s " % (wikiOptionUrl)	
			wikiMethodFile.write(wikiHeaderString + "\n")	
			wikiMethodFile.write(wikiDescriptionString + "\n")

# Audit the documentation
#	docPresentString = ""
#	for wikiOptionUrl in securityRoleDict:
#		if wikiOptionUrl in wikiMethodsSimpleList:
#			docPresentString = "Found: " + wikiOptionUrl + "\n"
#		else:
#			docPresentString = "Nodoc: " + wikiOptionUrl + "\n"	
#		docPresentFile.write(docPresentString)	

	wikiMethodFile.close()
	wikiCheckFile.close()
	roleFile.close()	
#	docPresentFile.close()

# Calls the main() function
if __name__ == '__main__':
	main()
