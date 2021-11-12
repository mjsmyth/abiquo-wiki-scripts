#!/usr/bin/python3 -tt
# Process the Configuration view options and print extra text from file
# TODO manually change the default view option from 0 to Home
# This script works
#

import sys
import re
import os
import json
import requests
import readline
import copy
from abiquo.client import Abiquo
from abiquo.auth import TokenAuth


def main():
    apiHeaders = {}
    td = "2021-11-11"

    # Enter path in filesystem to a file with the UI tags
    #   for fields cloned from github
    #   ui_path = input("Language file path: ").strip()
    input_subdir = "input_files"
    output_subdir = "output_files" 
    output_file_name = "wiki_config_view_table_" + td + ".txt"
    output_wiki_file_name = "wiki_config_wiki_links_" + td + ".txt"
    #   extra_text_file_name = 'process_config_view_extratext_' + td + '.txt'
    extra_text_file_name = 'process_config_view_extratext_2021-11-11.txt'
    ui_path = "../platform/ui/app/"
    ui_path_lang = ui_path + "lang/"
    ui_path_html = ui_path + "modules/configuration/partials/"

# Get data with requests
    # apiAuth = input("Enter API authorization, e.g. Basic XXXX: ")
    # apiIP = input("Enter API address, e.g. api.abiquo.com: ")
    # # Get system properties data from the API of a fresh Abiquo
    # #    apiAuth = input("Authorization: ").strip()
    # #   apiIP = input("API IP address: ").strip()
    # apiUrl = 'https://' + apiIP + '/api/config/properties'
    # print (apiUrl)
    # apiAccept = 'application/vnd.abiquo.systemproperties+json'
    # apiHeaders['Accept'] = apiAccept
    # apiHeaders['Authorization'] = apiAuth
    # r = requests.get(apiUrl, headers=apiHeaders, verify=False)
    # sp_data = r.json()

    # Abiquo API token
    token = input("Enter token: ")
    apiUrl = input("Enter API URL: ")
    # apiUrl = "https://abiquo.example.com/api"
    api = Abiquo(apiUrl, auth=TokenAuth(token), verify=False)
    # Get the virtual datacenters from the cloud
    code, propertiesList = api.config.properties.get(
        headers={'accept': 'application/vnd.abiquo.systemproperties+json'})
    print("Get UI configuration properties. Response code is: ", code)

# File format is as follows
    # {
    #   "id": 558,
    #   "name": "client.theme.defaultEnterpriseLogoPath",
    #   "value": "theme/abicloudDefault/img/logo.png",
    #   "description": "This is the path to the Enterprise logo used in the app",
    #   "links": [
    #     {
    #       "title": "client.theme.defaultEnterpriseLogoPath",
    #       "rel": "edit",
    #       "type": "application/vnd.abiquo.systemproperty+json",
    #       "href": "https://linatest.bcn.abiquo.com:443/api/config/properties/558"
    #     }
    #   ]
    # },
    # get the list of properties
    configProps = []
    configProps = propertiesList.collection
    # Eliminate the evil default dashboard which is very big and scary

    configProps[:] = [d for d in configProps if d.get('id') != 159]
    # for j in configProps:
    #     if len(j["name"].split(".")) > 3:
    #         print (j["name"] + " : " + j["value"])

    configDict = {j["name"]: j["value"] for j in configProps}
#    for b in configList:
#        print(b[0] + " : " + b[1])

    # # Get wiki links in format client.wiki.xxx.YYY
    # wikiList = list(filter(lambda j: len(j[0].split(".")) > 3, configList))
    # for ll in wikiList:
    #     print (ll[0] + " : " + ll[1])

    # # get UI properties list with format client.xxx.YYY
    # uiList = list(filter(lambda k: len(k[0].split(".")) <= 3, configList))
    # for ll in uiList:
    #     print (ll[0] + " : " + ll[1])

    # Process the language file which has keys and UI labels
    ui_json = ui_path_lang + "lang_en_US_labels.json"
    ui_json_data = open(ui_json)
    ui_data = json.load(ui_json_data)

    uiLabels = dict(filter(lambda elem: "configuration.systemproperties" in elem[0] and ".desc" not in elem[0], ui_data.items()))  
    for x in uiLabels:
        print (x + " ** " + uiLabels[x])
    mainmenuLabels = dict(filter(lambda elem: "mainmenu.button" in elem[0], ui_data.items()))
    # get extra text from file in input files input_files
    extraText = {}
    with open(os.path.join(input_subdir,
                           extra_text_file_name), 'r') as extra_text_file:
        extra_text_all = extra_text_file.read()
        extra_text_list = extra_text_all.split("\n\n")
        for etl in extra_text_list:
            eti = etl.split("=")
            ext = "".join(eti[1:])
            # print ("eti: ", eti)
            extraText[eti[0].strip()] = ext.strip()

    # for et in extraText:
    #     print("| " + et + " | " + extraText[et] + " |")

    # <div class="row"
    #             data-ng-if="('SYSCONFIG_MANAGE_DEFAULT_DASHBOARDS' | isGranted) && ('SYSCONFIG_ALLOW_MODIFY' | isGranted)">
    #            <div class="form-label pl-2">

    htmlTextList = []
    htmlOrder = ["generalform.html",
                 "infrastructureform.html",
                 "networkform.html",
                 "dashboardform.html",
                 "wikilinksform.html",
                 "passwordform.html"]
    for hO in htmlOrder:
        htmlFileWithPath = ui_path_html + hO
        with open(htmlFileWithPath, 'r') as htmlFile:
            htmlTextList.append((htmlFile.read()).strip())
