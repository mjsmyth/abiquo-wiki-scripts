#!/usr/bin/python3 -tt
# New attempt at processing Abiquo properties
# Hopefully this time it is developer proof
#
import codecs
import re
import json
# from collections import Counter
import copy


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
    groupTypes = {"{backupPlugin}": BACKUPS,
                  "{computePlugin}": PLUGINS,
                  "{devicePlugin}": NETWORKS}

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
    dirPropertyFile = inputDir + propertyFile

    # NARSPROPERTY = r"#abiquo\.nars\.async\.pool"
    NARSCOMMENT = ("Maximum number of simultaneous operations on a single "
                   "hypervisor or region connection, by type. "
                   "Default abiquo.nars.async.pool.max")

    NARSLIST = ["device plugins", "backup plugins"]

    groupDict = {}
    propertiesDict = {}
    groupStore = []
    propertyDict = {}
    profiles = []
    profilesList = []
    commentStore = []

    # groups in the file are separated by spaces
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

    # separate by the profile section markers
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
                    propertyList.append(propertyLine.strip("\n"))
                    # add each property to the corresponding propfiles
                    for profile in profiles:
                        propertyDict[profile].append(group)
            # get comments without whitespace between them and their properties
            for groupLine in groupLines:
                if groupLine[:] not in propertyList:
                    comment += groupLine.strip("#")
                else:
                    commentStore.append([groupLine, comment])
                    comment = ""

    propDict = {}
    propComment = ""
    propRange = ""

    # list of all properties with comments
    for line in commentStore:

        currentProp = line[0]
        if "=" in currentProp:
            splitProp = currentProp.split("=")
            propDefault = splitProp[1]
            propName = re.sub(r"^#?\s?", "", splitProp[0])
        else:
            propName = currentProp
            propDefault = ""
        propName = propName.replace("#", "")

        # # Metrics group is not in the file :-p
        # metricsGroup = [x for x in lastPropNameList if x in METRICS]
        # if metricsGroup:
        #     print("propName metrics: ", propName, metricsGroup)
        groupTag, groupPattern, groupName = processGroups(propName)

        if groupPattern:
            if groupPattern not in groupDict:
                groupDict[groupPattern] = {}
            if groupName not in groupDict[groupPattern]:
                groupDict[groupPattern][groupName] = []
            groupDict[groupPattern][groupName].append(propName)

        propDict[propName] = {}
        propDict[propName]["name"] = copy.deepcopy(propName)
        propDict[propName]["default"] = copy.deepcopy(propDefault)

        if line[1]:
            propRange = ""
            propComment = line[1]
            propComment = re.sub(r"^\s?", "", propComment)
            # deal with the case of interleaving comments
            if propComment in NARSLIST:
                propComment = NARSCOMMENT
            propRangeFound = re.search(
                r"(Range[\s]*?:[\s]*?)(.*)", propComment)
            if propRangeFound:
                propRangeString = propRangeFound.group(0)
                propRange = propRangeFound.group(2)
                propComment = re.sub(propRangeString, "", propComment)

        propDict[propName]["comment"] = copy.deepcopy(propComment)
        propDict[propName]["range"] = copy.deepcopy(propRange)

        propertiesDict[propName] = copy.deepcopy(propDict)

    # A property group has two or more items
    count = 0
    groupToRemove = []
    for groupPattern, groupNameDict in groupDict.items():
        for g, names in groupNameDict.items():
            count += len(names)
        if count < 2:
            groupToRemove.append(groupPattern)
        count = 0
    # Remove invalid groups
    for groupToRemoveName in groupToRemove:
        groupDict.pop(groupToRemoveName)

    print(json.dumps(groupDict, indent=2))

    # TO DO:
    # - Add valid group names to properties
    # - Add profiles to properties
    # - Write properties to a file


# Calls the main() function
if __name__ == '__main__':
    main()
