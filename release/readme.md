Confluence Release Scripts
==========================
--------------------------

These Python 3 scripts are designed to help manage a Confluence release and Confluence version spaces.

checkRelease.py
---------------
This script searches for new version pages and master pages. It checks if the master pages have been updated.
It creates an output file with a table of pages in wiki markup format with links to the pages.

testDocReleaseConfluence.py
---------------------------
This script searches for new version pages and master pages. It copies the master pages to another space, 
under a single parent page. The script then updates the master pages with the new version pages. 
It makes it easy to go through the list of updated pages and check the changes to the text.



checkVersionSpace.py
--------------------
This script searches for recent changes in Confluence, discarding pages from a specified new version. 
It then checks for pages of the same name in a version space, and compares the pages. 
Note that it adds new images to the version space. You can later use updateVersionSpace.py to apply the changes.
