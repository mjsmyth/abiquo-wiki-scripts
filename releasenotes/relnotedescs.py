#!/usr/bin/python2 -tt
## Process the release notes and look for already edited descriptions in the 
## known issues of the previous release notes. Give the option to edit the
## description
## Reads wiki markup and outputs wiki markup
## 
##
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

# Get the file
# TODO get from Confluence
	relNotesInputFile = "process_rel_notes_" + previousVersion + ".txt"
	FS = "|"
	improvLines = {}
	improvSorted = {}
	issueLines = {}
	issueSorted = {}

	relNotesOutputFile = "wiki_rel_notes_" + todaysDate + ".txt"

	relNotesHeader = "|| Key || Description ||   ||\n"; 

	relNotesInputList = [rn.strip() for rn in open(os.path.join(inputSubdir,relNotesInputFile))]

	for relNoteItem in relNotesInputList:		
# check it is a wiki line
# in basic case, it should have some pipe characters
		
		relNote = re.split('(?<!=)\|',relNoteItem)
		print "relNote: %s %s" % (str(relNote[1]),str(relNote[2])



