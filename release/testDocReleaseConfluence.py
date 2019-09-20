#!/usr/bin/python3
# coding=utf-8
#
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
from atlassian import Confluence
from pprint import pprint
#import requests
import os
import re
import base64
import json
import sys
import copy
import urllib

# This is stable, so just get this from the URL when displaying Page info
# move_to_page_id = "47535936"
# staging_area_page_id = Completed pages
staging_area_page_id = 47526929

# Get user credentials and space
site_URL = input("Enter Confluence site URL (no protocol & final slash): ")
uname = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
release_version = input("Release version, e.g. v463: ")

confluence = Confluence(
    url='https://' + site_URL,
    username=uname,
    password=pwd)

while True:
    # get draft pages for release searching on "vXXX"
    cql = "space.key={} and (text ~ {})".format(spacekey, release_version)
    print("cql: ", cql)
    results = confluence.cql(cql, limit=200)
    print ("- part a - search for bunch of pages ----------------")
    pprint(results)

    for page in results["results"]:
        pg_id = page["content"]["id"]
        pg_name = str(page["content"]["title"])
        print ("hello: ", pg_id)
        print ("page name: ", pg_name)
        # check the vXXX in title and not only in the page content
        # specific title search will get vXXX when you use vXX
        page_links_web_ui = str(page["content"]["_links"]["webui"])
        print ("page_links_web_ui: ",page_links_web_ui)
        print ("-part 1-------get pages with vXXX----------------------")

        if release_version.strip().lower() in page_links_web_ui.lower():
            # only work with pages, not attachments
            if "att" in pg_id:
                print ("Page is an attachment: ", pg_id)
            else:
                # Get more page details with expands
                page_got = confluence.get_page_by_id(
                    page_id=pg_id, 
                    expand='ancestors,version,body.storage')

                print ("-part 2-- got page by ID---------------------------")
                pprint (page_got)
                # For master page name remove the version name from the title
                master_page_name = (str(pg_name)).replace(release_version, "").strip()
                # maybe use re.sub to only replace at end of string
                #                replace_in_page_name = release_version + "$"
                #                (re.sub(replace_in_page_name,"",pg_name)).strip()
                # or use original page name --> master_page_name = pg_name[:]
                print("master page name spaces: ", master_page_name)
                # Get the master page

                
                print ("-part 3---got master page by title-----------------")
                mpage = confluence.get_page_by_title(space=spacekey, title=master_page_name)
                pprint(mpage)

                #mpage = json.loads(str(master_page_json))
                mpage_id = mpage["id"]

                print ("-part 3---get page by ID with text in storage format------")
                mpage_expanded = confluence.get_page_by_id(page_id=mpage_id, expand='ancestors,body.storage')
                #pprint(mpage_expanded)
                # print(content2)
                #mpage_expanded = json.loads(mpage_expanded_json)
                print ("-part 4---create a new page with the master content --------")
                release_version_dots = ".".join(release_version)
                new_page_title = release_version_dots + "test " + master_page_name

                status = confluence.create_page(
                    space='COMP',
                    title=new_page_title,
                    body=mpage_expanded["body"]["storage"]["value"],
                    parent_id=staging_area_page_id)
                new_page_id = status["id"]
                print("new_page_id: ", new_page_id)

        else:
            print ("Page does not have ", release_version, " in name: ",
                   (str(page["_links"]["webui"])).lower())
    if "next" not in results["_links"]:
        break
    else:
        searchUrl = apiUrl + results["_links"]["next"]
print ("That's all folks!\n")
