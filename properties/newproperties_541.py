#!/usr/bin/python3 -tt
# New attempt at processing Abiquo properties
# Hopefully this time it is developer proof
#
# import codecs
# import json
import re
import copy
from datetime import datetime
import os
from abiquo.client import Abiquo
from abiquo.auth import TokenAuth
# from abiquo.client import check_response

# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def getPlugins(api):
    # Get plugins: hypervisor types, network devices,
    #              backup devices, draas devices
    code, hypervisorTypesList = api.config.hypervisortypes.get(
        headers={'Accept': 'application/vnd.abiquo.hypervisortypes+json'})
    print("Get hypervisor types. Response code is: ", code)
    hypervisorTypes = [ht["name"].lower()
                       for ht in hypervisorTypesList.json["collection"]]

    code, deviceTypesList = api.config.devicetypes.get(
        headers={'Accept': 'application/vnd.abiquo.devicetypes+json'})
    print("Get device types. Response code is: ", code)
    deviceTypes = [dt["name"].lower()
                   for dt in deviceTypesList.json["collection"]]

    code, backupPluginTypesList = api.config.backupplugintypes.get(
        headers={'Accept': 'application/vnd.abiquo.backupplugintypes+json'})
    print("Get backup plugin types. Response code is: ", code)
    backupPluginTypes = [bpt["type"].lower()
                         for bpt in backupPluginTypesList.json["collection"]]

    code, draasPluginTypesList = api.config.draasplugintypes.get(
        headers={'Accept': 'application/vnd.abiquo.draasplugintypes+json'})
    print("Get DRaaS device types. Response code is: ", code)
    draasPluginTypes = [drpt["type"].lower()
                        for drpt in draasPluginTypesList.json["collection"]]
    return (hypervisorTypes, deviceTypes, backupPluginTypes, draasPluginTypes)


def getDefault(pName, default):
    # some defaults are replaced on filesystem during install
    newDefault = default[:]
    if pName == "abiquo.datacenter.id":
        newDefault = re.sub("default", "Abiquo", default)
    if "repositoryLocation" in pName:
        newDefault = re.sub("127.0.0.1", r"<IP-repoLoc>", default)
    if "localhost" in default:
        newDefault = re.sub("localhost", r"127.0.0.1", default)
    if "10.60.1.4" in default:
        newDefault = re.sub("10.60.1.4", r"127.0.0.1", default)
    # if default == "/":
    #    print("This is the default: ", pName, " - ", default)
    #    newDefault = "SLASH"
    return newDefault


def getCategory(pName, CATEGORYDICT):
    # categories are used for anchors
    prop_cat = pName.split(".")
    if prop_cat[0] == "abiquo":
        property_cat = prop_cat[1][:]
    else:
        if prop_cat[0] == "com":
            if prop_cat[1] == "abiquo":
                property_cat = prop_cat[3][:]
            else:
                property_cat = prop_cat[2][:]
        else:
            property_cat = prop_cat[0][:]

    if property_cat in CATEGORYDICT:
        # print("Adjust prop cat: ", property_cat)
        return copy.deepcopy(CATEGORYDICT[property_cat])
    else:
        return property_cat


