#!/usr/bin/python2
## Process the release notes and look for already edited descriptions in the 
## known issues of the previous release notes. Give the option to edit the
## description
## Reads wiki markup and outputs wiki markup
## 
import os
import re

class Issue:
	def __init__(self,a_issueNo,a_issueType,a_issueDesc):
		self.issueNo=a_issueNo
		self.issueType=a_issueType
		self.issueDesc=a_issueDesc

	def wiki_issue_string(self):
		wikiIssueNo = str(self.issueNo)
		wikiIssueType = self.issueType
		wikiIssueDesc = doWikiMarkup(self.issueDesc)        
		return (wikiIssueType,'| %s | %s | | \n' % (wikiIssueNo, wikiIssueDesc))

def main():
	inputSubdir = "input_files"
	outputSubdir = "output_files"
	todaysDate = "2016-06-27"
	previousVersion = "v382"
	currentVersion = "v383"

# Get the input file 
# TODO get from Confluence
	relNotesInputFile = "rel_notes_draft_" + currentVersion + ".txt"
	FS = "|"
	improvLines = {}
	improvSorted = {}
	issueLines = {}
	issueSorted = {}

	relNotesOutputFile = "rel_notes_wiki_" + currentVersion + ".txt"

	relNotesEditedFile = "rel_notes_wiki_" + previousVersion + ".txt"
	relNotesStorageFile = "rel_notes_wiki_storage_format_" + previousVersion + ".txt"

	relNotesHeader = "|| Key || Description ||   ||\n"; 


	relNotesInputList = [reln.strip() for reln in open(os.path.join(inputSubdir,relNotesStorageFile))]
	currentIssueType = ""
	for relNoteItem in relNotesInputList:		
# check it is a wiki line
# in basic case, it should have some pipe characters
		relNote = re.split('(?<!=)\|',relNoteItem)
		print "%d" % (len(relNote))
		if len(relNote) != 4:
			relNoteString = " ".join(relNote)
			if re.search("Planned Improvements",relNoteString):
				currentIssueType = "Improvement"
			if re.search("Known Issues",relNoteString):
				currentIssueType = "Issue"				
		else:
			print "relNote: %s %s %s" % (currentIssueType, str(relNote[1]),str(relNote[2]))


# Calls the main() function
if __name__ == '__main__':
	main()
