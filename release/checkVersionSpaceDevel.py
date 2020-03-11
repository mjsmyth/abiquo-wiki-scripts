# Python script: checkVersionSpace
# ---------------------------------------
# Uses python 3 :-D
# Requires a local images directory
#
# Second proof of concept script 
# Examine changes from doc space to version space
# Our environment has the master doc wiki and a version wiki at the same time
# May attach screenshots from master space in version space
# In this check version, the update code is commented
#
# Update version space
# ------------------
# 1. Get the pages changed in the last week from the doc space
# 2. Get the corresponding pages from a version space
# 3. Update changed attachments in the doc space (add new files)
#    - maybe should delete existing by name
# 4. Update the version space pages with the content of the doc space pages
#
#
import requests
# import json
from requests.auth import HTTPBasicAuth
from atlassian import Confluence


def GetPageIdByTitle(confluence, spacekey, version_page_name):
    if not confluence.page_exists(
            space=spacekey,
            title=version_page_name):
        print("Nonexistent page: ", version_page_name)
        return None
    else:
        vpage = confluence.get_page_by_title(
            space=spacekey,
            title=version_page_name)
        vpage_id = vpage["id"]
        return vpage_id


def ProcessAttachment(attachments_URL_start,
                      attachments_URL_end,
                      wiki_images_id_current,
                      apiHeaders,
                      uname,
                      pwd,
                      apiPostHeaders,
                      site_URL,
                      pg_id,
                      pg_name):

    # get the attachment and copy to the new space
    # This will only add attachments, not update them,
    image_folder = "images/"
    attachments_URL = attachments_URL_start +\
        pg_name + attachments_URL_end
    # print ("attach URL: ", attachments_URL)
    a = requests.get(
        attachments_URL,
        headers=apiHeaders,
        auth=HTTPBasicAuth(uname, pwd))
    attachments = a.json()

    # Download the attachment to a file
    # and then open the file... :rolleyes
    if "results" in attachments and len(attachments["results"]) > 0:
        download_link = 'https://' + site_URL \
            + str(attachments["results"][0]["_links"]["download"])
        # print ("Download link: ", download_link)
        file_name = image_folder + pg_name
        af = requests.get(
            download_link,
            auth=HTTPBasicAuth(uname, pwd),
            headers=apiPostHeaders)
        open(file_name, 'wb').write(af.content)

        # Add the attachment to the images page
        # in the existing space to update
        new_attachment_url = 'https://' + site_URL +\
            "/rest/api/content/" + wiki_images_id_current +\
            "/child/attachment"

        # ADD ATTACHMENTS TO existing space to update
        # attachment_files_for_upload = {'file': open(file_name, 'rb')}
        # requests.post(
        #     new_attachment_url,
        #     headers=apiPostHeaders,
        #     files=attachment_files_for_upload,
        #     auth=HTTPBasicAuth(uname, pwd))

        return new_attachment_url
        # print ("Page is an attachment: ", pg_id)
        # print ("Page name is: ", pg_name)


