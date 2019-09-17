# Python script: moveConfluencePages
# ---------------------------------------

import requests
import os
import re
import base64
import json

#1. Get the title of the page we wish to move
#2. Get the content ID and version of the page
# Add "ancestors":[{"id":47535934}]
# curl -X PUT -H "Authorization: ..." -H "Content-Type: application/json" -d 
#              '{"id":1234567,
#                  "type":"page", 
#                   "title":"Your page Title", 
#                   "ancestors":[{"id":9876543}], 
#                   "space":{"key":"xxx"},
#                   "version":{"number":17}}' 
# "https://confluence.ges.symantec.com/rest/api/content/1234567"

site_URL = input("Confluence site URL (exclude protocol & final slash): ")
username = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")

apiUrl = 'https://' + site_URL

apiHeaders = {}
apijson = 'application/json'
apiHeaders['Accept'] = apijson

upwd = username + ":" + pwd
apiAuth = base64.b64encode(upwd.encode())
apiHeaders['Authorization'] = apiAuth

apiHeadersPut = {}
apiHeadersPut['Authorization'] = apiAuth
apiHeadersPut['Content-type'] = apijson

searchQueryCql ='?cql=siteSearch+~+"v461"+and+space+%3D+"COMP"&queryString=v461'
#searchQueryCql = '?cql=space+%3D+\"COMP\"+and+title+~+\"v461\"'

searchUrl = apiUrl + '/rest/api/content/search' + searchQueryCql
print("searchUrl: ",searchUrl)
r = requests.get(searchUrl, headers=apiHeaders)
results = r.json()
print (str(results))
for page in results["results"]:
    page_id = str(page["id"])
    print ("hello: ",page_id)
    if "att" in page_id:
        print("att: ",page_id)
    else:   
        page_name = page["title"]
        new_page_name = (str(page_name)).replace("v461","version461")
        page_uri = apiUrl + '/rest/api/content/' + page_id 
        p = requests.get(page_uri, headers=apiHeaders)
        # p = requests.get(page_uri, headers=apiHeaders, verify=False)
        page_got = p.json()
        page_version = page_got["version"]["number"]
#        print (str(page_version))
#        page_name_qualified = (re.sub(r'([^\s\w]|_)+', '', page_name)) + "-" + page_id
        pageUrlForList = "**" + apiUrl + page["_links"]["webui"] + "** "+ page_id + " * " + str(page_version) +"\n"
#        pageUrlForList = "**" + apiUrl + page["_links"]["webui"] + "** \n"
        print (pageUrlForList)
        page_put = {}
        page_put["id"] = page_id
        page_put["type"] = page_got["type"]
        page_put["title"] = new_page_name
#        page_put["ancestors"] = [{"id":47535934}]
        page_put["ancestors"] = [{"id": 47535936}]
        page_put["space"] = {}
        page_put["space"]["key"] = spacekey
        page_put["version"] = {}
        page_put["version"]["number"] = page_version + 1
        print ("page_put: ", str(page_put), "\n")
        page_put_serialized = json.dumps(page_put)
        try:    
            q = requests.put(page_uri, headers=apiHeadersPut, data=page_put_serialized)
        except:
            print ("Something went wrong")    

print("That's all folks!\n")