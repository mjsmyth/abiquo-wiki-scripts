#!/usr/bin/python3 -tt
# New attempt at processing Abiquo properties
# Hopefully this time it is developer proof
#
# import codecs
import re
import json
# from collections import Counter
import copy
from datetime import datetime
import os


def getDefault(pName, default):
    # some defaults are replaced on filesystem during install
    if pName == "abiquo.datacenter.id":
        newDefault = re.sub("default", "Abiquo", default)
    if "repositoryLocation" in pName:
        newDefault = re.sub("127.0.0.1", r"<IP-repoLoc>", default)
    newDefault = re.sub("localhost", r"127.0.0.1", default)
    newDefault = re.sub("10.60.1.4", r"127.0.0.1", default)
    return newDefault


def getCategory(pName, CATEGORYDICT):
    # categories are used for anchors
    prop_cat = pName.split(".")
    property_cat = prop_cat[1]
    if property_cat[0] == "workflow":
        property_cat = "workflow"
    if property_cat[0] == "com":
        property_cat = "virtualfactory"

    if property_cat in CATEGORYDICT:
        return CATEGORYDICT[property_cat]
    else:
        return property_cat


def writePropsToFormattedFile(propertiesDict, PRINTORDER,
                              outputSubdir, wikiPropertiesFile):
    with open(os.path.join(outputSubdir, wikiPropertiesFile), 'w') as f:
        count = 0
        previousCategory = ""

        # sort by name
        sortedProperties = sorted(propertiesDict,
                                  key=lambda x: x.lower())
        for pNa in sortedProperties:
            # print ("pName: ", pNa)
            propOutDict = propertiesDict[pNa]
            # replace name with real name
            if propOutDict["realName"]:
                propOutDict["Property"] = \
                    copy.deepcopy(propOutDict["realName"])
                # print (propOutDict["Property"])
            # add anchor for category
            if propOutDict["Category"] != previousCategory:
                anchor = " {anchor: " + propOutDict["Category"] + "}"
                propOutDict["Property"] = propOutDict["Property"] \
                    + anchor
                previousCategory = copy.deepcopy(propOutDict["Category"])
            # Add Default and Range in the description
            if propOutDict["Default"]:
                if ("http") not in propOutDict["Default"]:
                    propOutDict["Description"] += " \\\\ _Default: " + \
                                                  propOutDict["Default"] + \
                                                  "_ "
                else:
                    propOutDict["Description"] += " \\\\ Default: " + \
                                                  propOutDict["Default"] + \
                                                  " "
            if propOutDict["Range"]:
                propOutDict["Description"] += " \\\\ _Range: " + \
                                              propOutDict["Range"] + \
                                              "_ "

            # sort the dictionary for print
            index_map = {v: i for i, v in enumerate(PRINTORDER)}
            propOutDictSorted = sorted(propOutDict.items(),
                                       key=lambda pair: index_map[pair[0]])
            # print(json.dumps(propOutDict, indent=2))
            if count == 0:
                headLineText = " || ".join(str(x) for x in PRINTORDER)
                headLine = "|| " + headLineText + " ||\n"
                f.write(headLine)
                count += 1
            # Later remove realname and category from sorted output properties

            propLineText = " | ".join(str(x[1]) for
                                      x in propOutDictSorted)
            propLine = "| " + propLineText + " |\n"
            f.write(propLine)
    return True


def writePropsToFile(propertiesDict, PRINTORDER,
                     outputSubdir, wikiPropertiesFile):
    # Basic markup file with all properties
    with open(os.path.join(outputSubdir, wikiPropertiesFile), 'w') as f:
        count = 0
        sortedProperties = sorted(propertiesDict, key=lambda s: s.lower())
        for pNa in sortedProperties:
            # print ("pName: ", pNa)
            propOutDictToSort = propertiesDict[pNa]
            index_map = {v: i for i, v in enumerate(PRINTORDER)}
            propOutDictValues = sorted(propOutDictToSort.items(),
                                       key=lambda pair: index_map[pair[0]])
            # print(json.dumps(propOutDict, indent=2))
            if count == 0:
                headLineText = " || ".join(str(x) for x in PRINTORDER)
                headLine = "|| " + headLineText + " ||\n"
                f.write(headLine)
                count += 1

            propLineText = " | ".join(str(x[1]) for
                                      x in propOutDictValues)
            propLine = "| " + propLineText + " |\n"
            f.write(propLine)
    return True