def main():
    # Get user credentials and space
    site_URL = input("Enter Confluence site URL (no protocol & final slash): ")
    uname = input("Username: ")
    pwd = input("Password: ")
    spacekey = input("Version space key, e.g. ABI46: ")
    master_spacekey = "doc"
    current_version = input("Current version for image filename, eg v46: ")
    release_version = input("Upcoming version to discard drafts, eg v47: ")
    # current_image_page = current_version + "_images"

    confluence = Confluence(
        url='https://' + site_URL,
        username=uname,
        password=pwd)

    # Image pages
    images_page_name = current_version + "_images"
    wiki_images_id_master = GetPageIdByTitle(confluence,
                                             master_spacekey,
                                             images_page_name)
    wiki_images_id_current = GetPageIdByTitle(confluence,
                                              spacekey,
                                              images_page_name)

    # SEARCH
    cql = 'space.key={} and (lastModified > now("-15d") )'.format(
        master_spacekey)
    # Old search
    # searchQueryCql =
    # '?cql=siteSearch+~+"v463"+and+space+%3D+"COMP"&queryString=v463'
    # Title search: when you enter v46, it gets all v461, v462, v463...
    # searchQueryCql = '?cql=space+%3D+\"COMP\"+and+title+~+\"v461\"'

    # ATTACHMENTS
    # note that encoding of parameters
    # with spaces does not work well
    attachments_URL_start = 'https://' + site_URL +\
        '/rest/api/content/' + wiki_images_id_master +\
        '/child/attachment?filename='
    attachments_URL_end = '&os_authType=basic'
    apiHeaders = {}
    apijson = 'application/json'
    apiHeaders['Accept'] = apijson
    apiPostHeaders = {"X-Atlassian-Token": "nocheck"}
    # apiUrl = 'https://' + site_URL

    attachments_list = []
    pages_list = []
    release_version_pages_list = []

    # PAGING
    # control loop with next set of pages
    start_next = 0

    while True:
        # get pages updated in the recent period from the doc space
        print("cql: ", cql)
        results = confluence.cql(cql, limit=200, start=start_next)

        # Process results as attachments or pages
        for page in results["results"]:
            pg_id = page["content"]["id"]
            pg_name = str(page["content"]["title"])
            print ("Page: ", pg_id, " Name: ", pg_name)
            page_links_web_ui = str(page["content"]["_links"]["webui"])
            print ("page_links_web_ui: ", page_links_web_ui)

            # Don't copy changes to draft pages of future release
            # OJO ---> why not this could be a good backup!
            if release_version.strip().lower() \
                    not in page_links_web_ui.lower():
                # process attachments
                if "att" in pg_id:
                    attachment_url = ProcessAttachment(
                        attachments_URL_start,
                        attachments_URL_end,
                        wiki_images_id_current,
                        apiHeaders,
                        uname,
                        pwd,
                        apiPostHeaders,
                        site_URL,
                        pg_id,
                        pg_name)
                    if attachment_url:
                        attachments_list.append([pg_id,
                                                 pg_name,
                                                 attachment_url])
                else:
                    # Replace to fix encoding or something.
                    version_page_name = (str(pg_name)).replace(
                        "foofoo", "barbar").strip()

                    if not confluence.page_exists(
                            space=spacekey,
                            title=version_page_name):
                        print("Nonexistent page in: ",
                              spacekey,
                              "name: ",
                              version_page_name)
                    else:

                        page_got = confluence.get_page_by_id(
                            page_id=pg_id,
                            expand='ancestors,version,body.storage')

                        master_content = page_got["body"]["storage"]["value"]

                        vpage = confluence.get_page_by_title(
                            space=spacekey,
                            title=version_page_name)

                        vpage_id = vpage["id"]

                        # For checking if page is the same?
                        # vpage_expanded = confluence.get_page_by_id(
                        #    page_id=vpage_id,
                        #    expand='ancestors,body.storage')

                        # Create a new copy of the page to update
                        # in the version space with the master space content

                        # new_version_content = (
                        #    str(master_content)).replace(
                        #    "foofoo", "barbar")
                        # new_version_page_name = (
                        #    str(version_page_name)).replace(
                        #    "foofoo", "barbar")
                        # status = confluence.update_page(
                        #     parent_id=None,
                        #     page_id=vpage_id,
                        #     title=new_version_page_name,
                        #     body=new_version_content)
                        pages_list.append([vpage_id,
                                          version_page_name,
                                          page_links_web_ui])

            else:
                # Page has release version in name
                release_version_pages_list.append([
                    pg_id,
                    pg_name,
                    page_links_web_ui])

        if "next" not in results["_links"]:
            break
        else:
            print("Next: ", results["_links"]["next"])

    with open("output_files/checkVersionSpace.txt", 'w') as outfile:
        header = "|| Page ID || Page Name || Page URL ||\n"
        outfile.write("h3. Pages to update\n")
        outfile.write(header)
        for page_details in pages_list:
            page_line = "| " + (" | ").join(page_details) + " |\n"
            outfile.write(page_line)
        outfile.write("\n")
        outfile.write("h3. Attachments\n")
        outfile.write(header)
        for attachment_details in attachments_list:
            attachment_line = "| " + (" | ").join(attachment_details) \
                + " |\n"
            outfile.write(attachment_line)
        outfile.write("\n")
        outfile.write("h3. Release version pages list\n")
        outfile.write(header)
        for release_version_details in release_version_pages_list:
            release_version_line = "| " + (" | ").join(
                release_version_details) \
                + " |\n"
            outfile.write(release_version_line)
        outfile.write("\n")


# Calls the main() function
if __name__ == '__main__':
    main()
