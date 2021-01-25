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

    STUPIDLIST = ["#device plugins", "#backup plugins"]
    METRICS = ["cpu", "cpu-mz", "cpu-time", "memory",
               "memory-swap", "memory-swap2", "memory-vmmemctl",
               "memory-physical", "memory-host", "disk-latency",
               "uptime"]
    PLUGINS = ["amazon", "kvm", "vmx_04",
               "rackspace-cloudservers-uk",
               "softlayer", "esx", "vcenter_cluster",
               "openstack-nova", "packet",
               "hyperv_301", "oracle-ase-emea",
               "azurecompute-arm", "oracle-ase-us",
               "vcd", "xenserver",
               "digitalocean2", "google-compute-engine",
               "rackspace-cloudservers-us", "cloudoorsphere",
               "openstack-neutron", "nsx-gateway",
               "nsx-nat", "logical", "nsx-ecmp",
               "omapi", "dnsmasq",
               "veeam95u4", "veeam10", "networker", "veeam"]
    DEVICES = ["openstack-neutron", "dnsmasq", "omapi",
               "nsx-ecmp", "logical",
               "nsx-nat", "nsx-gateway"]

    propertiesList = []
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
            # find all the properties in a group
            pValue = re.finditer(propertySearchString, group)
            if pValue:
                for pv in pValue:
                    propertyLine = pv.group(0)
                    propertyList.append(propertyLine.strip("\n"))
                    # add each property to the corresponding propfiles
                    for profile in profiles:
                        propertyDict[profile].append(group)
            # get comments without whitespace between them
            for groupLine in groupLines:
                if groupLine[:] not in propertyList:
                    comment += groupLine.strip("#")
                    if groupLine[:] in STUPIDLIST:
                        comment = commentStore[-1][-1]
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
        propNameList = propName.split(".")
        # plugins etc are not in first two parts of name
        # filter list of plugins in each list
        lastPropNameList = propNameList[2:]
        metricsGroup = [x for x in lastPropNameList if x in METRICS]
        if metricsGroup:
            print("propName metrics: ", propName, metricsGroup)

        devicesGroup = [x for x in lastPropNameList if x in DEVICES]
        if devicesGroup:
            print("propName devices: ", propName, devicesGroup)

        pluginsGroup = [x for x in lastPropNameList if x in PLUGINS]
        if pluginsGroup:
            print("propName devices: ", propName, pluginsGroup)

        propDict[propName] = [propName, propDefault]

        if line[1]:
            propRange = ""
            propComment = line[1]
            propComment = re.sub(r"^\s?", "", propComment)
            propRangeFound = re.search(
                r"(Range[\s]*?:[\s]*?)(.*)", propComment)
            if propRangeFound:
                propRangeString = propRangeFound.group(0)
                propRange = propRangeFound.group(2)
                propComment = re.sub(propRangeString, "", propComment)

        propDict[propName].append(propComment)
        propDict[propName].append(propRange)
    propertiesList.append(propDict)

#    for props in propertiesList:
#        print(json.dumps(props, indent=2))


        # numberOfNameOccurrences = Counter(
        #     propNameOccurs.split(" "))
        # propDict[propName].append(numberOfNameOccurrences)

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
