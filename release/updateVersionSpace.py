# Python script: updateVersionSpace
# ---------------------------------------
# Copy changes from doc space to version space
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
from requests.auth import HTTPBasicAuth
import json
from atlassian import Confluence
from pprint import pprint
import os

def GetPageIdByTitle(spacekey,version_page_name):
    if not confluence.get_page_by_title(
            space=spacekey,
            title=version_page_name):
        print("Nonexistent page: ",version_page_name)
    else:        
        vpage = confluence.get_page_by_title(
            space=spacekey,
            title=version_page_name)   
        vpage_id = vpage["id"]
        return vpage_id


# Get user credentials and space
site_URL = input("Enter Confluence site URL (no protocol & final slash): ")
uname = input("Username: ")
pwd = input("Password: ")
spacekey = input("Version space key, e.g. ABI46: ")
master_spacekey = "doc"
current_version = input("Current release version for image file name, e.g v46: ")
release_version = input("Upcoming release version to discard drafts, e.g. v47: ")
current_image_page = current_version + "_images"

confluence = Confluence(
    url='https://' + site_URL,
    username=uname,
    password=pwd)

image_folder = "images/"
images_page_name = current_version + "_images"

# image pages are attached to these pages
# v46_images_id_master = "46470972"
# v46_images_id_current = "47536596"
v46_images_id_master = GetPageIdByTitle(master_spacekey,images_page_name)
v46_images_id_current = GetPageIdByTitle(spacekey,images_page_name)

# Get stuff for using requests - note that encoding of parameters with spaces does not work well
attachments_URL_start = 'https://' + site_URL + '/rest/api/content/' + v46_images_id_master + '/child/attachment?filename=' 
attachments_URL_end = '&os_authType=basic'
apiHeaders = {}
apijson = 'application/json'
apiHeaders['Accept'] = apijson
apiPostHeaders = {"X-Atlassian-Token": "nocheck"}


print("----------------- start --------------------------")
# control loop with next set of pages
start_next = 0

while True:
    # get pages updated in the last week from the doc space
    cql = 'space.key={} and (lastModified > now("-7d") )'.format(master_spacekey)
    print("cql: ", cql)
    results = confluence.cql(cql, limit=200, start=start_next)
    print ("- Search for recenlty modified pages in doc space ----------------")
    pprint(results)

    for page in results["results"]:
        print ("- page ---------------------------------- ----------------")
        pg_id = page["content"]["id"]
        pg_name = str(page["content"]["title"])
        print ("hello: ", pg_id, " Name: ", pg_name)
        page_links_web_ui = str(page["content"]["_links"]["webui"])
        print ("page_links_web_ui: ",page_links_web_ui)

        # Don't copy changes to draft pages to upcoming release 
        # OJO ---> why not this could be a good backup!
        if release_version.strip().lower() not in page_links_web_ui.lower():
            # only work with pages, not attachments
            if "att" in pg_id:
                print ("---------------------------------------------")
                print ("Page is an attachment: ", pg_id)
                print ("Page name is: ", pg_name)
                #as I only add attachments, not update them, get the attachment and copy to the new space
                attachments_URL = attachments_URL_start + pg_name + attachments_URL_end
                print ("attach URL: ", attachments_URL)
                a = requests.get(attachments_URL, headers=apiHeaders, auth=HTTPBasicAuth(uname, pwd))
                attachments = a.json()
                # pprint (attachments)
                # Download the attachment to a file and then open the file... :rolleyes
                download_link = 'https://' + site_URL + str(attachments["results"][0]["_links"]["download"])
                print ("Download link: ",download_link)
                file_name = image_folder + pg_name
                af = requests.get(download_link, auth=HTTPBasicAuth(uname, pwd), headers=apiPostHeaders)
                open(file_name, 'wb').write(af.content)
                attachment_files_for_upload = {'file': open(file_name, 'rb')}
                # Add the attachment to the images page in the existing space to update 
                new_attachment_url = 'https://' + site_URL + "/rest/api/content/" + v46_images_id_current + "/child/attachment"
                requests.post(
                    new_attachment_url, 
                    headers=apiPostHeaders, 
                    files=attachment_files_for_upload, 
                    auth=HTTPBasicAuth(uname, pwd))
                
            else:
                print ("----------------------------------------------------")
                # Get more page details with expands
                page_got = confluence.get_page_by_id(
                    page_id=pg_id, 
                    expand='ancestors,version,body.storage')

                # pprint (page_got)
                master_content = page_got["body"]["storage"]["value"]

                # Do a replace on the page name to fix something about its encoding or something.
                # Not exactly sure why this helps....
                version_page_name = (str(pg_name)).replace("foofoo", "barbar").strip()
                # maybe use re.sub to only replace at end of string
                #                replace_in_page_name = release_version + "$"
                #                (re.sub(replace_in_page_name,"",pg_name)).strip()
                # or use original page name --> master_page_name = pg_name[:]
                print("Version page name spaces: ", version_page_name)

                # print ("-part 3---get page in version space by title-----------------")

                if not confluence.get_page_by_title(
                        space=spacekey,
                        title=version_page_name):
                    print("Nonexistent page: ",version_page_name)
                else:        
                    #mpage = json.loads(str(master_page_json))
                    vpage = confluence.get_page_by_title(
                        space=spacekey,
                        title=version_page_name)   

                    vpage_id = vpage["id"]
                    # pprint(mpage)
                    print ("Found version page ID: ", vpage_id, " Name: ", version_page_name)               
                    #print ("-part 3---get page by ID with text in storage format------")
                    vpage_expanded = confluence.get_page_by_id(
                        page_id=vpage_id,
                        expand='ancestors,body.storage')
                    #pprint(mpage_expanded)
                    # print(content2)
                    #mpage_expanded = json.loads(mpage_expanded_json)

                    # Create a new copy of the page to update in the version space with the changed content
                    new_version_content = (str(master_content)).replace("foofoo","barbar")
                    new_version_page_name = (str(version_page_name)).replace("foofoo","barbar")
                    status = confluence.update_page(
                        parent_id=None,
                        page_id=vpage_id,
                        title=new_version_page_name,
                        body=new_version_content)

                    print ("Updated version page with title: ",version_page_name)
                    print ("----------- EOR -----------------")    

        else:
            print ("Page does not have ", release_version, " in name: ", page_links_web_ui)
    if "next" not in results["_links"]:
        break
    else:
        start_next = int(results["size"]) + 1

print ("That's all folks!\n")