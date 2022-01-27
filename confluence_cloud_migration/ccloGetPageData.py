# Python script: confGetPageData.py
# ---------------------------------------
#
# This script should get all the pages from Confluence Cloud
#
# This script works with Python 3.x

from datetime import datetime
from atlassian import Confluence
import copy
# import dateutil.parser
# import pprint
# from itertools import zip_longest


def get_metadata(page, site_URL, keylist):
    page_metadata = []
    page_metadata_dict = {}
    pg_id = str(page["id"])
    pg_name = str(page["title"])
    page_links_web_ui = str(page["_links"]["webui"])
    pg_url = site_URL + page_links_web_ui
    page_metadata = [pg_name, pg_id, pg_url]
    for key in keylist:
        page_metadata_dict[key] = page_metadata[keylist.index(key)]
    return copy.deepcopy(page_metadata_dict)


def get_a_few_pages(confluence, start_next, spacekey):
    start_next = 0
    results = confluence.get_all_pages_from_space(spacekey,
                                                  start=start_next,
                                                  limit=5, status=None,
                                                  expand=None,
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
                                                      expand=None,
                                                      content_type='page')
        returned_size = len(results)
        print ("returned_size: ", returned_size)
        results_list.extend(results)
        start_next = start_next + len(results)
    return results_list


def processResults(results, confluence, site_URL,
                   cloud_results, confluence_cloud, cloud_site_URL):
    # pp = pprint.PrettyPrinter(indent=4)

    td = datetime.today().strftime('%Y-%m-%d')
    page_filename = "cloud_pages_" + td + ".tsv"
    page_file = open(page_filename, "w+")

    server_list = ["Name", "ServerID", "ServerURL"]
    cloud_list = ["Name", "CloudID", "CloudURL"]
    header_list = ["Name", "ServerURL", "CloudURL", "ServerID", "CloudID"]
    header = "\t".join(header_list) + "\n"
    page_file.write(header)
    main_server_dict = {}
    main_cloud_dict = {}
    main_dict = {}

    for page in results:
        server_page_metadata = get_metadata(page, site_URL, server_list)
        main_server_dict[server_page_metadata["Name"]] = \
            copy.deepcopy(server_page_metadata)

    for page in cloud_results:
        cloud_page_metadata = get_metadata(page, cloud_site_URL, cloud_list)
        # print(", ".join(cloud_page_metadata))
        # page_list.append(pg_id + "\t" + pg_name + "\t" + page_links_web_ui)
        main_cloud_dict[cloud_page_metadata["Name"]] = \
            copy.deepcopy(cloud_page_metadata)

    sorted_main_server_dict = dict(sorted(main_server_dict.items()))
    sorted_main_cloud_dict = dict(sorted(main_cloud_dict.items()))
    for server_name in sorted_main_server_dict:
        if server_name in sorted_main_cloud_dict:
            main_dict[server_name] = \
                copy.deepcopy(sorted_main_server_dict[server_name])
            main_dict[server_name]["CloudID"] = \
                copy.deepcopy(sorted_main_cloud_dict[server_name]["CloudID"])
            main_dict[server_name]["CloudURL"] = \
                copy.deepcopy(sorted_main_cloud_dict[server_name]["CloudURL"])

    # main_list = [{**u, **v} for u, v in zip_longest(sorted_main_server_list,
    #                                                sorted_main_cloud_list,
    #                                                fillvalue={})]
    for key, item in main_dict.items():
        print_list = []
        for head_name in header_list:
            print_list.append(item[head_name])
        page_details = "\t".join(print_list) + "\n"
        page_file.write(page_details)

    page_file.close()
    print ("That's all folks!\n")


def main():
    # Get server user credentials and space
    site_URL = input("Enter Confluence site URL (no final slash): ")
    uname = input("Username: ")
    pwd = input("Password: ")
    spacekey = input("Space key: ")

    confluence = Confluence(
        url=site_URL,
        username=uname,
        password=pwd)

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

    cloud_results = get_all_the_pages(confluence_cloud, start_next, spacekey)
    results = get_all_the_pages(confluence, start_next, spacekey)
    # results = get_a_few_pages(confluence, start_next, spacekey)
    processResults(results, confluence, site_URL,
                   cloud_results, confluence_cloud, cloud_site_URL)


# Calls the main() function
if __name__ == '__main__':
    main()
