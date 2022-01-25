# Python script: confGetPageData.py
# ---------------------------------------
#
# This script should get all the pages and all their metadata
#
# This script works with Python 3.x

from datetime import datetime
from atlassian import Confluence
# import pprint


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
    page_filename = "page_METADATA_" + td + ".tsv"
    page_file = open(page_filename, "w+")

    header_list = ["Page ID", "Name", "URL", "Last upd.", "Created", "Labels"]
    header = "\t".join(header_list)
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
        pg_lab = ", ".join(pg_lab_list)
        # pp.pprint(pg_labels)
        page_metadata = [pg_id, pg_name, pg_url, pg_upd,
                         pg_cre, pg_lab]
        print(", ".join(page_metadata))
        # page_list.append(pg_id + "\t" + pg_name + "\t" + page_links_web_ui)
        page_details = "\t".join(page_metadata) + "\n"
        page_file.write(page_details)

    page_file.close()
    print ("That's all folks!\n")


def main():
    # Get user credentials and space
    site_URL = input("Enter Confluence site URL (no final slash): ")
    uname = input("Username: ")
    pwd = input("Password: ")
    spacekey = input("Space key: ")

    confluence = Confluence(
        url=site_URL,
        username=uname,
        password=pwd)

    start_next = 0

    # results = get_a_few_pages(confluence, start_next, spacekey)
    results = get_all_the_pages(confluence, start_next, spacekey)
    processResults(results, confluence, site_URL)


# Calls the main() function
if __name__ == '__main__':
    main()
