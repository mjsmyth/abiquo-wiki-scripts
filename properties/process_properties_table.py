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
import json
from abiquo.client import Abiquo
from abiquo.auth import TokenAuth
from pathlib import Path

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


def sortForOutput(propertiesDict):
    for pName, pValue in propertiesDict.items():
        if not propertiesDict[pName]["sortName"]:
            propertiesDict[pName]["sortName"] = copy.deepcopy(
                propertiesDict[pName]["property"])
    sortedPropDict = dict(sorted(propertiesDict.items(),
                                 key=lambda x: x[1]["sortName"]))
    return sortedPropDict


def prepareForWiki(propDict, NEWLINE):
    if "{" in propDict["property"]:
        # Process property names with text in {}
        # Are explicit groups without list members
        # So just escape the { characters in the name and
        # and store it as realName
        propDict["realName"] = re.sub(r"{", r"\{", propDict["property"])
    return propDict


def fixDefault(pName, default):
    # some local defaults are replaced on filesystem during install
    newDefault = default[:]
    if "datacenter.id" in pName:
        newDefault = re.sub("default", "Abiquo", default)
    if "repositoryLocation" in pName:
        newDefault = re.sub("127.0.0.1", r"<IP-repoLoc>", default)
    if "localhost" in default:
        newDefault = re.sub("localhost", r"127.0.0.1", default)
    if "10.60.1.4" in default:
        newDefault = re.sub("10.60.1.4", r"127.0.0.1", default)
    return newDefault


def getCategory(pName, CATEGORYDICT):
    # Anchors are generally the second part of the name
    propSortName = ""
    prop_cat = pName.split(".")
    if prop_cat[0] == "abiquo":
        property_cat = prop_cat[1][:]
    else:
        if prop_cat[0] == "com":
            if prop_cat[1] == "abiquo":
                property_cat = prop_cat[3][:]
                propSortName = ".".join(prop_cat[1:])
            else:
                property_cat = prop_cat[2][:]
        else:
            property_cat = prop_cat[0][:]

    if property_cat in CATEGORYDICT:
        return (copy.deepcopy(CATEGORYDICT[property_cat]), propSortName)
    else:
        return property_cat, propSortName


def getPropNameDefault(currentProp):
    # Split property name into name and default
    # note that default can contain an equals sign
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
    propDefault = fixDefault(propName, propDefault)
    return propName, propDefault


def processGroup(propList, GROUPTYPES):
    groupWorkList = []
    groupList = []
    groupTagList = []
    propDefDict = {}
    propGroupDefDict = {}
    groupName = ""
    myGroup = ""

    for prop in propList:
        propName, propDefault = getPropNameDefault(prop)
        propDefDict[propName] = propDefault

    for propName in propDefDict:
        propName.strip()
        propNameList = propName.split(".")
        # plugins etc are not in first two parts of name
        # filter list of plugins in each list
        # lastPropNameList = propNameList[2:]
        groupWorkList.extend(propNameList[2:])
    reducedSet = set(groupWorkList)
    reducedList = list(reducedSet)
    print("****GROUPFULLLIST: ", reducedList)

    for group, groupList in GROUPTYPES.items():
        for x in reducedList:
            if x in groupList:
                groupTagList.append(x)
                myGroup = copy.deepcopy(group)

    if len(groupTagList) > 0:
        # groupTag = groupTagList[0]
        # This will be the propName
        print("****GROUPTAGLIST: ", groupTagList)
        for tag in groupTagList:
            for name, default in propDefDict.items():
                if tag in name:
                    propGroupDefDict[tag] = default
                    if not groupName:
                        groupName = name.replace(tag, myGroup)
        print("****GROUPNAME: ", groupName)
        return groupName, propGroupDefDict
    return "", ""


def getPropertyValues(propertyList, propertyDict,
                      GROUPTYPES, CATEGORYDICT):
    initialPropName, propDefault = getPropNameDefault(propertyList[0])
    propertyDict["category"], propertyDict["sortName"] = getCategory(
        initialPropName, CATEGORYDICT)
    if len(propertyList) == 1:
        propertyDict["property"] = initialPropName
        propertyDict["default"] = propDefault
    else:
        propertyDict["property"], propertyDict["default"] = processGroup(
            propertyList, GROUPTYPES)
    return(propertyDict)


def processComment(commentList, NEWLINE):
    description = ""
    if len(commentList) < 10:
        for comment in commentList:
            description += comment.strip("#")
    else:
        # Format the long comment with hard newlines
        for comment in commentList:
            description += comment.strip("#") + NEWLINE
    return(description.strip())


def processValid(description):
    foundValid = ""
    newDescription = description[:]
    searchValid = r"(?<=Valid values)[\s]*?[:]?[\s]*?(.*)$"
    foundValid = re.search(searchValid, description)
    if foundValid:
        print ("found valid: ", foundValid.group(1))
    replaceValid = "Valid values" + foundValid.group(0)
    newDescription = re.sub(replaceValid, "", description)
    validValues = foundValid.group(1).strip()
    print("New description: ", newDescription)
    return(newDescription, validValues)


