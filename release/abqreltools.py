# #!/usr/bin/python3
# Python script: release/releaseTools
# ---------------------------------------
# Script with common tools to use in scripts
# - create master pages for new version
# - do documentation release
#
# Tools
# ------------------
# 1. Get the draft pages with vXXX in name
# 2. Strip version from name to create master page name
# 3. Check if page exists
# 4. Get ID of page
# 5. Get parent ID
# 6. Hide a page
# 7. Create wiki log page


from atlassian import Confluence
import requests
import json


def getVersionPgs(spacekey, release_version, confluence):
    start_next = 0
    returned_size = 1
    while returned_size > 0:
        # get draft pages for release searching on "vXXX"
        cql = "space.key={} and (text ~ {})".format(spacekey, release_version)
        results = confluence.cql(cql, limit=200, start=start_next)
        returned_size = results["size"]
        page_list = []
        for page in results["results"]:
            pg_id = page["content"]["id"]
            # pg_name = str(page["content"]["title"])
            # check the vXXX in title and not only in the page content
            # specific title search will get vXXX when you use vXX
            page_links_web_ui = str(page["content"]["_links"]["webui"])
            if release_version.strip().lower() in page_links_web_ui.lower():
                # only work with pages, not attachments
                if "att" not in pg_id:
                    page_list.append(page)
        return page_list


def getPgFull(confluence, initial_page):
    # Get more page details with expands
    pg_id = initial_page["content"]["id"]
    page_got = confluence.get_page_by_id(
        page_id=pg_id,
        expand='ancestors,version,body.storage')
    return page_got


def getOrigPgName(release_version, page):
    pg_name = str(page["content"]["title"])
    master_page_name = (str(pg_name)).replace(
        release_version, "").strip()
    # maybe use re.sub to only replace at end of string
    #                replace_in_page_name = release_version + "$"
    #                (re.sub(replace_in_page_name,"",pg_name)).strip()
    # or use original page name --> master_page_name = pg_name[:]
    return master_page_name


def checkPgExists(confluence, spacekey, page_name):
    if confluence.page_exists(
            space=spacekey,
            title=page_name):
        return True
    else:
        return False


def updPgRestns(site_URL, inuname, inpsswd,
                spacekey, page_id, restrictions):
    payload = json.dumps(restrictions)
    apiUrl = 'https://' + site_URL
    url = apiUrl + "/rest/experimental/content/" + page_id + "/restriction"
    apiAppJson = "application/json"
    apiHeaders = {}
    apiHeaders["Accept"] = apiAppJson[:]
    apiHeaders["Content-Type"] = apiAppJson[:]
    restrictionsResponse = requests.put(url, verify=False, data=payload,
                                        headers=apiHeaders,
                                        auth=(inuname, inpsswd))
    return restrictionsResponse


def main():
    # Get user credentials and space
    site_URL = input("Enter Confluence site URL (no protocol & final slash): ")
    inuname = input("Username: ")
    inpsswd = input("Password: ")
    spacekey = input("Space key: ")
    release_version = input("Release version, e.g. v463: ")
    # print_version = input("Release print version, e.g. 4.6.3: ")

    confluence = Confluence(
        url='https://' + site_URL,
        username=inuname,
        password=inpsswd)

    versionPageList = getVersionPgs(
        spacekey, release_version, confluence)
    draftPageList = []
    wikiPageList = []

    for page in versionPageList:
        masterPageName = getOrigPgName(release_version, page)
        masterPageExists = checkPgExists(
            confluence, spacekey, masterPageName)
        if masterPageExists is False:
            draftPageList.append(page)

    for page in draftPageList:
        pageFull = getPgFull(confluence, page)
        masterPageName = getOrigPgName(release_version, page)
        ancestorsList = pageFull["ancestors"]
        parentPage = ancestorsList.pop()
        parentPageId = parentPage["id"]

        pageContent = pageFull["body"]["storage"]["value"]
        # print("parentPageId: ", parentPageId)
        # print("masterPageName: ", masterPageName)
        # print("pageContent:", pageContent)

        status = confluence.create_page(spacekey,
                                        masterPageName,
                                        pageContent,
                                        parent_id=parentPageId,
                                        type='page',
                                        representation='storage',
                                        editor='v2')
        if status["id"]:
            newPageId = status["id"]
        else:
            print ("status", status)

        restrictions = [{"operation": "update", "restrictions":
                        {"user": [{"type": "known",
                                   "username": "maryjane.smyth"}],
                         "group": [{"type": "group",
                                    "name": "abiquo-team"}]}},
                        {"operation": "read", "restrictions":
                        {"user": [{"type": "known",
                                   "username": "maryjane.smyth"}],
                         "group": [{"type": "group",
                                    "name": "abiquo-team"}]}}]

        restrictionsResponse = updPgRestns(site_URL, inuname,
                                           inpsswd, spacekey,
                                           newPageId, restrictions)
        if str(restrictionsResponse) != "<response [200]>":
            print("restrictionsResponse: ", restrictionsResponse)
        wikiPageList.append("| " + newPageId + " |"
                            " " + masterPageName + " |"
                            " [" + spacekey + ":" + masterPageName + "] |\n")
    # createWikiLogPage(wikiPageList)


# Calls the main() function
if __name__ == '__main__':
    main()
