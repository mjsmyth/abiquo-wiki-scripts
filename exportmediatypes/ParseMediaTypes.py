#ParseMediaTypes.py
'''<h5>Category Media Type</h5>
<h5> | EOF

'''

import os
import re



def openContentFile(contentFileName):
#    contentFileName = os.path.join(subdir,contentFileNameInput)
#    logging.info("c_file_name: %s " % c_file_name)
    newContent = ""
    try: 
        newContentFile = open(contentFileName,'r')    
#        os.system("open '"+ contentFileName + "'")
        newContent = newContentFile.read()
#        logging.info("Read content file okay")
        newContentFile.close()
    except:
#        logging.info("Could not open content file %s " % c_file_name)
         print("Could not open content file %s " % contentFileName)
    return newContent


def searchForMediaTypes(wikiContent):
# Search for media types on the page
#    methodSearchString = '<h5>(.*?)\sMedia Type.*?;application/vnd.abiquo.(.*?)\+json.*?<td>(.*?)((?=<h5>)|\Z)'
    mediaTypeSearchString = '.*?([\w]*?)(?:\s|\&nbsp\;)(?=Media Type).*?(?<=application/vnd.abiquo.)(.*?)(?=\+json).*?((?:<td>|<td colspan=\"1\">).*</td>)'    
    mediaTypeBlocks = wikiContent.split("<h5>")
    foundMediaTypes = []
    for mediaTypeBlock in mediaTypeBlocks:
        foundMediaTypes.append(re.findall(mediaTypeSearchString,mediaTypeBlock,re.DOTALL))        
#    foundMediaTypes = re.findall(mediaTypeSearchString,wikiContent,re.DOTALL)
#    if foundMediaTypes:
#        print "Found mediatype: %s" % str(foundMediaTypes)
#       sff = fnm.group(1)    
    return foundMediaTypes

def searchForAttributes(mediaTypeName,mediaTypeContent):
# Search for attributes in the media type
    attributeSearchString = '(?:<td>|<td colspan="1">)(?:<p>)?(.*?)(?:</p>)?</td>.*(?:(?<=<td>)|(?<=<td colspan=\"1\">))(?:<p>)?(.*?)(?:</p>)?</td>'
#    attributeSearchString = '<p>(.*?)</p>.*(?<=<p>)(.*?)</p>'
# If there's more than one table, only use the first one, as the second one has enumerations
# Exclude entities that have sub media types such as pricingtemplate and backuppolicydefinition      
    if (mediaTypeName == 'pricingtemplate' or mediaTypeName == 'backuppolicydefinition' or mediaTypeName == 'limiterror'): 
        mediaTypeOnly = mediaTypeContent[:]    
    else:
        tableBlocks = mediaTypeContent.split("</table>")
        mediaTypeOnly = tableBlocks[0]

    attributeBlocks = mediaTypeOnly.split("</tr>")
    foundAttributes = []
    for attributeBlock in attributeBlocks:
        foundAttributes.append (re.findall(attributeSearchString,attributeBlock,re.DOTALL))
    return foundAttributes


def cleanHTMLfromText(textToClean):
# Get rid of HTML from the data media types
    cleanRegex = re.compile('<.*?>')
    cleanText = re.sub(cleanRegex, '', textToClean)
    return cleanText

def cleanSpansfromText(textToClean):
# Get rid of <span> </span> from the description
    cleanRegex = re.compile('<[///]?span>')
    cleanText = re.sub(cleanRegex, '', textToClean)
    return cleanText    


def main():
#     Open wiki page retrieved with Get Confluence page script based on Sarah's script     
#    dataMediaTypes = openContentFile("/home/mjsmyth/abiquo-wiki-scripts/exportmediatypes/Abiquo_Data_Media_Types-27076188-20180810.txt")
    contentFile = r'/home/mjsmyth/abiquo-wiki-scripts/exportmediatypes/v4234files/Abiquo Data Media Types-27076188'
    dataMediaTypes = openContentFile(contentFile)


    dataMediaTypesList = searchForMediaTypes(dataMediaTypes)

    mediaTypeDict = {}
    for DMT in dataMediaTypesList:
        for (dtoName,rawMediaTypeName,attributeTableText) in DMT:
    #        print "dtoName: %s" % dtoName
    #        print "mediaTypeName: %s" % mediaTypeName
            mediaTypeName = cleanHTMLfromText(rawMediaTypeName)
            mediaTypeDict[dtoName] = {}
            mediaTypeDict[dtoName]['mediaTypeName'] = mediaTypeName
    #        mediaTypeDict[dtoName]['attributes'] = {}
            attributeList = searchForAttributes(mediaTypeName,attributeTableText)
            attributeDict = {}
            for attribute in attributeList:
                for (attributeName,attributeDesc) in attribute:
                    attributeDescWithSpans = attributeDesc
                    attributeDict[attributeName] = cleanSpansfromText(attributeDescWithSpans)
                mediaTypeDict[dtoName]['attributes'] = attributeDict    

    for dtoN,mediaTypeOutputDict in mediaTypeDict.iteritems():
        print "DTO: %s " % dtoN
        print "DMT: %s \n" % mediaTypeOutputDict['mediaTypeName']

        for attributeNameOutput, attributeDescOutput in mediaTypeOutputDict['attributes'].iteritems():
            print "\t%s: " % (attributeNameOutput)
            print "\t* %s \n" % (attributeDescOutput)    
        print "\n"    

# Calls the main() function
if __name__ == '__main__':
    main()