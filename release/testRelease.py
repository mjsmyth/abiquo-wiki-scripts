#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Python script: testRelease
# ---------------------------------------
# Script designed to perform a test release and a release
#
# Test Release
# ------------------
# 1. Get the draft pages
# 2. Get the real pages by name after removing the draft vXXX
# 3. Copy the real pages to the draft release area (under releasestaging page)
# 4. Update the staging copies with drafts
# Check by the diffs by hand
#
# coding=utf-8
from atlassian import Confluence
from pprint import pprint
import requests
import os
import re
import base64
import json
import sys
import copy
import urllib
#urllib.quote_plus=urllib.quote
#from requests.utils import requote_uri
from requests.auth import HTTPBasicAuth

# This is stable, so just get this from the URL when displaying Page info
# move_to_page_id = "47535936"
# staging_area_page_id = Completed pages
staging_area_page_id = 47526929

# Get user credentials and space
site_URL = input("Enter Confluence site URL (no protocol & final slash): ")
uname = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
to_spacekey = spacekey[:]
release_version = input("Release version, e.g. v463: ")

# API and Authentication
apiUrl = 'https://' + site_URL
apiHeaders = {}
apijson = 'application/json;charset=UTF-8'
apiHeaders['Accept'] = apijson


confluence = Confluence(
    url='https://wiki.abiquo.com',
    username=uname,
    password=pwd)


# basic page limit is about 20-25 pages
# need to specify you are using basic auth for server
apiParamsLimit = {'os_authType': 'basic', 'limit': '200'}

# if you expand for ancestors to check that page is not already
#   under the desired page, need to also expand version
apiParams = {'os_authType': 'basic', 'expand': 'ancestors,version'}

apiHeadersPut = {}
apiHeadersPut['Content-Type'] = apijson[:]
apiHeadersPut['Accept'] = apijson[:]



# Search for entities containing release_version string - can be attachments
# Can also be pages with the release_version string in the body text
# These will be el¡minated when the
searchQueryCql = '?cql=siteSearch+~+"' + release_version + '"+and+space+%3D+"' + spacekey + '"&queryString=' + release_version
# Old search
# searchQueryCql =
# '?cql=siteSearch+~+"v463"+and+space+%3D+"COMP"&queryString=v463'
# Title search: when you enter v46, it gets all v461, v462, v463...
# searchQueryCql = '?cql=space+%3D+\"COMP\"+and+title+~+\"v461\"'

searchUrl = apiUrl + '/rest/api/content/search' + searchQueryCql

# limit Get 200 results from limit. Hopefully this will never happen
# Usually 60-80 pages, and as we are not retrieving content, this is okay
while True:
    print("searchUrl: ", searchUrl)
    r = requests.get(searchUrl, headers=apiHeaders,
                     auth=HTTPBasicAuth(uname, pwd), params=apiParamsLimit)
    results = r.json()
    # print (str(results)) --> watch out, very big :-D
    for page in results["results"]:
        page_id = page["id"]
        print ("hello: ", page_id)

        # check the vXXX in title and not only in the page content
        # specific title search will get vXXX when you use vXX
        page_links_web_ui = str(page["_links"]["webui"])
        if release_version.strip().lower() in page_links_web_ui.lower():

            # only work with pages, not attachments
            if "att" in page_id:
                print ("Page is an attachment: ", page_id)
            else:
                page_name = str(page["title"])
                page_uri = apiUrl + '/rest/api/content/' + page_id


                #
                # Get more page details with expands
                p = requests.get(page_uri, headers=apiHeaders,
                                 auth=HTTPBasicAuth(uname, pwd),
                                 params=apiParams)
                page_got = p.json()
                print ("page name: ", page_name)
                print (str(page_got))
                
                #
                # For master page name remove the version name from the title
                master_page_name = (str(page_name)).replace(release_version, "").strip()
                # going to start using re.sub to only replace at end of string
                # replace_in_page_name = release_version + "$"
                # mpn = (re.sub(replace_in_page_name,"",page_name)).strip()

                print("master page name spaces: ", master_page_name)
                # master_page_name_encoded = urllib.parse.quote(master_page_name)
                # Get the master page
            #    master_page_uri = apiUrl + '/rest/api/content'
            #    payload = {"title" : master_page_name, "spaceKey" : spacekey, "ie" : "UTF-8", "os_authType" : "basic" }
            #    mp_params = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
            #    master_page_uri_with_params = master_page_uri + '?spaceKey=' + spacekey + '&title=' + master_page_name
            #    master_page_uri_with_auth = master_page_uri_with_params + '&os_authType=basic&ie=UTF-8'
            #    requote_uri(master_page_uri_with_auth)
            #    m = requests.get(master_page_uri_with_auth, headers=apiHeaders, auth=HTTPBasicAuth(uname, pwd))
            #    m = requests.get(master_page_uri_with_auth, headers=apiHeaders, auth=HTTPBasicAuth(uname, pwd))
            #    master_page_got = m.json()

            #    if master_page_got:
            #        print ("Master page got: ", master_page_got)

                # Get content if you know Space and Title
                master_page_json = confluence.get_page_by_title(space=spacekey, title=master_page_name)
                pprint(master_page_json)

                mpage = json.loads(str(master_page_json))
                mpage_id = mpage["id"]

                # If you know page_id of the page
                mpage_expanded = confluence.get_page_by_id(page_id=mpage_id, expand='ancestors,body')
                pprint(mpage_expanded)
                # print(content2)
                #mpage_expanded = json.loads(mpage_expanded_json)


        else:
            print ("Page does not have ", release_version, " in name: ",
                   (str(page["_links"]["webui"])).lower())
    if "next" not in results["_links"]:
        break
    else:
        searchUrl = apiUrl + results["_links"]["next"]
print ("That's all folks!\n")
