# Python script: ccloRewriteMapLinks.py
# ---------------------------------------
#
# This script should get all the pages from Confluence Cloud
#
# This script works with Python 3.x

from datetime import datetime
from atlassian import Confluence
import copy
import re
# import dateutil.parser
# import pprint
# from itertools import zip_longest

# The sort_pages section is adapted from Atlassian answers
# https://community.developer.atlassian.com/t/get-space-page-hierarchy-using-the-rest-api/15999/11


def get_metadata(page, site_URL, keylist):
    page_metadata = []
    page_metadata_dict = {}
    Editor = "v1"
    CloudID = str(page["id"])
    Name = str(page["title"])
    page_links_web_ui = str(page["_links"]["webui"])
    CloudURL = site_URL + page_links_web_ui + "/"
    if "editor" in str(page["metadata"]["properties"]):
        Editor = str(page["metadata"]["properties"]["editor"]["value"])
    page_metadata = [Name, CloudID, CloudURL, Editor]

    for key in keylist:
        page_metadata_dict[key] = page_metadata[keylist.index(key)]
    return copy.deepcopy(page_metadata_dict)


def get_a_few_pages(confluence, start_next, spacekey):
    start_next = 0
    results = confluence.get_all_pages_from_space(spacekey,
                                                  start=start_next,
                                                  limit=5, status=None,
                                                  expand='metadata.properties.editor,ancestors',
                                                  content_type='page')
    return results


def get_all_the_pages(confluence, start_next, spacekey):
    results_list = []
    returned_size = 1
    start_next = 0
    while returned_size > 0:
        results = confluence.get_all_pages_from_space(spacekey,
                                                      start=start_next,
                                                      limit=100, status=None,
                                                      expand='metadata.properties.editor,ancestors',
                                                      content_type='page')
        returned_size = len(results)
        print("returned_size: ", returned_size)
        results_list.extend(results)
        start_next = start_next + len(results)
    return results_list


def processResults(cloud_results, confluence_cloud, cloud_site_URL):
    # pp = pprint.PrettyPrinter(indent=4)

    td = datetime.today().strftime('%Y-%m-%d')
    page_filename = "wiki_tree_" + td + ".txt"
    page_file = open(page_filename, "w+")

    # server_list = ["Name", "ServerID", "ServerURL", "Level", "Ancestors"]
    cloud_list = ["Name", "CloudID", "CloudURL", "Editor"]
    header_list = ["CloudURL", "Editor"]
    header = "\t".join(header_list) + "\n"
    page_file.write(header)
    # main_server_dict = {}
    main_dict = {}

    for page in cloud_results:
        cloud_page_metadata = get_metadata(page, cloud_site_URL, cloud_list)

        # /wiki/rest/api/content/{content-id}?expand=metadata.properties.editor

        # print(", ".join(cloud_page_metadata))
        # page_list.append(pg_id + "\t" + pg_name + "\t" + page_links_web_ui)
        main_dict[cloud_page_metadata["Name"]] = \
            copy.deepcopy(cloud_page_metadata)
        # this is Name, CloudID, CloudURL
        # print("CloudURL: ", cloud_page_metadata["CloudURL"])
        # As we add a / to end of CloudURL, get second last section
        serverURLName = cloud_page_metadata["CloudURL"].split("/")[-2]
        if cloud_page_metadata["Name"] == "overview":
            serverURLName = "Abiquo+Documentation+Home"
        tempServerURLName = r"/display/doc/" \
            + re.escape(serverURLName)
        main_dict[cloud_page_metadata["Name"]]["ServerURL"] = \
            tempServerURLName
        main_dict[cloud_page_metadata["Name"]]["CloudURL"] = \
            re.escape(main_dict[cloud_page_metadata["Name"]]["CloudURL"])

    for key, item in main_dict.items():
        print_list = []
        for head_name in header_list:
            print_list.append(item[head_name])
        page_details = "\t".join(print_list) + "\n"
        page_file.write(page_details)

    page_file.close()
    print("That's all folks!\n")


def main():
    # # Get server user credentials and space
    # site_URL = input("Enter Confluence site URL (no final slash): ")
    # uname = input("Username: ")
    # pwd = input("Password: ")
    spacekey = input("Space key: ")

    # confluence = Confluence(
    #     url=site_URL,
    #     username=uname,
    #     password=pwd)

    # Get cloud user credentials and space
    cloud_site_URL = "https://abiquo.atlassian.net/wiki"
    cloud_uname = input("Cloud username: ")
    pwd = input("Cloud token string: ")

    confluence_cloud = Confluence(
        url=cloud_site_URL,
        username=cloud_uname,
        password=pwd,
        cloud=True)

    start_next = 0

    results = get_all_the_pages(confluence_cloud, start_next, spacekey)
    # results = get_a_few_pages(confluence_cloud, start_next, spacekey)
    processResults(results, confluence_cloud, cloud_site_URL)


# Calls the main() function
if __name__ == '__main__':
    main()