def writePropsToFile(propertiesDict, outputSubdir, wikiPropertiesFile,
                     PLGDEPRC, profileImages, profileColumns,
                     FMTPRINTORDER):
    # Basic markup file with all properties
    with open(os.path.join(outputSubdir, wikiPropertiesFile), 'w') as f:
        previousCategory = ""
        headLineText = " || ".join(str(x) for x in FMTPRINTORDER)
        headLine = "|| " + headLineText + " ||\n"
        f.write(headLine)

        sortedProperties = sorted(propertiesDict, key=lambda s: s.lower())
        # remove from list properties containing
        # deprecated plugin names e.g. e1c :-p
        sortedPropsNotDep = [b for b in sortedProperties if
                             all(a not in b for a in PLGDEPRC)]

        for pNa in sortedPropsNotDep:
            fullDesc = " "
            addDefault = " "
            addRange = " "
            groupDefault = " "
            # add an anchor for the category
            if propertiesDict[pNa]["Category"] != previousCategory:
                anchor = " {anchor: " + \
                    copy.deepcopy(propertiesDict[pNa]["Category"]) + "}"
            else:
                anchor = " "
            previousCategory = copy.deepcopy(propertiesDict[pNa]["Category"])

            # add profiles
            if propertiesDict[pNa]["profiles"]:
                for profileName, profileImage in profileImages.items():
                    if profileName in propertiesDict[pNa]["profiles"]:
                        if profileName in profileColumns:
                            column = profileColumns[profileName]
                            propertiesDict[pNa][column] = copy.deepcopy(
                                profileImages[profileName])
                    else:
                        propertiesDict[pNa][profileName] = "  "
            # use real name
            if propertiesDict[pNa]["realName"]:
                printName = anchor + " " + \
                    copy.deepcopy(propertiesDict[pNa]["realName"])
                if "defaults" in propertiesDict[pNa]:
                    print("found Group with defaults: ", pNa)
                    if len(set(propertiesDict[pNa]["defaults"].values())) - \
                            len(propertiesDict[pNa]["defaults"]) >= -1:
                        if len(set(propertiesDict[pNa]["defaults"].values())) > 1:
                            for tag, df in propertiesDict[pNa]["defaults"].items():
                                groupDefault += "\\\\" + " - " + tag + " = " + df + " "
                            propertiesDict[pNa]["Default"] = "Default: "
                    else:                 
                        for tag, df in propertiesDict[pNa]["defaults"].items():
                            if df != propertiesDict[pNa]["Default"]:
                                groupDefault += "\\\\" + " - " + tag + " = " + df + " "
            else:
                printName = anchor + " #*#" + \
                    copy.deepcopy(propertiesDict[pNa]["Property"]) + "#*# "

            # add the default and range to the description
            if "Default" in propertiesDict[pNa]:
                if re.search(r'[\w,/]', propertiesDict[pNa]["Default"]):
                    if "http" not in propertiesDict[pNa]["Default"]:
                        addDefault = " \\\\ _Default: " + \
                            copy.deepcopy(propertiesDict[pNa]["Default"]) + "_"
                    else:
                        linkFormat = re.sub(r"((http:|https:)(\S*)?)", r'[\1]',
                                            copy.deepcopy(propertiesDict[pNa]["Default"]))
                        addDefault = " \\\\ Default: " + linkFormat + " "
                    # this is probably a regex, give it the big escape    
                    if "[" in addDefault and "{" in addDefault:
                        addDefault = re.sub(r'_Default: (.*)?_',
                                            r'_Default:_ {newcode}\1{newcode}',
                                            addDefault)
                if re.search(r'[\w,/]', groupDefault):
                    addDefault += groupDefault
            if "Valid values" in propertiesDict[pNa]:
                if re.search(r'\w', propertiesDict[pNa]["Valid values"]):
                    addRange = " \\\\ _Valid values: " + copy.deepcopy(propertiesDict[pNa]["Valid values"]) + "_ "
            descWithHttp = copy.deepcopy(propertiesDict[pNa]["Description"])
            if "http" in descWithHttp:
                if "<" not in descWithHttp:
                    descWithHttp = re.sub(r"((http:|https:)(\S*)?)", r'[\1]', descWithHttp)
                else:
                    descWithHttp = re.sub(r"((http:|https:)//<(.*?)>(\S*)?)", r'{newcode}\1{newcode}', descWithHttp)
            fullDesc =  descWithHttp + addDefault + addRange
            propOutDictValues = []
            propOutDictValues.append(copy.deepcopy(printName))
            propOutDictValues.append(copy.deepcopy(fullDesc))
            propOutDictValues.append(copy.deepcopy(propertiesDict[pNa]["SERVER"]))
            propOutDictValues.append(copy.deepcopy(propertiesDict[pNa]["REMOTESERVICES"]))
            propOutDictValues.append(copy.deepcopy(propertiesDict[pNa]["V2VSERVICES"]))
            propOutDictValues.append(copy.deepcopy(propertiesDict[pNa]["MOUTBOUNDAPI"]))

            propLineText = " | ".join(propOutDictValues)
            propLine = "| " + propLineText + " |\n"
            if "{" in propLine:
                # if a bracket is not already escaped, escape it
                propLine = re.sub(r'(?<!\\){', r'\\{', propLine)
                # if we want to create a macro, unescape the escape we just did
                propLine = re.sub(r'\\{(?=anchor)|\\{(?=status)|\\{(?=newcode)', r'{', propLine)
                # also if the escape is in a bracket
                # TODO we need to do something here or sort out all the escapes :-p
                # note that it thinks square brackets are links, and you can't escape it!
                propLine = re.sub(r'\[javax mail property]', r'\{javaxMailProperty}', propLine)
                # Create unescaped stars for bold text by replacing escaped stars
                propLine = re.sub(r'\*', r'\\*', propLine)
                propLine = re.sub(r'\#\\\*\#', r'*', propLine)
                # propLine = re.sub(r'SLASH', r'/', propLine)
                # print("Proppline: ", propLine)
            f.write(propLine)
    return True


