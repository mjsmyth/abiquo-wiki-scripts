# Python script: confGetPageData.py
# ---------------------------------------
#
# This script should get all the pages and their metadata
# This script is for Confluence Server
# This script works with Python 3.x

from datetime import datetime
from atlassian import Confluence
import pprint
import copy


def get_page_id_from_name(confluence, page_name, start_next, spacekey):
    pp = pprint.PrettyPrinter(indent=4)
    start_next = 0
    print("page_name: ", page_name)
    cql_get_page_id = f"(title=\"{page_name}\" and space =\"{spacekey}\")"
    print("cql_get_page_id: ", cql_get_page_id)
    results_page_id = confluence.cql(cql_get_page_id, start=start_next, limit=None, expand=None, include_archived_spaces=None, excerpt=None)
    pp.pprint(results_page_id)
    page_id = copy.deepcopy(results_page_id["results"][0]["content"]["id"])
    print("page_id: ", page_id)
    return page_id


def get_pages_under_a_page(confluence, page_id, start_next, spacekey):
    pp = pprint.PrettyPrinter(indent=4)
    results_list = []
    returned_size = 1
    start_next = 0
    cql_get_children = f"(parent={page_id})"
    print("cql_get_children: ", cql_get_children)
    # while returned_size > 0:
        # Parent id request:
        # /content/search?cql=(title="foo" and space="bar") => id: 1234
        # Child pages request:
        # /content/search?cql=(parent=1234)
    results_dict = confluence.cql(cql_get_children, start=start_next, limit=None, expand=None, excerpt=None)
        # returned_size = len(results)
        # print ("returned_size: ", returned_size)
        # results_list.extend(results)
        # start_next = start_next + len(results)
    pp.pprint(results_dict)
    return results_dict


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


def processResults(results, confluence, site_URL):
    # pp = pprint.PrettyPrinter(indent=4)
    td = datetime.today().strftime('%Y-%m-%d')
    page_filename = "wiki_pages_" + td + ".tsv"
    page_file = open(page_filename, "w+")

    header_list = ["Page ID", "Name", "URL", "Last upd.", "Created", "Labels"]
    header = "\t".join(header_list) + "\n"
    page_file.write(header)

    for page in results:
        pg_lab_list = []
        page_metadata = []
        pg_id = str(page["id"])
        pg_name = str(page["title"])
        page_links_web_ui = str(page["_links"]["webui"])
        pg_url = site_URL + page_links_web_ui
        pg_history = confluence.history(pg_id)
        # pp.pprint(pg_history)
        pg_u = pg_history['lastUpdated']['when']
        pg_upd = datetime.fromisoformat(pg_u).strftime('%Y-%m-%d')
        pg_c = pg_history['createdDate']
        pg_cre = datetime.fromisoformat(pg_c).strftime('%Y-%m-%d')
        pg_labels = confluence.get_page_labels(pg_id, prefix=None,
                                               start=None, limit=None)
        for lab in pg_labels['results']:
            pg_lab_list.append(lab['name'])
        pg_lab = "\t".join(pg_lab_list)
        # pp.pprint(pg_labels)
        page_metadata = [pg_id, pg_name, pg_url, pg_upd,
                         pg_cre, pg_lab]
        print("\t".join(page_metadata))
        # page_list.append(pg_id + "\t" + pg_name + "\t" + page_links_web_ui)
        page_details = "\t".join(page_metadata) + "\n"
        page_file.write(page_details)

    page_file.close()
    print ("That's all folks!\n")


def processResultsOfCql(results, confluence, site_URL, page_file):
    pp = pprint.PrettyPrinter(indent=4)
    for result in results:
        pg_lab_list = []
        page_metadata = []
        page = copy.deepcopy(result["content"])
        pg_id = str(page["id"])
        pg_name = str(page["title"])
        page_links_web_ui = str(page["_links"]["webui"])
        pg_url = site_URL + page_links_web_ui
        pg_history = confluence.history(pg_id)
        # pp.pprint(pg_history)
        pg_u = pg_history['lastUpdated']['when']
        pg_upd = datetime.fromisoformat(pg_u).strftime('%Y-%m-%d')
        pg_c = pg_history['createdDate']
        pg_cre = datetime.fromisoformat(pg_c).strftime('%Y-%m-%d')
        pg_labels = confluence.get_page_labels(pg_id, prefix=None,
                                               start=None, limit=None)
        for lab in pg_labels['results']:
            pg_lab_list.append(lab['name'])
        pg_lab = "\t".join(pg_lab_list)
        # pp.pprint(pg_labels)
        page_metadata = [pg_id, pg_name, pg_url, pg_upd,
                         pg_cre, pg_lab]
        print(", ".join(page_metadata))
        # page_list.append(pg_id + "\t" + pg_name + "\t" + page_links_web_ui)
        page_details = "\t".join(page_metadata) + "\n"
        page_file.write(page_details)


def main():
    big_dict = []
    # Get user credentials and space
    site_URL = input("Enter Confluence site URL (no final slash): ")
    uname = input("Username: ")
    pwd = input("Password: ")
    spacekey = input("Space key: ")
    page_name = input("Enter parent page for get child pages: ")
    confluence = Confluence(
        url=site_URL,
        username=uname,
        password=pwd)

    # open page file
    td = datetime.today().strftime('%Y-%m-%d')
    page_filename = "wiki_pages_" + td + ".tsv"
    page_file = open(page_filename, "w+")

    header_list = ["Page ID", "Name", "URL", "Last upd.", "Created", "Labels"]
    header = "\t".join(header_list) + "\n"
    page_file.write(header)
    # end open page file

    start_next = 0

    page_id = get_page_id_from_name(confluence, page_name, start_next, spacekey)

    results_dict = get_pages_under_a_page(confluence, page_id, start_next, spacekey)
    # results = get_a_few_pages(confluence, start_next, spacekey)
    # results = get_all_the_pages(confluence, start_next, spacekey)
    
    if results_dict["size"] > 0:            
        for result in results_dict["results"]:
            big_dict.append(copy.deepcopy(result))
            results_dict = get_pages_under_a_page(confluence, result["content"]["id"], start_next, spacekey)
            if results_dict["size"] > 0:
                for result in results_dict["results"]:
                    big_dict.append(copy.deepcopy(result))
                    results_dict = get_pages_under_a_page(confluence, result["content"]["id"], start_next, spacekey)
                    if results_dict["size"] > 0:
                        for result in results_dict["results"]:
                            big_dict.append(copy.deepcopy(result))
                            results_dict = get_pages_under_a_page(confluence, result["content"]["id"], start_next, spacekey)

    processResultsOfCql(big_dict, confluence, site_URL, page_file)

    # close page file
    page_file.close()
    print ("That's all folks!\n")


# Calls the main() function
if __name__ == '__main__':
    main()
