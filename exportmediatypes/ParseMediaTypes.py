#ParseMediaTypes.py
'''<h5>Category Media Type</h5>
<h5> | EOF

'''

import os
import re



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



def searchForMediaTypes(wikiContent):
# Search for media types on the page

#	methodSearchString = '<h5>(.*?)\sMedia Type.*?;application/vnd.abiquo.(.*?)\+json.*?<td>(.*?)((?=<h5>)|\Z)'
	mediaTypeSearchString = '.*?([\w]*?)(?:\s|\&nbsp\;)(?=Media Type).*?(?<=application/vnd.abiquo.)(.*?)(?=\+json).*?((?:<td>|<td colspan=\"1\">).*</td>)'	
	mediaTypeBlocks = wikiContent.split("<h5>")
	foundMediaTypes = []
	for mediaTypeBlock in mediaTypeBlocks:
		foundMediaTypes.append(re.findall(mediaTypeSearchString,mediaTypeBlock,re.DOTALL))	    
#	foundMediaTypes = re.findall(mediaTypeSearchString,wikiContent,re.DOTALL)
#	if foundMediaTypes:
#		print "Found mediatype: %s" % str(foundMediaTypes)
#	   sff = fnm.group(1)    
	return foundMediaTypes

def searchForAttributes(mediaTypeName,mediaTypeContent):
# Search for attributes in the media type
	attributeSearchString = '(?:<td>|<td colspan="1">)(?:<p>)?(.*?)(?:</p>)?</td>.*(?:(?<=<td>)|(?<=<td colspan=\"1\">))(?:<p>)?(.*?)(?:</p>)?</td>'
#	attributeSearchString = '<p>(.*?)</p>.*(?<=<p>)(.*?)</p>'
# If there's more than one table, only use the first one, as the second one has enumerations
# Exclude entities that have sub media types such as pricingtemplate and backuppolicydefinition	  
	if (mediaTypeName == 'pricingtemplate' or mediaTypeName == 'backuppolicydefinition'): 
		mediaTypeOnly = mediaTypeContent[:]	
	else:
		tableBlocks = mediaTypeContent.split("</table>")
		mediaTypeOnly = tableBlocks[0]

	attributeBlocks = mediaTypeOnly.split("</tr>")
	foundAttributes = []
	for attributeBlock in attributeBlocks:
		foundAttributes.append (re.findall(attributeSearchString,attributeBlock,re.DOTALL))

#	foundAttributes = re.findall(attributeSearchString,mediaTypeContent)
# OJO	for rawRoles in foundRoles:
# OJO		rawRoles = [y.replace("\n","") for y in rawRoles] 
# OJO		rawRoles = [x.replace("ROLE_","") for x in rawRoles] 
#	print foundAttributes
#	if foundRoles:
#	print "Found role: %s" % foundRoles[0]
#	   sff = fnm.group(1)    
	return foundAttributes


#def cleanRestMethod(restMethod):
# Get rid of HTML poo and XML poo	
#	stringsToClean = {"<span.*?>","</span>","<u>","</u>","<a.*?>","</a.*?>"}
#	for stringClean in stringsToClean:
#		restMethod = re.sub(stringClean,"",restMethod)
#		restMethod = re.sub("&nbsp;"," ",restMethod)
#	return restMethod	


def main():

	dataMediaTypes = openContentFile("/home/mjsmyth/a3/Abiquo_Data_Media_Types-27076188")
	dataMediaTypesList = searchForMediaTypes(dataMediaTypes)

	mediaTypeDict = {}
	for DMT in dataMediaTypesList:
		for	(dtoName,mediaTypeName,attributeTableText) in DMT:
	#		print "dtoName: %s" % dtoName
	#		print "mediaTypeName: %s" % mediaTypeName
			mediaTypeDict[dtoName] = {}
			mediaTypeDict[dtoName]['mediaTypeName'] = mediaTypeName
	#		mediaTypeDict[dtoName]['attributes'] = {}
			attributeList = searchForAttributes(mediaTypeName,attributeTableText)
			attributeDict = {}
			for attribute in attributeList:
				for (attributeName,attributeDesc) in attribute:
					attributeDict[attributeName] = attributeDesc
				mediaTypeDict[dtoName]['attributes'] = attributeDict	

	for dtoN,mediaTypeOutputDict in mediaTypeDict.iteritems():
 		print "DTO: %s " % dtoN
 		print "DMT: %s " % mediaTypeOutputDict['mediaTypeName']

 		for attributeNameOutput, attributeDescOutput in mediaTypeOutputDict['attributes'].iteritems():
 			print "\t %s: %s" % (attributeNameOutput,attributeDescOutput)	
			
# 	for (url,option,roles) in securityRolesList:
# 		securityOptionUrl = option + " " + url
# 		securityRoleDict[securityOptionUrl] = roles

# 	roleFile = open("roleFile.txt", "w+")
# 	wikiMethodFile = open("wikiFile.txt", "w+")
# 	wikiCheckFile = open("wikiCheckFile.txt", "w+")
# 	docPresentFile = open("docPresentFile.txt","w+")