def getPropNameDefault(currentProp):
    if "=" in currentProp:
        splitProp = currentProp.split("=")
        defaultJoined = "=".join(splitProp[1:])
        propDefault = defaultJoined.strip()
        propName = splitProp[0].strip()
        propName = re.sub(r"^#?\s?", "", propName)
    else:
        propName = currentProp.strip()
        propDefault = ""
        propName = re.sub(r"^#?\s?", "", propName)
    pDefault = getDefault(propName, propDefault)
    propRealName = ""
    # deal with properties with com. prefix to name
    if re.match(r"^com.", propName):
        propRealName = copy.deepcopy(propName)
        propName = re.sub(r"^com.", "", propName)
    return (propName, propRealName, pDefault)


def processFile(inputDir, propertyFile, STARTCOMMENT,
                PROFILE_SPACES, propertySearchString,
                groupStore, profileDict,
                profilesList, commentStore):
    # groups in the file are separated by spaces
    profiles = []

    with open(os.path.join(inputDir, propertyFile), 'r') as f:
        # with codecs.open(dirPropertyFile, 'r', 'utf-8') as f:
        group = ""
        for line in f:
            if not re.search("^\n", line):
                group += line
            elif (STARTCOMMENT in group):
                # eliminate the comment at start of file
                group = ""
            else:
                groupStore.append(group)
                group = ""

    # separate by the profile section markers
    for group in groupStore:
        if re.search(r"#{10}", group):
            changedGroup = copy.deepcopy(group)
            for profileNoSpaces, profileSpaces in PROFILE_SPACES.items():
                if profileSpaces in group:
                    changedGroup = group.replace(profileSpaces,
                                                 profileNoSpaces)
            profiles = re.findall(r"[A-Z,1-9]+", changedGroup)
            for profile in profiles:
                # print("profile: ", profile)
                # if profile not in propertyDict:
                #     propertyDict[profile] = []
                if profile not in profilesList:
                    profilesList.append(profile)
        # separate groups into further groups of properties plus their comments
        else:
            propertyList = []
            comment = ""
            # remove readability comments in format "#-- xxx"
            group = group.replace(r'^#--.*?\n', "")
            groupLines = group.split("\n")
            # find all the properties in a group that may include comments
            pValue = re.finditer(propertySearchString, group)
            if pValue:
                for pv in pValue:
                    propertyLine = pv.group(0)
                    propertyLine = propertyLine.strip("\n")
                    # print("propertyLine: ", propertyLine)
                    propertyList.append(propertyLine)

                    propertyName, propRealName, propDefault = \
                        getPropNameDefault(propertyLine)
                    # add each property to the corresponding profiles
                    for profile in profiles:
                        if propertyName not in profileDict:
                            profileDict[propertyName] = {}
                        profileDict[propertyName][profile] = profile
            # get comments without whitespace between them and their properties
            for groupLine in groupLines:
                if groupLine[:] not in propertyList:
                    comment += groupLine.strip("#")
                else:
                    commentStore.append([groupLine, comment])
                    comment = ""
    return(profilesList, commentStore, profileDict)


