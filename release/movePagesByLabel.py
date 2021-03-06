# Python script: moveConfluencePages
# ---------------------------------------
# Script designed to move pages with label to underneath another page
#
from atlassian import Confluence
from pprint import pprint

# 1. Search for pages by label
# 2. Get the content ID and version of the page
# 3. Add 1 to the version number
# 4. Add "ancestors":[{"id":47535934}] with ID for new parent page
# 5. "Rename" the page with fake foo bar replace :-D and save
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
# This is stable, so just get this from the URL when displaying Page info
# move_to_page_id = "47535936"
# SecondIntranetBackup
# Archived pages in the COMP space
# Archived pages = 47542566
# move_to_pg_id = 47542566
# Archived pages 2 = 47542582
move_to_pg_id = 47542582

# Get user credentials and space
site_URL = input(
    "Enter Confluence site URL (exclude protocol & final slash): ")
uname = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
# to_spacekey = input("To space key: ")
label = input("Move pages with label: ")

confluence = Confluence(
    url='https://' + site_URL,
    username=uname,
    password=pwd)

get_start = 0
get_limit = 3
total_pages = 0
# Use a while loop to get more than 50 results from limit.
while True:
    # Get all pages by label
    results = confluence.get_all_pages_by_label(
        label,
        start=get_start,
        limit=get_limit)
    pprint(results)

    for page in results:
        total_pages = total_pages + 1
        print("total pages: ", total_pages)
        pg_id = str(page["id"])
        print("hello: ", pg_id)

        # assuming no attachments but test just in case
        pg_name = page["title"]

        # Do a fake replace instead of a rename to force a move.
        # Hopefully no pages with foofoo in their name
        # Can always do a replace of barbar right :-D
        new_page_name = (str(pg_name)).replace("foofoo", "barbar")
        page_uri = "https://" + site_URL + '/rest/api/content/' + pg_id
        # Get more page details with expands
        page_got = confluence.get_page_by_id(
            page_id=pg_id,
            expand='ancestors,version,body.storage')

        page_version = page_got["version"]["number"]

        # apparently the list is ordered and this gets the last ancestor
        if page_got["ancestors"]:
            current_ancestor_id = (page_got["ancestors"].pop())["id"]
            print("current ancestor: ", current_ancestor_id)

            if current_ancestor_id == str(move_to_pg_id):
                print("Page already there: ", pg_id)
            else:
                pageUrlForList = "**" + "https://" + site_URL\
                    + page["_links"]["webui"] + "**  ID: "\
                    + pg_id + " * version: " + str(page_version)
                print (pageUrlForList)
                pg_body_text = page_got["body"]["storage"]["value"]
                new_pg_body_value = str(pg_body_text) + " "

                print("page uri: ", page_uri)

                status = confluence.update_page(
                    parent_id=move_to_pg_id,
                    page_id=pg_id,
                    title=new_page_name,
                    body=new_pg_body_value)
                # pprint(status)
        else:
            print("Page has no ancestors: ", pg_id)
    if len(results) < get_limit:
        print("got pages: ", len(results))
        break
    else:
        get_start = total_pages
        print("get start: ", get_start)
print("That's all folks!\n")