def readFileGetProperties(inputDir, propertyFile,
                          PROFILE_SPACES,
                          propertySearchString,
                          propSearchString,
                          GROUPTYPES,
                          CATEGORYDICT,
                          NEWLINE):
    inputText = Path(os.path.join(inputDir, propertyFile)).read_text()
    textList = inputText.split("\n\n")
    currentProfiles = []
    propertiesDict = {}
    for text in textList:
        # If it's a profile section header "########## REMOTESERVICES" etc
        if re.search(r"#{10}", text):
            roughProfile = copy.deepcopy(text)
            for profileNoSpaces, profileSpaces in PROFILE_SPACES.items():
                if profileSpaces in roughProfile:
                    roughProfile = roughProfile.replace(profileSpaces,
                                                        profileNoSpaces)
            currentProfiles = re.findall(r"[A-Z,1-9]+", roughProfile)

        # If it contains a property
        else:
            propertyDict = {}
            commentList = []
            propertyList = []
            propertyLines = text.split("\n")
            for propertyLine in propertyLines:
                if re.match(propSearchString, propertyLine):
                    propertyList.append(propertyLine)
                else:
                    commentList.append(propertyLine)
            print("CL: ", commentList)
            print("PL: ", propertyList)
            if len(propertyList) >= 1:
                propertyDict = getPropertyValues(
                    propertyList, propertyDict,
                    GROUPTYPES, CATEGORYDICT)
                propertyDict["profiles"] = currentProfiles[:]
                propertyDict["description"] = processComment(commentList,
                                                             NEWLINE)
                if "Valid values" in propertyDict["description"]:
                    propertyDict["description"], propertyDict[
                        "validValues"] = processValid(
                        propertyDict["description"])

                tempPropName = copy.deepcopy(propertyDict["property"])
                propertiesDict[tempPropName] = copy.deepcopy(propertyDict)
            else:
                continue
    return(copy.deepcopy(propertiesDict))


def main():
    token = input("Enter token: ")
    apiUrl = input("Enter API URL: ")
    api = Abiquo(apiUrl, auth=TokenAuth(token), verify=False)
    hypervisorTypes, deviceTypes, \
        backupPluginTypes, draasPluginTypes = getPlugins(api)
    # add "plugins" that aren't "real" plugins
    backupPluginTypes.append("veeam")
    hypervisorTypes.append("esxi")

    PLUGINS = hypervisorTypes + deviceTypes \
        + backupPluginTypes + draasPluginTypes
    PROFILE_SPACES = {"MOUTBOUNDAPI": "M OUTBOUND API",
                      "COSTUSAGE": "COST USAGE"}
    DONT_FORMAT = ["Template to configure guest initial"]
    propertySearchString = r"#?\s?((([\w,\-,\{,\}]{1,60}?\.){1,10})([\w,\-,\{,\}]{1,50}))(=?(.*?))\n"
    propSearchString = r"#?\s?((([\w,\-,\{,\}]{1,60}?\.){1,10})([\w,\-,\{,\}]{1,50}))(=?(.*?))"
    inputDir = '/Users/maryjane/platform/system-properties/src/main/resources/'
    propertyFile = 'abiquo.properties'
    outputSubdir = '/Users/maryjane/abiquo-wiki-scripts/properties/'
    outputPropertyFile = 'test_properties_'
    todaysDate = datetime.today().strftime('%Y-%m-%d')
    wikiPropertiesFile = outputPropertyFile + todaysDate + ".txt"

    CATEGORYDICT = {"stale": "stale sessions",
                    "dvs": "dvs and vcenter",
                    "vi": "virtual infrastructure",
                    "m": "m outbound api"}
    # FMTPRINTORDER = ["Property", "Description", "API",
    #                 "RS", "OA", "DNSMASQ", "COSTUSAGE", "BILLING"]
    FMTPRINTORDER = ["Property", "Description", "API", "RS", "V2V", "OA"]
    NEWLINE = "\\\\"
    # Deprecated plugins
    PLGDEPRC = [r"\.ha\."]
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

    GROUPTYPES = {"{plugin}": PLUGINS, "{metric}": METRICS}
    # Display these lozenges in wiki markup
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
    # Piggyback other profiles into the main columns
    profileColumns = {"SERVER": "SERVER",
                      "REMOTESERVICES": "REMOTESERVICES",
                      "V2VSERVICES": "V2VSERVICES",
                      "MOUTBOUNDAPI": "MOUTBOUNDAPI",
                      "DNSMASQ": "REMOTESERVICES",
                      "COSTUSAGE": "SERVER",
                      "BILLING": "SERVER"
                      }

    propertiesDict = {}
    propertiesDict = readFileGetProperties(inputDir, propertyFile,
                                           PROFILE_SPACES,
                                           propertySearchString,
                                           propSearchString,
                                           GROUPTYPES,
                                           CATEGORYDICT,
                                           NEWLINE)
    propertiesSortedDict = sortForOutput(propertiesDict)
    for propertyName, propertyValue in propertiesSortedDict.items():
        print(propertyName, propertyValue)
    print(json.dumps(propertiesSortedDict, indent=4, sort_keys=True))


# Calls the main() function
if __name__ == '__main__':
    main()
