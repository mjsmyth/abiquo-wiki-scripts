# Python script: get_bad_links.py
# ---------------------------------------
#
# This script should get all the bad links from a file of grep output
#
# This script works with Python 3.x


def main():
	with open ("files_with_bad_links.txt", "r") as lfile:
		ldata=lfile.readlines()
	ofile = open("bad_link_data.tsv", "w")
	previousLink = ""
	for lrec in ldata:
		plink = ""
		(filename,badlink) = lrec.split(":", 1)
		badlink = badlink.strip("\n")
		pagefiledir = "doc_20221007"
		pagefilename = pagefiledir + "/" + filename
		with open (pagefilename, "r") as pfile:
			plink = pfile.readline()
		plink = plink.strip("\n")

		plink = plink.removesuffix('**')    
		plink = plink.removeprefix('**')  

		plink = plink.replace("https://","",1)	
		oline = pagefilename + "\t" + badlink + "\t" + plink + "\n"
		ofile.write(oline)
	ofile.close()


# Calls the main() function
if __name__ == '__main__':
    main()
