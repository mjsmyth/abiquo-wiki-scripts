# #!/usr/bin/python3
# Python script: autoRelease
# ---------------------------------------
# Script designed to perform a release
#
# Do Release
# ------------------
# 1. Get the draft pages
# 2. Get the real pages
# 3. Update the real pages with the content of the draft pages
#
#
import os
from atlassian import Confluence
from datetime import datetime


def get_draft_pages(spacekey, release_version, start_next):
    # get draft pages for release searching on "vXXX"
    cql = "space.key={} and (text ~ {})".format(spacekey, release_version)
    print("cql: ", cql)
    results = confluence.cql(cql, limit=200, start=start_next)
    print ("- part a - search for bunch of pages ----------------")
    # pprint(results)
    return results


# Get user credentials and space
site_URL = input("Enter Confluence site URL (no protocol & final slash): ")
uname = input("Username: ")
pwd = input("Password: ")
spacekey = input("Space key: ")
release_version = input("Release version, e.g. v463: ")
print_version = input("Release print version, e.g. 4.6.3: ")
todaysDate = datetime.today().strftime('%Y-%m-%d')

# Create confluence instance
confluence = Confluence(
    url='https://' + site_URL,
    username=uname,
    password=pwd)

start_next = 0
returned_size = 1

# todaysDate = "2020_02_18"
output_file = "outputDoRelease." + todaysDate + ".txt"
output_dir = "./output_files"
output_list = []

page_header_list = ["Page ID",
                    "Name",
                    "Updated",
                    "Doc present",
                    "Attachment",
                    "Link",
                    "\n"]
page_header = " || ".join(page_header_list)
output_list.append(page_header)
print(page_header)

while returned_size > 0:

    results = get_draft_pages(spacekey, release_version, start_next)
    returned_size = results["size"]

    for draft_page in results["results"]:
        pg_id = draft_page["content"]["id"]
        pg_name = str(draft_page["content"]["title"])
        # check the vXXX in title and not only in the page content
        # specific title search will get vXXX when you use vXX
        draft_page_links_web_ui = str(draft_page["content"]["_links"]["webui"])
        print ("page_links_web_ui: ", draft_page_links_web_ui)

        if release_version.strip().lower() in draft_page_links_web_ui.lower():
            # only work with pages, not attachments
            if "att" in pg_id:
                print ("Page is an attachment: ", pg_id)
                attachment_list = [pg_id,
                                   pg_name,
                                   " ",
                                   " ",
                                   " (/) ",
                                   " ",
                                   "\n"]
                attachment_line = " | ".join(attachment_list)
                output_list.append(attachment_line)
                print(attachment_line)
            else:
                # Get more page details with expands
                page_got = confluence.get_page_by_id(
                    page_id=pg_id,
                    expand='ancestors,version,body.storage')

                # print ("-part 2-- got page by ID---------------------------")
                # pprint (page_got)
                draft_content = page_got["body"]["storage"]["value"]
                # For master page name remove the version name from the title
                master_page_name = (str(pg_name)).replace(
                    release_version, "").strip()
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
                    nonexistent_list = [pg_id,
                                        pg_name,
                                        " ",
                                        " (-) ",
                                        " ",
                                        "[" + spacekey + ":" + pg_name + "]",
                                        "\n"]
                    nonexistent_line = " | ".join(nonexistent_list)
                    output_list.append(nonexistent_line)
                    print(nonexistent_line)
                    print("------- moving on --------------")
                else:
                    # mpage = json.loads(str(master_page_json))
                    mpage = confluence.get_page_by_title(
                        space=spacekey,
                        title=master_page_name)

                    mpage_id = mpage["id"]
                    # pprint(mpage)
                    print ("Found master page ID: ",
                           mpage_id,
                           " Name: ",
                           master_page_name)
                    # print ("-part 3---get page by ID\
                    #        with text in storage format--")
                    mpage_expanded = confluence.get_page_by_id(
                        page_id=mpage_id,
                        expand='ancestors,version,body.storage')
                    # pprint(mpage_expanded)
                    # print(content2)
                    # mpage_expanded = json.loads(mpage_expanded_json)
                    master_page_content = mpage_expanded["body"]["storage"]["value"]
                    if draft_content == master_page_content:
                        updated_list = [mpage_id,
                                        master_page_name,
                                        "(/)",
                                        "(/)",
                                        " ",
                                        "[" + spacekey + ":" + master_page_name + "]",
                                        "\n"]
                        updated_line = " | ".join(updated_list)
                        output_list.append(updated_line)
                    else:
                        notupdated_list = [mpage_id,
                                           master_page_name,
                                           "(x)",
                                           "(/)",
                                           " ",
                                           "[" + spacekey + ":" + master_page_name + "]",
                                           "\n"]
                        notupdated_line = " | ".join(notupdated_list)
                        output_list.append(notupdated_line)

                        new_draft_content = (str(draft_content))\
                            .replace("foofoo", "barbar")
                        new_master_page_name = (str(master_page_name))\
                            .replace("foofoo", "barbar")

                        # Use draft page message
                        print("Page_got[version][message]: ",
                              page_got["version"]["message"])
                        if page_got["version"]["message"] == "":
                            version_message = print_version + " - release --"
                        else:
                            version_message = page_got["version"]["message"]
                        # "version": {"number": latest_page_version + 1,
                        # "message": "Your message goes in here"}

                        status = confluence.update_page(
                            parent_id=None,
                            page_id=mpage_id,
                            version_comment=version_message[:],
                            title=new_master_page_name,
                            body=new_draft_content)

                        print ("Updated master page with title: ",
                               master_page_name)
                        print ("----------- EOR -----------------")

        else:
            print ("Page does not have ",
                   release_version,
                   " in name: ",
                   draft_page_links_web_ui)
            output_list.append("| " + pg_id + " | \
                               " + pg_name + " |  |  | | \
                               " + spacekey + ":" + pg_name + "\
                               ] |\n")

    start_next = results["start"] + results["size"]

with open(os.path.join(output_dir, output_file), 'w') as ofil:
    ofil.writelines(output_list)
print ("That's all folks!\n")
