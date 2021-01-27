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


def getPropNameDefault(currentProp):
    if "=" in currentProp:
        splitProp = currentProp.split("=")
        propDefault = splitProp[1]
        propName = re.sub(r"^#?\s?", "", splitProp[0])
    else:
        propName = currentProp
        propDefault = ""
    propName = propName.replace("#", "")

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


def processGroups(propName):
    # METRICS = ["cpu", "cpu-mz", "cpu-time", "memory",
    #            "memory-swap", "memory-swap2", "memory-vmmemctl",
    #            "memory-physical", "memory-host", "disk-latency",
    #            "uptime"]
    BACKUPS = ["veeam95u4", "veeam10", "networker", "veeam"]
    PLUGINS = ["amazon", "kvm", "vmx_04",
               "rackspace-cloudservers-uk",
               "softlayer", "esx", "vcenter_cluster",
               "openstack-nova", "packet",
               "hyperv_301", "oracle-ase-emea",
               "azurecompute-arm", "oracle-ase-us",
               "vcd", "xenserver",
               "digitalocean2", "google-compute-engine",
               "rackspace-cloudservers-us", "cloudoorsphere"]
    NETWORKS = ["openstack-neutron", "dnsmasq", "omapi",
                "nsx-ecmp", "logical",
                "nsx-nat", "nsx-gateway"]
    groupTypes = {"\{backupPlugin}": BACKUPS,
                  "\{computePlugin}": PLUGINS,
                  "\{devicePlugin}": NETWORKS}

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

        propDict = {}
        propDict["name"] = copy.deepcopy(propName)
        propDict["default"] = copy.deepcopy(propDefault)
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
            propRange = ""
            propComment = line[1]
            propComment = re.sub(r"^\s?", "", propComment)
            # deal with the case of certain interleaving comments
            if propComment in NARSLIST:
                propComment = NARSCOMMENT
            propRangeFound = re.search(
                r"(Range[\s]*?:[\s]*?)(.*)", propComment)
            if propRangeFound:
                propRangeString = propRangeFound.group(0)
                propRange = propRangeFound.group(2)
                propComment = re.sub(propRangeString, "", propComment)

        propDict["comment"] = copy.deepcopy(propComment)
        propDict["range"] = copy.deepcopy(propRange)
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
    # Remove invalid groups
    for groupToRemoveName in groupToRemove:
        groupDict.pop(groupToRemoveName)

    # print(json.dumps(groupDict, indent=2))

    for groupPattern, groupNameDict in groupDict.items():
        for group, names in groupNameDict.items():
            for prName, groupTag in names.items():
                propertiesDict[prName]["groupName"] = copy.deepcopy(group)
                propertiesDict[prName]["groupTag"] = copy.deepcopy(groupTag)

    for pNae, profList in profileDict.items():
        if pNae in propertiesDict:
            propertiesDict[pNae]["profiles"] = copy.deepcopy(profList)

    PRINTORDER = ["name", "comment", "default", "range",
                  "profiles", "groupName", "groupTag", "realName"]
    with open(os.path.join(outputSubdir, wikiPropertiesFile), 'w') as f:
        count = 0
        sortedProperties = sorted(propertiesDict)
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

# TO DO
# - Replace square brackets in property name with \{ blah }
# - Check order of properties with odd names
# - Add profiles as images
# - Replace name with realName
# - Replace keys with wiki key names (e.g. Property, Description)
# - Check against wiki version
# - Add metrics to file (?)
# - Revise English of file
# - Nicely print Default and Range values
# - Sort weird profile names - add correspondence to RS or API or ?


# Calls the main() function
if __name__ == '__main__':
    main()
