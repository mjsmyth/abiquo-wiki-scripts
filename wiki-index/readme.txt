Use Sarah Maddox's script:
mjsmyth@mjsmyth:~/confluence-full-text-search (master) $ python getConfluencePageContent.py

Use command:
find . -type f -print0 | xargs -0 grep -H -P -o "(?<=Resource URI:&nbsp;<strong>).*?<|(?<=Resource URI:[\s]<strong>).*?<" | sort 