def processExplicitGroups(propName):
    # Process property names that have one or more texts in {}
    # This is an explicit group but it doesn't have any list members
    # So just escape the { characters in the name and
    # and store it as realName
    rName = re.sub(r"{", r"\{", propName)
    return rName


def processGroups(propName, PLUGINS):

    METRICS = ["cpu",
               "cpu-mz",
               "cpu-time",
               "memory",
               "memory-swap",
               "memory-swap2",
               "memory-vmmemctl",
               "memory-physical",
               "memory-host",
               "disk-latency",
               "uptime"]
    groupTypes = {"{plugin}": PLUGINS, "{metric}": METRICS}

    propName.strip()
    propNameList = propName.split(".")
    # plugins etc are not in first two parts of name
    # filter list of plugins in each list
    lastPropNameList = propNameList[2:]

    for group, groupList in groupTypes.items():
        groupTagList = [x for x in lastPropNameList if x in groupList]
        if groupTagList:
            # print("propName devices: ", propName, devicesGroup)
            groupTag = groupTagList[0]
            groupPattern = propName.replace(groupTag, "XXX")
            groupName = propName.replace(groupTag, group)
            return (groupTag, groupPattern, groupName)
    return("", "", "")


def main():
    token = input("Enter token: ")
    apiUrl = input("Enter API URL: ")
    api = Abiquo(apiUrl, auth=TokenAuth(token), verify=False)
    hypervisorTypes, deviceTypes, \
        backupPluginTypes, draasPluginTypes = getPlugins(api)
    for ht in hypervisorTypes:
        print("ht: ", ht)
    for dt in deviceTypes:
        print("dt: ", dt)
    for bpt in backupPluginTypes:
        print("bpt: ", bpt)
    for dpt in draasPluginTypes:
        print("dpt: ", dpt)
    PLUGINS = hypervisorTypes + deviceTypes + \
        backupPluginTypes + draasPluginTypes
    STARTCOMMENT = "# Abiquo Configuration Properties"
    PROFILE_SPACES = {"MOUTBOUNDAPI": "M OUTBOUND API",
                      "COSTUSAGE": "COST USAGE"}
    # propertySearchString = r"#?\s?((([\w,\-]{1,60}?\.){2,10})([\w,\-]{2,50}))(=?(.*?))\n"
    # Note that a single property only has two parts :-p abiquo.capturedhcp :-(
    propertySearchString = r"#?\s?((([\w,\-,{,}]{1,60}?\.){1,10})([\w,\-,{,}]{1,50}))(=?(.*?))\n"
    # rangeSearchString = r"(Range[\s]*?:?[\s]*?)(.*?)"
    inputDir = '/Users/maryjane/platform/system-properties/src/main/resources/'
    propertyFile = 'abiquo.properties'
    outputSubdir = '/Users/maryjane/abiquo-wiki-scripts/properties/'
    outputPropertyFile = 'wiki_properties_'
    #    inputDirPropertyFile = inputDir + propertyFile
    todaysDate = datetime.today().strftime('%Y-%m-%d')
    wikiPropertiesFile = outputPropertyFile + "_format_" + todaysDate + ".txt"
    # inputDirPropertyFile = inputDir + propertyFile
    # outputDirPropertyFile = outputSubdir + wikiPropertiesFile

    CATEGORYDICT = {"stale": "stale sessions",
                    "dvs": "dvs and vcenter",
                    "vi": "virtual infrastructure",
                    "m": "m outbound api"}
    # FMTPRINTORDER = ["Property", "Description", "API",
    #                 "RS", "OA", "DNSMASQ", "COSTUSAGE", "BILLING"]
    FMTPRINTORDER = ["Property", "Description", "API", "RS", "V2V", "OA"]

    # Deprecated plugins
    PLGDEPRC = ["google-compute-engine"]
    # ESXi metrics list
    METRICS = ["cpu",
               "cpu-mz",
               "cpu-time",
               "memory",
               "memory-swap",
               "memory-swap2",
               "memory-vmmemctl",
               "memory-physical",
               "memory-host",
               "disk-latency",
               "uptime"]
    # Display these lozenges
    profileImages = {"SERVER":
                     " {status:colour=green|title=API|subtle=false}",
                     "REMOTESERVICES":
                     " {status:colour=blue|title=RS|subtle=false}",
                     "V2VSERVICES":
                     " {status:colour=grey|title=V2V|subtle=false}",
                     "MOUTBOUNDAPI":
                     " {status:colour=yellow|title=OA|subtle=false}",
                     "DNSMASQ":
                     " {status:colour=yellow|title=DNSMASQ|subtle=false}",
                     "COSTUSAGE":
                     " {status:colour=yellow|title=COSTUSAGE|subtle=false}",
                     "BILLING":
                     " {status:colour=yellow|title=BILLING|subtle=false}"
                     }
    # Piggyback the profiles into the main columns
    profileColumns = {"SERVER": "SERVER",
                      "REMOTESERVICES": "REMOTESERVICES",
                      "V2VSERVICES": "V2VSERVICES",
                      "MOUTBOUNDAPI": "MOUTBOUNDAPI",
                      "DNSMASQ": "REMOTESERVICES",
                      "COSTUSAGE": "SERVER",
                      "BILLING": "SERVER"
                      }

    groupDict = {}
    propertiesDict = {}
    groupStore = []
    profileDict = {}
    profilesList = []
    commentStore = []

    profilesList, commentStore, profileDict = \
        processFile(inputDir, propertyFile,
                    STARTCOMMENT, PROFILE_SPACES,
                    propertySearchString,
                    groupStore, profileDict,
                    profilesList, commentStore)

    propDict = {}
    propComment = ""
    propRange = ""
    groupPropDefaults = {}

    # list of all properties with comments
    for line in commentStore:

        currentProp = line[0]
        propName, propRealName, propDefault = getPropNameDefault(currentProp)
        if "{" in propName:
            propRealName = processExplicitGroups(propName)
        propDict = {}
        propDict["Property"] = copy.deepcopy(propName)
        propDict["Default"] = copy.deepcopy(propDefault)
        if propRealName:
            propDict["realName"] = "#*#" + copy.deepcopy(propRealName) + "#*#"
        else:
            propDict["realName"] = ""

        # check for property names that are groups
        groupTag, groupPattern, groupName = processGroups(propName, PLUGINS)

        if groupPattern:
            if groupPattern not in groupDict:
                groupDict[groupPattern] = {}
            if groupName not in groupDict[groupPattern]:
                groupDict[groupPattern][groupName] = {}
            groupDict[groupPattern][groupName][propName] = \
                copy.deepcopy(groupTag)

        if line[1]:
            # process a property comment
            propRange = ""
            propComment = line[1]
            propComment = re.sub(r"^\s?", "", propComment)
            propRangeList = []
            if "Valid values" in propComment:
                # print("propComment: ", propComment)
                # propRangeFound = re.search(rangeSearchString, propComment)
                propRangeList = propComment.split("Valid values")
                propRangeFound = propRangeList[-1]
                # print("propRangeFound: ", propRangeFound)
                propRange = copy.deepcopy(propRangeFound)
                propRange = re.sub(r"^[\s]*?[:]*?[\s]*?", "", propRange)
                propRange = propRange.strip()
                # print("propRangeSubbed: ", propRange)
                if propRange:
                    propComment = propComment.replace(propRangeFound, "")
                    propComment = propComment.replace("Valid values", "")
                # Escape special character for links in the wiki
                if "[" in propRange:
                    propRange = propRange.replace("[", "")
                    propRange = propRange.replace("]", "")
                # print("propRange:", propRange)
            # Escape special character for macros in the wiki
            if "{" in propComment:
                propComment = re.sub(r"{", r"\{", propComment)
            propComment = re.sub(r"\n\s*?\n", r"\n", propComment)
            if "http" not in propComment:
                propComment = re.sub(r"-(.*?)-", r"\\-\1-", propComment)
            # print("newComment: ", propComment)
        # print("propName: ", propName)
        categ = getCategory(propName, CATEGORYDICT)
        # print ("Category: ", categ)
        propDict["Category"] = copy.deepcopy(categ)
        propDict["Description"] = copy.deepcopy(propComment)
        propDict["Valid values"] = copy.deepcopy(propRange)
        propDict["groupName"] = ""
        propDict["groupTag"] = ""
        propDict["profiles"] = []
        propertiesDict[propName] = copy.deepcopy(propDict)
    # A property group has two or more items
    count = 0
    groupToRemove = []
    for groupPattern, groupNameDict in groupDict.items():
        for group, names in groupNameDict.items():
            for name, tag in names.items():
                count += 1
        if count < 2:
            groupToRemove.append(groupPattern)
        count = 0
    # Don't process groups with only one item
    for groupToRemoveName in groupToRemove:
        groupDict.pop(groupToRemoveName)

    # print(json.dumps(groupDict, indent=2))

    for groupPattern, groupNameDict in groupDict.items():
        groupPropertyDict = {}
        groupPropDefaults = {}
        for groupName, propertyNamesTags in groupNameDict.items():
            realName = re.sub("{", r"\{", groupName)
            groupNameWithTags = "#*#" + copy.deepcopy(realName) + "#*#"
            newProperty = True
            for prName, groupTag in propertyNamesTags.items():
                # groups are repeated text sections
                # but they must also be plugins
                if groupTag in PLUGINS or groupTag in METRICS:
                    # add an escaped star to later unescape after
                    # escaping stars in text
                    groupNameWithTags += " \\\\ - " + groupTag
                    groupPropDefaults[groupTag] = copy.deepcopy(propertiesDict[prName]["Default"])
                    if newProperty is True:
                        groupPropertyDict = copy.deepcopy(propertiesDict[prName])
                        newProperty = False
                        if prName in profileDict:
                            groupPropertyDict["profiles"] = \
                                copy.deepcopy(profileDict[prName])
                    propertiesDict.pop(prName)
            groupPropertyDict["realName"] = copy.deepcopy(groupNameWithTags)
            groupPropertyDict["Property"] = copy.deepcopy(groupName)
            groupPropertyDict["defaults"] = copy.deepcopy(groupPropDefaults)
            # Write the new group property
            propertiesDict[groupName] = copy.deepcopy(groupPropertyDict)
            #    propertiesDict[prName]["groupName"] = copy.deepcopy(group)
            #    propertiesDict[prName]["groupTag"] = copy.deepcopy(groupTag)

    for pNae, profList in profileDict.items():
        # if "instance" in pNae:
        #   print("property: ", pNae)
        if pNae in propertiesDict:
            propertiesDict[pNae]["profiles"] = copy.deepcopy(profList)

    # write a plain wiki markup file from the file
    check = writePropsToFile(propertiesDict, outputSubdir, wikiPropertiesFile,
                             PLGDEPRC, profileImages, profileColumns,
                             FMTPRINTORDER)

    if check is True:
        print("Wrote to file")

# TO DO
# - Check quitwait
# - Add status lozenges to header


# Calls the main() function
if __name__ == '__main__':
    main()