def getPropNameDefault(currentProp):
    if "=" in currentProp:
        splitProp = currentProp.split("=")
        propDefault = splitProp[1].strip()
        propName = splitProp[0].strip()
        propName = re.sub(r"^#?\s?", "", propName)
    else:
        propName = currentProp.strip()
        propDefault = ""
        propName = re.sub(r"^#?\s?", "", propName)

    propRealName = ""
    # deal with properties with com. prefix to name
    if re.match(r"^com.", propName):
        propRealName = copy.deepcopy(propName)
        propName = re.sub(r"^com.", "", propName)
    return (propName, propRealName, propDefault)


def processFile(inputDir, propertyFile, NOTPROFILE, STARTCOMMENT,
                MOUTBOUNDAPI, propertySearchString,
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
            elif (NOTPROFILE in group or STARTCOMMENT in group):
                group = ""
            else:
                groupStore.append(group)
                group = ""

    # separate by the profile section markers
    for group in groupStore:
        if re.search(r"#{10}", group):
            if MOUTBOUNDAPI in group:
                changedGroup = group.replace(MOUTBOUNDAPI, "MOUTBOUNDAPI")
            else:
                changedGroup = copy.deepcopy(group)
            profiles = re.findall(r"[A-Z,1-9]+", changedGroup)
            for profile in profiles:
                # if profile not in propertyDict:
                #     propertyDict[profile] = []
                if profile not in profilesList:
                    profilesList.append(profile)
        # separate groups into further groups of properties plus their comments
        else:
            propertyList = []
            comment = ""
            groupLines = group.split("\n")
            # find all the properties in a group that may include comments
            pValue = re.finditer(propertySearchString, group)
            if pValue:
                for pv in pValue:
                    propertyLine = pv.group(0)
                    propertyLine = propertyLine.strip("\n")
                    # print("propertyLine: ", propertyLine)
                    propertyList.append(propertyLine)

                    propertyName, blah, blah = getPropNameDefault(propertyLine)
                    # add each property to the corresponding profiles
                    for profile in profiles:
                        if propertyName not in profileDict:
                            profileDict[propertyName] = []
                        profileDict[propertyName].append(profile)
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


def processGroups(propName):
    # METRICS = ["cpu", "cpu-mz", "cpu-time", "memory",
    #            "memory-swap", "memory-swap2", "memory-vmmemctl",
    #            "memory-physical", "memory-host", "disk-latency",
    #            "uptime"]
    PLUGINS = ["veeam95u4", "veeam10", "networker", "veeam",
               "cloudsigma2-hnl", "cloudsigma2-zrh",
               "cloudsigma2-sjc", "cloudsigma2-wdc",
               "cloudsigma2-lvs", "digitalocean2",
               "elastichosts-ams-e", "elastichosts-hkg-e",
               "elastichosts-lax-p", "elastichosts-lon-b",
               "elastichosts-lon-p", "elastichosts-sat-p",
               "elastichosts-sjc-c", "cloudsigma2-lvs",
               "google-compute-engine", "openstack-nova",
               "packet", "amazon", "kvm", "vmx_04",
               "rackspace-cloudservers-uk",
               "softlayer", "esx", "vcenter_cluster",
               "packet", "e1c",
               "hyperv_301", "oracle-ase-emea",
               "azurecompute-arm", "oracle-ase-us",
               "oracle-ase-emea", "oraclevm",
               "vcd", "xenserver", "oracle_vm",
               "digitalocean2", "google-compute-engine",
               "rackspace-cloudservers-us", "cloudoorsphere",
               "openstack-neutron", "dnsmasq", "omapi",
               "nsx-ecmp", "logical",
               "nsx-nat", "nsx-gateway"]
    groupTypes = {"{plugin}": PLUGINS}

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
    NOTPROFILE = "IN MULTIPLE PROFILES"
    STARTCOMMENT = "# Abiquo Configuration Properties"
    MOUTBOUNDAPI = "M OUTBOUND API"
    propertySearchString = r"#?\s?((([\w,\-]{2,50}?\.){2,10})([\w,\-]{2,50}))(=?(.*?))\n"
    # rangeSearchString = r"(Range[\s]*?:?[\s]*?)(.*?)"
    inputDir = '/Users/maryjane/platform/system-properties/src/main/resources/'
    propertyFile = 'abiquo.properties'
    outputSubdir = '/Users/maryjane/abiquo-wiki-scripts/properties/'
    outputPropertyFile = 'wiki_properties_'
    #    inputDirPropertyFile = inputDir + propertyFile
    todaysDate = datetime.today().strftime('%Y-%m-%d')
    wikiPropertiesFile = outputPropertyFile + todaysDate + ".txt"
    # inputDirPropertyFile = inputDir + propertyFile
    # outputDirPropertyFile = outputSubdir + wikiPropertiesFile

    # NARSPROPERTY = r"#abiquo\.nars\.async\.pool"
    NARSCOMMENT = ("Maximum number of simultaneous operations on a single "
                   "hypervisor or region connection, by type. "
                   "Default abiquo.nars.async.pool.max")

    NARSLIST = ["device plugins", "backup plugins"]
    CATEGORYDICT = {"stale": "stale sessions", "dvs": "dvs and vcenter",
                    "vi": "virtual infrastructure",
                    "USE_SECURE_CHANNEL_LOGIN": "client",
                    "m": "m outbound api"}
    PRINTORDER = ["Property", "Category", "Description", "Default", "Range",
                  "profiles", "groupName", "groupTag", "realName"]
    groupDict = {}
    propertiesDict = {}
    groupStore = []
    profileDict = {}
    profilesList = []
    commentStore = []

    profilesList, commentStore, profileDict = \
        processFile(inputDir, propertyFile, NOTPROFILE,
                    STARTCOMMENT, MOUTBOUNDAPI,
                    propertySearchString,
                    groupStore, profileDict,
                    profilesList, commentStore)

    propDict = {}
    propComment = ""
    propRange = ""

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
            propDict["realName"] = copy.deepcopy(propRealName)
        else:
            propDict["realName"] = ""

        # check for property names that are groups
        groupTag, groupPattern, groupName = processGroups(propName)

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
            # deal with specific interleaving comments in nars list
            if propComment in NARSLIST:
                propComment = NARSCOMMENT
            propRangeList = []
            if "Range" in propComment:
                print("propComment: ", propComment)
                # propRangeFound = re.search(rangeSearchString, propComment)
                propRangeList = propComment.split("Range")
                propRangeFound = propRangeList[-1]
                print("propRangeFound: ", propRangeFound)
                propRange = copy.deepcopy(propRangeFound)
                propRange = re.sub(r"^[\s]*?[:]*?[\s]*?", "", propRange)
                propRange = propRange.strip()
                print("propRangeSubbed: ", propRange)
                if propRange:
                    propComment = propComment.replace(propRangeFound, "")
                    propComment = propComment.replace("Range", "")
                # Escape special character for links in the wiki
                if "[" in propRange:
                    propRange = propRange.replace("[", "")
                    propRange = propRange.replace("]", "")
                print("propRange:", propRange)
            # Escape special character for macros in the wiki
            if "{" in propComment:
                propComment = re.sub(r"{", r"\{", propComment)
            propComment = re.sub(r"\n\s*?\n", r"\n", propComment)
            propComment = re.sub(r"-(.*?)-", r"\\-\1-", propComment)
            print("newComment: ", propComment)
        propDict["Category"] = getCategory(propName, CATEGORYDICT)
        propDict["Description"] = copy.deepcopy(propComment)
        propDict["Range"] = copy.deepcopy(propRange)
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
        for groupName, propertyNamesTags in groupNameDict.items():
            realName = re.sub("{", r"\{", groupName)
            groupNameWithTags = copy.deepcopy(realName)
            newProperty = True
            for prName, groupTag in propertyNamesTags.items():
                groupNameWithTags += "\n * " + groupTag
                if newProperty is True:
                    groupPropertyDict = copy.deepcopy(propertiesDict[prName])
                    newProperty = False
                propertiesDict.pop(prName)
            groupPropertyDict["Property"] = copy.deepcopy(groupName)
            groupPropertyDict["realName"] = copy.deepcopy(groupNameWithTags)
            # Write the new group property
            propertiesDict[groupName] = copy.deepcopy(groupPropertyDict)
            #    propertiesDict[prName]["groupName"] = copy.deepcopy(group)
            #    propertiesDict[prName]["groupTag"] = copy.deepcopy(groupTag)

    for pNae, profList in profileDict.items():
        if pNae in propertiesDict:
            propertiesDict[pNae]["profiles"] = copy.deepcopy(profList)

    # write a plain wiki markup file from the file
    # check = writePropsToFile(propertiesDict, PRINTORDER,
    #                         outputSubdir, wikiPropertiesFile)
    check = writePropsToFormattedFile(propertiesDict, PRINTORDER,
                                      outputSubdir, wikiPropertiesFile)
    if check is True:
        print("Wrote to file")

# TO DO
# - Resolve real name when printing
# - Sort by category and then by property name?
# - Add profiles as images
# - Check against wiki version
# - Add metrics to file (?)
# - Revise English of file
# - Sort weird profile names - add correspondence to RS or API or ?
# - Put properties into categories - and add anchors


# Calls the main() function
if __name__ == '__main__':
    main()
