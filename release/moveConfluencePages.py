# Python script: moveConfluencePages
# ---------------------------------------
# Script designed to move draft pages from the main space to under another page
# Use after the release is complete
#
import requests
import os
import re
import base64
import json
import sys
import copy
from requests.auth import HTTPBasicAuth

#1. Get the title of the page we wish to move
#2. Get the content ID and version of the page
#3. Add 1 to the version number
#4. Add "ancestors":[{"id":47535934}]
#5. "Rename" the page with fake foo bar replace :-D
# curl -X PUT -H "Authorization: ..." -H "Content-Type: application/json" -d 
#              '{"id":1234567,
#                  "type":"page", 
#                   "title":"Your page Title", 
#                   "ancestors":[{"id":9876543}], 
#                   "space":{"key":"xxx"},
#                   "version":{"number":17}}' 
# "https://confluence.ges.symantec.com/rest/api/content/1234567"
#
# This is stable, so just get this from the URL when displaying Page information :-D
# testing page = PAGESPARK
# move_to_page_id = "47535936"
# testing page = Completed pages
move_to_page_id = 47526929

# Get user credentials and space
site_URL = input("Enter Confluence site URL (exclude protocol & final slash): ")
username = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
to_spacekey = spacekey[:]
release_version = input("Release version, e.g. v463: ")

# API and Authentication
apiUrl = 'https://' + site_URL
apiHeaders = {}
apijson = 'application/json'
apiHeaders['Accept'] = apijson

# basic page limit is about 20-25 pages
# need to specify you are using basic auth for server
apiParamsLimit = {'os_authType':'basic','limit':'200'}

# if you expand for ancestors to check that page is not already 
#   under the desired page, need to also expand version
apiParams = {'os_authType':'basic','expand':'ancestors,version'}

apiHeadersPut = {}
apiHeadersPut['Content-Type'] = apijson[:]
apiHeadersPut['Accept'] = apijson[:]

# Search for entities containing release_version string - can be attachments
# Can also be pages with the release_version string in the body text
# These will be el¡minated when the 
searchQueryCql ='?cql=siteSearch+~+"' + release_version + '"+and+space+%3D+"' + spacekey + '"&queryString=' + release_version
# Old search
# searchQueryCql ='?cql=siteSearch+~+"v463"+and+space+%3D+"COMP"&queryString=v463'
# Title search: when you enter v46, it gets all v461, v462, v463... 
# searchQueryCql = '?cql=space+%3D+\"COMP\"+and+title+~+\"v461\"'

searchUrl = apiUrl + '/rest/api/content/search' + searchQueryCql

# Use a while loop to get more than 200 results from limit. Hopefully this will never happen
# I would usually expect around 60-80 pages, and as we are not retrieving content, this is okay
while True:
    print("searchUrl: ",searchUrl)
    r = requests.get(searchUrl, headers=apiHeaders, auth=HTTPBasicAuth(username,pwd), params=apiParamsLimit)
    results = r.json()
    #print (str(results)) --> watch out, very big :-D
    for page in results["results"]:
        page_id = str(page["id"])
        print ("hello: ",page_id)

        # check the vXXX or whatever is in the page title and not only in the page content 
        # note that the specific title search will get vXXX when you use vXX (e.g. v463 from v46)
        if release_version.strip().lower() in (str(page["_links"]["webui"])).lower():

            # only move pages, not attachments
            if "att" in page_id:
                print ("Page is an attachment: ",page_id)
            else:   
                page_name = page["title"]

                # Do a fake replace instead of a rename to force a move. Hopefully no pages with foofoo in their name 
                # Can always do a replace of barbar right :-D       
                new_page_name = (str(page_name)).replace("foofoo","barbar")
                page_uri = apiUrl + '/rest/api/content/' + page_id 

                # Get more page details with expands
                p = requests.get(page_uri, headers=apiHeaders, auth=HTTPBasicAuth(username,pwd), params=apiParams)
                page_got = p.json()
                print (str(page_got))

                page_version = page_got["version"]["number"]
                                
                # apparently the list is ordered and this gets the last ancestor ???? 
                if page_got["ancestors"]:
                    current_ancestor_id = (page_got["ancestors"].pop())["id"]
                    print("current ancestor: ",current_ancestor_id)

                    if current_ancestor_id == str(move_to_page_id):
                        print ("Page already there: ",page_id)
                    else:
                #        print (str(page_version))
                #        page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id
                        pageUrlForList = "**" + apiUrl + page["_links"]["webui"] + "**  ID: "+ page_id + " * version: " + str(page_version)
                #        pageUrlForList = "**" + apiUrl + page["_links"]["webui"] + "** \n"
                        print (pageUrlForList)
                #        page_put = copy.deepcopy(page_got)
                        page_put = {}
                        page_put["id"] = page_id
                        page_put["type"] = page_got["type"]
                        page_put["title"] = new_page_name
                        page_put["status"] = "current"
                #       page_put["body"] = copy.deepcopy(page_got["body"])
                #       page_put["ancestors"] = [{"id":47535934}]
                        page_put["ancestors"] = [{"id": move_to_page_id}]
                        page_put["space"] = {}
                        page_put["space"]["key"] = to_spacekey
                        page_put["version"] = {}
                        page_put["version"]["number"] = page_version + 1
                        print ("page_put: ", str(page_put))
                        page_put_serialized = json.dumps(page_put)
                #        print ("params: ",apiParams,"\n")
                #        print ("headers: ",str(apiHeadersPut),"\n")
                        print ("page uri: ",page_uri)
                        try:    
                            q = requests.put(page_uri, headers=apiHeadersPut, auth=HTTPBasicAuth(username,pwd), data=page_put_serialized, params=apiParams)
                            print (str(q),"\n")
                        except:
                            print (r.status_code)    
                else:
                    print ("Page has no ancestors: ",page_id)
        else:
            print ("Page does not have ",release_version," in name: ",(str(page["_links"]["webui"])).lower())                
    if "next" not in results["_links"]:
        break
    else:
        searchUrl = apiUrl + results["_links"]["next"]
print("That's all folks!\n")