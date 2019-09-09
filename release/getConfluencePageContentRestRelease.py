# Python script: getConfluencePageContent
# ---------------------------------------
# Friendly warning: This script is provided "as is" and without any guarantees.
# I developed it to solve a specific problem.
# I'm sharing it because I hope it will be useful to others too.
# If you have any improvements to share, please let me know.
#
# Author: Sarah Maddox
# Source: https://bitbucket.org/sarahmaddox/confluence-full-text-search
# Usage guide: http://ffeathers.wordpress.com
# /2013/04/20/confluence-full-text-search-using-python-and-grep/
#
# A Python script that gets the content
# of all pages in a given Confluence space.
# It puts the content of each page into a
# separate text file, in a given directory.
# The content is in the form of the Confluence "storage format",
# which is a type of XML consisting of HTML with Confluence-specific elements.
#
# This script works with Python 3

import requests
import os
import re
# import sys
# import json
import base64
#import urllib3

def WriteContentToFiles(results,apiUrl):
    for page in results["results"]:
        page_id = str(page["id"])
        # Get the content of the page
        page_uri = apiUrl + '/rest/api/content/' + page_id + "?expand=body.storage"
        p = requests.get(page_uri, headers=apiHeaders)
        # p = requests.get(page_uri, headers=apiHeaders, verify=False)
        pcu = p.json()
        # print ("Getting page %s" % page_uri)
        try:
            unsafe_content = pcu["body"]["storage"]["value"]
        except:
            unsafe_content = ""
            # File name is equal to page name without special characters,
            # plus page ID.
            # Use a regular expression (re) to strip 
            # non-alphanum characters from page name.
        page_name = page["title"]

        print ("\npage_name: " + page_name + "\n")

        page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id

        print ("page_name_qualified: " + page_name_qualified + "\n")

        if ".png" in page_name:
        	pass
        else:	
	        # Open the output file for writing. Will overwrite existing file.
	        # File is in the required output directory.
	        page_file = open(os.path.join(output_path,
	                         page_name_qualified), "w+")
	        # Write a line containing the URL of the page,
	        # marked with asterisks for easy grepping
	        page_file.write("**" + apiUrl + page["_links"]["webui"] + "**\n")

	        # Write the page content to the file, after removing any
	        # weird characters such as a BOM
	        safe_content = str(unsafe_content.encode('ascii',
	                                                      'xmlcharrefreplace'))
	        # almost_safe_content = page_content_unsafe.decode('utf-8-sig')
	        # safe_content = page_content_unsafe.encode('utf-8') 
	        # Remove unwanted characters at beginning and end
	        safe_content = str.lstrip(safe_content, "b'")
	        safe_content = str.rstrip(safe_content, "'")

	        page_file.write(safe_content)
	        page_file.close()


def ListLimitedPages(searchQueryCql,apiUrl):
    limitedUrl = apiUrl + '/rest/api/content/search' + searchQueryCql
    # r = requests.get(apiUrlLimit, headers=apiHeaders, verify=False)
    r = requests.get(limitedUrl, headers=apiHeaders)
    results = r.json()
    for page in results["results"]:
        page_id = str(page["id"])
        # Get the content of the page
        page_uri = apiUrl + '/rest/api/content/' + page_id + '?expand=body.storage'
        p = requests.get(page_uri, headers=apiHeaders)
        # p = requests.get(page_uri, headers=apiHeaders, verify=False)
        # OJO COMMENTED OUT PAGE CONTENT on next line
        # pcu = p.json()
        page_name = page["title"]
        page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id
        pageUrlForList = "**" + apiUrl + page["_links"]["webui"] + "**\n"
        print (pageUrlForList)
    return results
    print("That's all folks!\n")


#urllib3.disable_warnings()
# Get from input: Confluence URL, username, password,
# space key, output directory
apiHeaders = {}
print("G'day! I'm the getConfluencePageContent script.\nGive me a" +
      "Confluence space, and I'll give you the content of all its pages.\n")
site_URL = input("Confluence site URL (exclude protocol & final slash): ")
username = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
onlyGetRecent = input("Get recent files (y/n): ")
getVersion = input("Get version files (y/n): ")
output_directory = input("Output directory (relative to current," +
                             "exclude initial slash, example 'output'): ")
apiUrl = 'https://' + site_URL
apiAccept = 'application/json'
apiHeaders['Accept'] = apiAccept
upwd = username + ":" + pwd
apiAuth = base64.b64encode(upwd.encode())
apiHeaders['Authorization'] = apiAuth

# Create the output directory
# os.mkdir("../output")
output_path = "../" + output_directory
if os.path.isdir(output_path) == True:
	overwrite = input("Directory already exists, overwrite files (y/n):")
	if overwrite not in ("y", "Y", "yes", "YES"):
		sys.exit(0)
else:
	os.mkdir(output_path)

if onlyGetRecent in ("y", "Y", "yes", "Yes", "YES"):
    oGR = "y"
else:
    oGR = ""
if getVersion in ("y", "Y", "yes", "Yes", "YES"):
    gVe = "y"
else:
    gVe = ""

if (oGR or gVe):
    if oGR:
        lastWeekCql = '?cql=space+%3D+\"doc\"+and+lastmodified+>%3D+now(%27-1w%27)'
        pageListRecent = ListLimitedPages(lastWeekCql,apiUrl)
        WriteContentToFiles(pageListRecent,apiUrl)

    if gVe:
        getVersion = '?cql=space+%3D+\"doc\"+and+title+~+\"v463\"'
        pageListVersion = ListLimitedPages(getVersion,apiUrl)
        WriteContentToFiles(pageListVersion,apiUrl)
else:

    # Log in to Confluence
    # server = xmlrpc.client.ServerProxy(site_URL + "/rpc/xmlrpc")
    # token = server.confluence2.login(username, pwd)

    # apiAuth = input("Enter API authorization, e.g. Basic XXXX: ")
    # apiIP = input("Enter API address, e.g. api.abiquo.com: ")
    # upwd = username + ":" + pwd
    # apiAuth = base64.b64encode(upwd.encode())

    # apiUrl = 'https://' + site_URL
    # print (apiUrl)
    apiUrlLimit = apiUrl + '/rest/api/content?spaceKey=' + spacekey + '&limit=200'

    # apiAccept = 'application/json'
    # apiHeaders['Accept'] = apiAccept
    # apiHeaders['Authorization'] = apiAuth

    while True:
        # r = requests.get(apiUrlLimit, headers=apiHeaders, verify=False)
        r = requests.get(apiUrlLimit, headers=apiHeaders)
        results = r.json()
        # Get all the pages in the space
        # pages_list = server.confluence2.getPages(token, spacekey)
        # For each page, get the content of the page and write it out to a file

        WriteContentToFiles(results,apiUrl)
        
        if "next" not in results["_links"]:
            break
        else:
            apiUrlLimit = apiUrl + results["_links"]["next"]
    print("All done! I've put the results in this directory: ",
          output_directory)
