# Python script: getConfluencePageContent
# ---------------------------------------
# Friendly warning: This script is provided "as is" and without any guarantees.
# I developed it to solve a specific problem.
# I'm sharing it because I hope it will be useful to others too.
# If you have any improvements to share, please let me know.
#
# Author: Sarah Maddox
# Source: https://bitbucket.org/sarahmaddox/confluence-full-text-search
# Usage guide: http://ffeathers.wordpress.com/2013/04/20/confluence-full-text-search-using-python-and-grep/
#
# A Python script that gets the content of all pages in a given Confluence space.
# It puts the content of each page into a separate text file, in a given directory.
# The content is in the form of the Confluence "storage format",
# which is a type of XML consisting of HTML with Confluence-specific elements.
#
# This script works with Python 2.7.10

import requests
import os
import re
import sys
import json
import base64
#import urllib3


#urllib3.disable_warnings()
# Get from input: Confluence URL, username, password, space key, output directory
apiHeaders = {}
print("G'day! I'm the getConfluencePageContent script.\nGive me a Confluence space, and I'll give you the content of all its pages.\n")
site_URL = raw_input("Confluence site URL (exclude final slash): ")
username = raw_input("Username: ")
pwd = raw_input("Password: ")
spacekey = raw_input("Space key: ")
output_directory = raw_input("Output directory (relative to current, exclude initial slash, example 'output'): ")

# Create the output directory
# os.mkdir("../output")
output_path = "../" + output_directory
os.mkdir(output_path)

# Log in to Confluence
#server = xmlrpc.client.ServerProxy(site_URL + "/rpc/xmlrpc")
#token = server.confluence2.login(username, pwd)

#apiAuth = raw_input("Enter API authorization, e.g. Basic XXXX: ")
#apiIP = raw_input("Enter API address, e.g. api.abiquo.com: ")
upwd = username + ":" + pwd
apiAuth = base64.b64encode(upwd.encode())

apiUrl = 'https://' + site_URL 
print apiUrl
apiUrlLimit = apiUrl + '/rest/api/content?spaceKey=' + spacekey + '&limit=200'
apiAccept = 'application/json'
apiHeaders['Accept'] = apiAccept
apiHeaders['Authorization'] = apiAuth

while True:
#	r = requests.get(apiUrlLimit, headers=apiHeaders, verify=False)
	r = requests.get(apiUrlLimit, headers=apiHeaders)
	results = r.json()


	# Get all the pages in the space
	#pages_list = server.confluence2.getPages(token, spacekey)

	# For each page, get the content of the page and write it out to a file
	for page in results["results"]:
		page_id = str(page["id"])	
	#     # Get the content of the page
		page_uri = apiUrl + '/rest/api/content/' + page_id + "?expand=body.storage"
		p = requests.get(page_uri, headers=apiHeaders)
	#	p = requests.get(page_uri, headers=apiHeaders, verify=False)		
		pcu = p.json()
		print "Getting page %s" % page_uri 
		try:
			page_content_unsafe = pcu["body"]["storage"]["value"]
		except:
			page_content_unsafe = ""
	#     # File name is equal to page name without special characters, plus page ID.
	#     # Use a regular expression (re) to strip non-alphanum characters from page name.
		page_name = page["title"]

		page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id
	#  # Open the output file for writing. Will overwrite existing file.
	#	# File is in the required output directory.
		page_file = open(os.path.join(output_path, page_name_qualified), "w+")
	#	# Write a line containing the URL of the page, marked with asterisks for easy grepping
		page_file.write("**" + apiUrl + page["_links"]["webui"] + "**\n")
	#	
	#     # Write the page content to the file, after removing any weird characters such as a BOM	
		safe_content = str(page_content_unsafe.encode('ascii', 'xmlcharrefreplace'))
	#     # Remove unwanted characters at beginning and end
		safe_content = str.lstrip(safe_content, "b'")
		safe_content = str.rstrip(safe_content, "'")
		page_file.write(safe_content)
		page_file.close()

	if "next" not in results["_links"]:
		break
	else:
		apiUrlLimit = apiUrl + results["_links"]["next"] 	

print("All done! I've put the results in this directory: ", output_directory)