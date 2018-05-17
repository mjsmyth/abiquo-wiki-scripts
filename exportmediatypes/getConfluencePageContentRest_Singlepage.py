# Python script: getConfluencePageContentRest_Singlepage
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
# A Python script that gets the content of a page by name in a given Confluence space.
# It puts the content of the page into a separate text file, in a given directory.
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


# Get from input: Confluence URL, username, password, space key, output directory
apiHeaders = {}
print("G'day! I'm the getConfluencePageContentRest_Singlepage script.\nGive me a Confluence space and a page name, and I'll give you the content of the pages.\n")
site_URL = raw_input("Confluence site URL (exclude final slash): ")
username = raw_input("Username: ")
pwd = raw_input("Password: ")
spacekey = raw_input("Space key: ")
pageName = raw_input("Page name: ")
# urllib.pathname2url(pageName)
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
contentUrl = 'https://' + site_URL + '/rest/api/content'

payload = {}
payload ['type'] = 'page'
payload['spaceKey'] = spacekey
payload['title'] = pageName
payload['expand'] = 'body.storage'


apiAccept = 'application/json'
apiHeaders['Accept'] = apiAccept
apiHeaders['Authorization'] = apiAuth


r = requests.get(contentUrl, headers=apiHeaders, params=payload, verify=False)
results = r.json()
# print "respone is: %s " % r.text
# print "encoding is: %s " % r.encoding

for page in results["results"]:
	page_id = str(page["id"])	
	try:
		page_content = page["body"]["storage"]["value"]
#		print "page content: %s" % page_content
#		print "printed page content"
	except:
		page_content = ""
		print "no page content found"
	
	page_name = page['title']
	page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id
#  # Open the output file for writing. Will overwrite existing file.
#	# File is in the required output directory.
	page_file = open(os.path.join(output_path, page_name_qualified), "w+")
#	# Write a line containing the URL of the page, marked with asterisks for easy grepping
	page_file.write("**" + apiUrl + page["_links"]["webui"] + "**\n")
#	
#     # Write the page content to the file, after removing any weird characters such as a BOM	
	safe_content = str(page_content.encode('ascii', 'xmlcharrefreplace'))
#     # Remove unwanted characters at beginning and end
	safe_content = str.lstrip(safe_content, "b'")
	safe_content = str.rstrip(safe_content, "'")
	page_file.write(safe_content)
	page_file.close()
		

print("All done! I've put the results in this directory: ", output_directory)