# 	for securityMethod,securityRoles in securityRoleDict.iteritems():
# 		roleString = "sMethod: " + securityMethod + " sRoles: " + securityRoles + "\n"
# #		print "sMethod: %s sRoles: %s " % (securityMethod,securityRoles)
# 		roleFile.write(roleString)

# 	inputSubdir = "v4210pages"
# 	wikiFileList = []	
# 	wikiFileList = getContentFileNames(inputSubdir)
# 	wikiFileMethodDict = {}
# 	wikiMethodsSimpleList = []

# 	for wikiFile in wikiFileList:
# 		wikiContent = ""
# 		wikiContent = openContentFile(wikiFile)
# 		wikiFileMethodDict[wikiFile] = []
# #		print ("wikiContent: %s" % wikiContent)
# 		restMethodsList = searchForMethods(wikiContent)
# 		for fullRestMethod in restMethodsList:
# 			print "restOption: %s" % fullRestMethod[1]
# 			print "restMethod: %s" % fullRestMethod[0]
# 			restOption = fullRestMethod[1]
# 			restMethod = fullRestMethod[0]
# 			restMethod = cleanRestMethod(restMethod)
# #			print "restMethod: %s" % restMethod
# # Remove the http://blah.de.blah			
# 			restMethod = re.sub("DELETE|GET|POST|PUT","",restMethod)
# 			restMethod = restMethod.strip()
# 			restMethod = re.sub("http://.*?/api","",restMethod)
# 			restMethod = restMethod.strip()			
# #			print "restMethod: %s" % restMethod
# # Replace the names with asterisks / stars			
# 			restMethod = re.sub("\{.*?\}","*",restMethod)	
# 			restMethod = re.sub(" ","",restMethod)
# 			restMethod = re.sub("<strong>RolesRequired:.*?</strong>.*","",restMethod)
# #Wiki: /cloud/virtualdatacenters/1/virtualappliances/1/virtualmachines/1/action/relocatecandidates
# #Wiki: /cloud/virtualdatacenters/1/virtualappliances/1/virtualmachines/1/action/relocate
# #Wiki: /cloud/virtualdatacenters/\*/virtualappliances/*/virtualmachines/*/action/clone]
# 			restMethod = re.sub("\\\\\\*","*",restMethod)
# 			restMethod = re.sub("1","*",restMethod)
# 			restMethod = re.sub("]","",restMethod)


# #			print "restMethod: %s" % restMethod
# # Discard weird stuff
# 			if '<' in restMethod or '>' in restMethod or '_' in restMethod or ':'  in restMethod:
# 				wikiResultString = "Discarded: " + restMethod + "\n"
# 				wikiCheckFile.write(wikiResultString)
# 				continue		
# 			wikiResultString = "Wiki: " + restMethod + "\n"	
# 			wikiCheckFile.write(wikiResultString)
# 			restOptionMethodList = []
# 			restOptionMethodList.append(restOption)
# 			restOptionMethodList.append(restMethod)			
# 			wikiFileMethodDict[wikiFile].append(restOptionMethodList)
# #		print "Method %s" % str(methodsList)
	
# 	for wikiFileName in wikiFileMethodDict:
# #		print "d: %s " % wikiFileName 
# 		wikiFileNameString = "File: " + wikiFileName + "\n"
# 		wikiMethodFile.write(wikiFileNameString)
# 		wikiFileMethodList = wikiFileMethodDict[wikiFileName]
# 		for wikiMethod in wikiFileMethodList:
# #			print "wm: %s " % wikiMethod
# 			wikiOptionUrl = " ".join(wikiMethod)
# #			print "wo: %s " % wikiOptionUrl
# 			wikiMethodsSimpleList.append(wikiOptionUrl)
# 			securityString = ""
# 			if wikiOptionUrl in securityRoleDict:
# 				securityString = "IN: " + wikiOptionUrl + " : " + securityRoleDict[wikiOptionUrl] + "\n"
# #				print "DONE: %s : %s" % (wikiOptionUrl,securityRoleDict[wikiOptionUrl])
# 			else:
# 				securityString = "NO: " + wikiOptionUrl + "\n"
# #				print "NOT: %s " % (wikiOptionUrl)	
# 			wikiMethodFile.write(securityString)	

# # Audit the documentation
# 	docPresentString = ""
# 	for wikiOptionUrl in securityRoleDict:
# 		if wikiOptionUrl in wikiMethodsSimpleList:
# 			docPresentString = "Found: " + wikiOptionUrl + "\n"
# 		else:
# 			docPresentString = "Nodoc: " + wikiOptionUrl + "\n"	
# 		docPresentFile.write(docPresentString)	

# 	wikiMethodFile.close()
# 	wikiCheckFile.close()
# 	roleFile.close()	
# 	docPresentFile.close()

# Calls the main() function
if __name__ == '__main__':
	main()