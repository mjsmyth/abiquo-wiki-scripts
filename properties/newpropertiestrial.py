#!/usr/bin/python3 -tt
# New attempt at processing Abiquo properties
#
import codecs
import re
import json
from collections import Counter


def groupLines(line, startComment, lineStore):
    # is it a profile line
    # is it a property description line
    #########
    return "hello"


def main():
    NOTPROFILE = "IN MULTIPLE PROFILES"
    STARTCOMMENT = "# Abiquo Configuration Properties"
    MOUTBOUNDAPI = "M OUTBOUND API"
    propertySearchString = r"#?\s?((([\w,\-]{2,50}?\.){2,10})([\w,\-]{2,50}))(=?(.*?))\n"
    inputDir = '/Users/maryjane/platform/system-properties/src/main/resources/'
    propertyFile = 'abiquo.properties'
    dirPropertyFile = inputDir + propertyFile

    propertiesList = []
    groupStore = []
    propertyDict = {}
    profiles = []
    profilesList = []
    commentStore = []

    with codecs.open(dirPropertyFile, 'r', 'utf-8') as f:
        group = ""
        for line in f:
            if not re.search("^\n", line):
                group += line
            elif (NOTPROFILE in group or STARTCOMMENT in group):
                group = ""
            else:
                groupStore.append(group)
                group = ""

    for group in groupStore:
        if re.search(r"#{10}", group):
            if MOUTBOUNDAPI in group:
                group.replace(MOUTBOUNDAPI, "MOUTBOUNDAPI")
            profiles = re.findall(r"[A-Z,1-9]+", group)
            for profile in profiles:
                if profile not in propertyDict:
                    propertyDict[profile] = []
                if profile not in profilesList:
                    profilesList.append(profile)
        else:
            propertyList = []
            comment = ""
            groupLines = group.split("\n")
            pValue = re.finditer(propertySearchString, group)
            if pValue:
                for pv in pValue:
                    propertyLine = pv.group(0)
                    propertyList.append(propertyLine.strip("\n"))
                    for profile in profiles:
                        propertyDict[profile].append(group)
            for groupLine in groupLines:
                if groupLine[:] not in propertyList:
                    comment += groupLine.strip("#")
                else:
                    # print ("groupLine: ", groupLine, "comment: ", comment)
                    commentStore.append([groupLine, comment])
                    comment = ""
    propDict = {}
    propComment = ""
    propRange = ""
    propNameOccurs = ""
    propNameWithSpaces = ""
    numberOfNameOccurrences = {}

    # commentStore has format property, comment, property, property, property.... 
    for line in commentStore:
        currentProp = line[0]
        if "=" in currentProp:
            splitProp = currentProp.split("=")
            propDefault = splitProp[1]
            propFullName = splitProp[0]
            propName = re.sub(r"^#?\s?", "", propFullName)
        else:
            propName = currentProp
            propDefault = ""
        propDict[propName] = [propName, propDefault]
        propNameWithSpaces = propName.replace(".", " ") + " "
        if line[1]:
            propRange = ""
            propComment = line[1]
            propRangeFound = re.search(
                r"(Range[\s]*?:[\s]*?)(.*)", propComment)
            if propRangeFound:
                propRangeString = propRangeFound.group(0)
                propRange = propRangeFound.group(2)
                propComment = re.sub(propRangeString, "", propComment)
            # if there's a comment it may be a new property
            if len(propNameOccurs) > len(propNameWithSpaces):
                numberOfNameOccurrences = Counter(
                    propNameOccurs.split(" "))
                print ("num of name occ: ",
                       json.dumps(numberOfNameOccurrences, indent=2))

            numberOfNameOccurrences = {}
            propNameOccurs = propNameWithSpaces[:]
        else:
            propComment = ""
            propNameOccurs += propNameWithSpaces[:]

        propDict[propName].append(propComment)
        propDict[propName].append(propRange)
        propDict[propName].append(numberOfNameOccurrences)

    propertiesList.append(propDict)
#    for props in propertiesList:
#        print(json.dumps(props, indent=2))




                    # propertyAndDefault = pv[0]
                    # print("propertyAndDefault: ", propertyAndDefault)
                    # propertyName = pv[1]
                    # print("name: ", propertyName)
                    # propertyDefault = pv[-1]
                    # print("default: ", propertyDefault)


            #     propertyGroup.append(comment)
            #     propertiesWithComments.append(propertyGroup)
            # for propertyGroup in propertiesWithComments:
            #     if len(propertyGroup) > 2:
            #         numberOfNameOccurrences = Counter(
            #             nameElementsString.split(" "))
            #         print ("num of name occ: ",
            #                json.dumps(numberOfNameOccurrences, indent=2))
#                for name, num in numberOfNameOccurrences.items():
#                    if num > 1:
#                        baseName.append(name)
#                    else:
#                        variables.append(name)
                # print("baseName: ", baseName)
                # print("variables: ", variables)

            
            # print (propertyValues)
            # print (otherPropertyText)
            # for pv in propertyValues:
            #     print (pv)
            #     if pv[0]:
            #         propertySection = pv[0]
            #         print("section: ", propertySection)
            #         propertyName = pv[1]
            #         print("name: ", propertyName)
            #         defaultValue = pv[-1]
            #         print("default: ", defaultValue)
            # print("group: ", group)


    # print(json.dumps(propertyDict, indent=2))
    # Discard the comments at start of file
    # for group in groupStore:
    #    print (group)
    #    print ("---")


# Calls the main() function
if __name__ == '__main__':
    main()
