# Python script: get_bad_links.py
# ---------------------------------------
#
# This script should get all the bad links from a file of grep output
#
# This script works with Python 3.x
import re

def main():
	with open ("links.txt", "r") as lfile:
		ldata=lfile.readlines()
	ofile = open("link_audit_data.tsv", "w")
	ofile.write("Page file name\tFull link\tLink text\tPage link\tLink page\n")
	for lrec in ldata:
		plink = ""
		(filename,alink) = lrec.split(":", 1)
		alink = alink.strip("\n")
		flink = re.search(r'href="(.*?)"', alink)
		fullLink = flink.group(1)[:]
		linkp = ""
		pSection = ""
		if '#' in fullLink:
			linkSplit = fullLink.split('#')
			linkp = linkSplit[0]
			if "-" in linkSplit[1]:
				pSection = linkSplit[1].split('-',1)[1]
		linkt = re.search(r'<a.*?>(.*?)</a>', alink)
		linkText = linkt.group(1)[:]
		pagefiledir = "doc_20221007"
		pagefilename = pagefiledir + "/" + filename
		with open (pagefilename, "r") as pfile:
			plink = pfile.readline()
		plink = plink.strip("\n")

		plink = plink.removesuffix('**')    
		plink = plink.removeprefix('**')  

		plink = plink.replace("https://","",1)	
		oline = pagefilename + "\t" + fullLink + "\t" + linkText + "\t" + plink + "\t" + linkp + "\t" + pSection + "\n"
		ofile.write(oline)
	ofile.close()


# Calls the main() function
if __name__ == '__main__':
    main()
