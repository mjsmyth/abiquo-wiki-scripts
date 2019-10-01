# Python script: moveConfluencePages
# ---------------------------------------
# Script designed to move pages with label to underneath another page
#
from atlassian import Confluence
from pprint import pprint

#import requests
#import os
#import re
#import base64
#import json
#import sys
#import copy
#from requests.auth import HTTPBasicAuth

#1. Search for pages by label
#2. Get the content ID and version of the page
#3. Add 1 to the version number
#4. Add "ancestors":[{"id":47535934}] with ID for new parent page
#5. "Rename" the page with fake foo bar replace :-D and save
#
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
# 
# move_to_page_id = "47535936"
# SecondIntranetBackup
move_to_pg_id = 47542249

# Get user credentials and space
site_URL = input("Enter Confluence site URL (exclude protocol & final slash): ")
uname = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
#to_spacekey = input("To space key: ")
label = input("Move pages with label: ")

confluence = Confluence(
    url='https://' + site_URL,
    username=uname,
    password=pwd)

get_start=0
get_limit=3


# Use a while loop to get more than 50 results from limit. 

while True:
    # Get all pages by label
    
    results = confluence.get_all_pages_by_label(label, start=get_start, limit=get_limit)
    pprint(results)

    for page in results:
        pg_id = str(page["id"])
        print ("hello: ",pg_id)

        # assuming no attachments but test just in case
        if "att" not in pg_id:
            pg_name = page["title"]

            # Do a fake replace instead of a rename to force a move. Hopefully no pages with foofoo in their name
            # Can always do a replace of barbar right :-D
            new_page_name = (str(pg_name)).replace("foofoo","barbar")
            page_uri = "https://" + site_URL + '/rest/api/content/' + pg_id
            
            # Get more page details with expands
            page_got = confluence.get_page_by_id(
                page_id=pg_id, 
                expand='ancestors,version,body.storage')

            # Get more page details with expands
            #page_got = p.json()
            #print (str(page_got))

            page_version = page_got["version"]["number"]

            # apparently the list is ordered and this gets the last ancestor ????
            if page_got["ancestors"]:
                current_ancestor_id = (page_got["ancestors"].pop())["id"]
                print("current ancestor: ",current_ancestor_id)

                if current_ancestor_id == str(move_to_pg_id):
                    print ("Page already there: ",pg_id)
                else:
            #        print (str(page_version))
            #        page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id
                    pageUrlForList = "**" + "https://" + site_URL + page["_links"]["webui"] + "**  ID: "+ pg_id + " * version: " + str(page_version)
            #        pageUrlForList = "**" + apiUrl + page["_links"]["webui"] + "** \n"
                    print (pageUrlForList)
                    pg_body = page_got["body"]
            #        page_put = copy.deepcopy(page_got)
            #         page_put = {}
            #         page_put["id"] = pg_id
            #         page_put["type"] = page_got["type"]
            #         page_put["title"] = new_page_name
            #         page_put["status"] = "current"
            # #       page_put["body"] = copy.deepcopy(page_got["body"])
            # #       page_put["ancestors"] = [{"id":47535934}]
            #         page_put["ancestors"] = [{"id": move_to_page_id}]
            #         page_put["space"] = {}
            #         page_put["space"]["key"] = to_spacekey
            #         page_put["version"] = {}
            #         page_put["version"]["number"] = page_version + 1
            #         print ("page_put: ", str(page_put))
            #         page_put_serialized = json.dumps(page_put)
            #        print ("params: ",apiParams,"\n")
            #        print ("headers: ",str(apiHeadersPut),"\n")
                    print ("page uri: ",page_uri)

                    status = confluence.update_page(
                        parent_id=move_to_pg_id,
                        page_id=pg_id,
                        title=new_page_name,
                        body=pg_body) 
                    # NOT SURE WHAT TO DO WITH BODY AS NO CHANGE TO CONTENT

            else:
                print ("Page has no ancestors: ",pg_id)
     
        if "next" not in results["_links"]:
            break
        else:
            get_start = int(results["size"]) + 1
print("That's all folks!\n")