#!/usr/bin/python3
# coding=utf-8
# Python script: checkRelease
# ---------------------------------------
# Script designed to check a release
#
# Check Release
# ------------------
# 1. Get the draft pages
# 2. Get the real pages
# 3. Check if the content is the same
# Log everything as markup table
#
# || Page || Updated ||
# | Backup plugins | (/) |
#

import os
from atlassian import Confluence
from pprint import pprint
from datetime import datetime

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

start_next = 0
returned_size = 1

todaysDate = datetime.today().strftime('%Y-%m-%d')

# td = "2019_11_05"
output_file = "outputCheckRelease." + todaysDate + ".txt"
output_dir = "./output_files"
output_list = []

output_list.append("|| Page ID || Name || Updated || Master present || Attachment || Master || Version || \n")

while returned_size > 0:
    # get draft pages for release searching on "vXXX"
    cql = "space.key={} and (text ~ {})".format(spacekey, release_version)
    print("cql: ", cql)
    results = confluence.cql(cql, limit=200, start=start_next)
    print ("- part a - search for bunch of pages ----------------")
    pprint(results)
    returned_size = results["size"]

    for page in results["results"]:
        pg_id = page["content"]["id"]
        pg_name = str(page["content"]["title"])
        print ("hello: ", pg_id, " Name: ", pg_name)
        # check the vXXX in title and not only in the page content
        # specific title search will get vXXX when you use vXX
        page_links_web_ui = str(page["content"]["_links"]["webui"])
        print ("page_links_web_ui: ", page_links_web_ui)
        #print ("-part 1-------get pages with vXXX----------------------")

        if release_version.strip().lower() in page_links_web_ui.lower():
            # only work with pages, not attachments
            if "att" in pg_id:
                print("Page is an attachment: ", pg_id)
                output_list.append("| " + pg_id + " | " + pg_name + " |  |  | (/) |  |  |\n")
            else:
                # Get more page details with expands
                page_got = confluence.get_page_by_id(
                    page_id=pg_id,
                    expand='ancestors,version,body.storage')

                #print ("-part 2-- got page by ID---------------------------")
                # pprint (page_got)
                draft_content = page_got["body"]["storage"]["value"]
                # For master page name remove the version name from the title
                master_page_name = (str(pg_name)).replace(release_version, "").strip()
                # maybe use re.sub to only replace at end of string
                #                replace_in_page_name = release_version + "$"
                #                (re.sub(replace_in_page_name,"",pg_name)).strip()
                # or use original page name --> master_page_name = pg_name[:]
                print("Master page name spaces: ", master_page_name)

                # print ("-part 3---got master page by title-----------------")

                if not confluence.get_page_by_title(
                        space=spacekey,
                        title=master_page_name):
                    print("Nonexistent page: ", master_page_name)
                    output_list.append("| " + pg_id + " | " + pg_name + " |  | (-) |  |  | [" + spacekey + ":" + pg_name + "]  |\n")
                else:
                    # mpage = json.loads(str(master_page_json))
                    mpage = confluence.get_page_by_title(
                        space=spacekey,
                        title=master_page_name)

                    mpage_id = mpage["id"]
                    # pprint(mpage)
                    print ("Found master page ID: ",mpage_id," Name: ",master_page_name)
                    # print ("-part 3---get page by ID with text in storage format------")
                    mpage_expanded = confluence.get_page_by_id(
                        page_id=mpage_id,
                        expand='ancestors,body.storage')

                    master_page_content = mpage_expanded["body"]["storage"]["value"]

                    if draft_content == master_page_content:
                        output_list.append("| " + mpage_id + "| " + master_page_name + " | (/) | (/) | | [" + spacekey + ":" + master_page_name + "] | [" + spacekey + ":" + pg_name + "] |\n")
                    else:
                        output_list.append("| " + mpage_id + "| " + master_page_name + " | (x) | (/) | | [" + spacekey + ":" + master_page_name + "] | [" + spacekey + ":" + pg_name + "] |\n")
        else:
            output_list.append ("| " + pg_id + " | " + pg_name + " |  |  | |  | [" + spacekey + ":" + pg_name + "] |\n")


    start_next = results["start"] + results["size"]


with open(os.path.join(output_dir, output_file), 'w') as ofil:
    ofil.writelines(output_list)

print ("That's all folks!\n")