#            htmlTextList.append('<div class="row">\n                <div class="form-label pl-2">')
            htmlTextList.append('<div class="form-label pl-2">')
    allHtmlText = " ".join(htmlTextList)
    splitText = '<div class="form-label pl-2">'
#    splitText = '<div class="row">\n                <div class="form-label pl-2">'
    htmlLabels = allHtmlText.split(splitText)
    tabHeaderRegex = re.compile('configuration\\.tab\\.[\\w]+')
    labelRegex = re.compile(r'configuration\.systemproperties\.[\w]+\.[\w]+\.?[\w]*')
    wikiRegex = re.compile(r'client\.wiki\.[\w]+\.[\w]+')
    sysPropRegex = r"\{\{ (systemProperties\.([\w]+)?)\[\'(.+)?\'\]\.value \}\}"
    # systemProperties.dashboard['client.dashboard.maintenanceEndTime'].value
    valueRegex = re.compile("'client\\.[\\w]+\\.[\\w]+\\.?[\\w]*\\.?[\\w]*'")
    # label:  configuration.systemproperties.wiki.dashboard.managedashboards
    wikiHeaderRegex = re.compile(r'mainmenu\.button\.[\w]+')
    outputOrder = []
    outputWikiLik = []

    for hL in htmlLabels:
        # print ("hL: ", hL)
        wikiLinkEntry = False
        defaultView = False
        checkBox = False
        if "checkbox" in hL:
            checkBox = True
        if "defaultView" in hL:
            defaultView = True
        tabheader = re.findall(tabHeaderRegex, hL)
        if tabheader:
            # print ("th:", tabheader)
            headerName = re.findall("[\\w]+$", tabheader[0])
            headerString = ("|| h6. " + headerName[0].capitalize()
                            + " || Default || Notes || Info ||")
            outputOrder.append(headerString)
        else:
            label = ""
            value = []
            outputList = []
            value = ""
            labelAll = re.findall(labelRegex, hL)
            if labelAll:
                label = labelAll[0]
                print ("label: ", label)
                if label in uiLabels:
                    outputList.append(uiLabels[label])
            if label == "configuration.systemproperties.dashboard.restoredefaultdashboards":
                value = "config.dashboard.restoredefaultdashboards.button"
            else:
                valueQuoted = re.findall(valueRegex, hL)
                if valueQuoted:
                    value = valueQuoted[0].strip("'")
                print("value: ", value)
            if len(value) > 0:
                if value in configDict:
                    if defaultView is True:
                        if configDict[value] == "0":
                            outputList.append(" Home ")
                    elif checkBox is True:
                        if configDict[value] == "0":
                            outputList.append(" (x) ")
                        if configDict[value] == "1":
                            outputList.append(" (/) ")
                    else:
                        valueOutput = configDict[value][:]
                        if r"{client.wiki.version}" in valueOutput:
                            valueOutput = valueOutput.replace(
                                r"{client.wiki.version}", "doc")
                        outputList.append(valueOutput)
                if value in extraText:
                    if extraText[value] == "-":
                        outputList.append(" ")
                    else:
                        outputList.append(extraText[value])

                wikiText = re.search(wikiRegex, value)
                if wikiText:
                    wikiLinkEntry = True

            if wikiLinkEntry is True:
                outputWikiLikLi = "| " + (" | ").join(outputList) + " |  |"
                outputWikiLik.append(outputWikiLikLi)
            else:
                outputMain = "| " + (" | ").join(outputList) + " |  |"
                outputOrder.append(outputMain)
            wikiheader = re.findall(wikiHeaderRegex, hL)
            if wikiheader:
                # print ("wh:", wikiheader)
                # wikiheaderName = re.findall("[\\w]+$", wikiheader[0])
                # wikiheaderString = ("|| h6. " + wikiheaderName[0].capitalize()
                #                     + " || Default || Info ||")
                if wikiheader[0] in mainmenuLabels:
                    wikiheaderName = mainmenuLabels[wikiheader[0]]
                    wikiheaderString = ("|| h6. " + wikiheaderName
                                        + " || Default || Info ||")
                outputWikiLik.append(wikiheaderString)

#
    outfile = open(os.path.join(output_subdir, output_file_name), 'w')
    for outputLine in outputOrder:
        outfile.write(outputLine + "\n")
    outfile.close()

    outwikifile = open(os.path.join(output_subdir, output_wiki_file_name), 'w')
    for wikiLine in outputWikiLik:
        outwikifile.write(wikiLine + "\n")
    outwikifile.close()


# Calls the main() function
if __name__ == '__main__':
    main()
