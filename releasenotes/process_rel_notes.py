#!/usr/bin/python2
## Process the release notes and look for already edited descriptions in the 
## known issues of the previous release notes. Give the option to edit the
## description
## Reads wiki markup and outputs wiki markup
## 
import os
import re
import collections

class Issue:
	def __init__(self,a_issueNo,a_issueType,a_issueDesc):
		self.issueNo=a_issueNo
		self.issueType=a_issueType
		self.issueDesc=a_issueDesc

	def wikiIssueString(self):
		wikiIssueNo = str(self.issueNo)
		wikiIssueType = self.issueType
		wikiIssueDesc = doWikiMarkup(self.issueDesc)        
		return (wikiIssueType,'| %s | %s | | \n' % (wikiIssueNo, wikiIssueDesc))

	def __repr__(self):
		return repr((self.issueNo, self.issueType, self.issueDesc))	

def doWikiMarkup(my_wiki_message):
	a_wiki_message = my_wiki_message.replace(r"\\",r"\\\\")
	a_wiki_message = re.sub("\|","\\\|",a_wiki_message)
	a_wiki_message = re.sub("-","\\\-",a_wiki_message)
#	a_wiki_message = a_wiki_message.strip("\"")
#	a_wiki_message = re.sub(r"\\\\\|",r"\\\|",a_wiki_message)
	a_wiki_message = a_wiki_message.replace("{",r"\{")
	a_wiki_message = a_wiki_message.replace("}",r"\}")
	a_wiki_message = a_wiki_message.replace("[",r"\[")		
	a_wiki_message = a_wiki_message.replace("]",r"\]")
	return a_wiki_message			

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
	previousStore = {}
	currentStore = {}
	editedStore = {}
	revisionList = []


	relNotesOutputFile = "rel_notes_wiki_" + currentVersion + ".txt"

	relNotesStorageFile = "rel_notes_wiki_storage_format_" + previousVersion + ".txt"

	relNotesHeader = "|| Key || Description ||   ||\n"; 


	relNotesPreviousList = [reln.strip() for reln in open(os.path.join(inputSubdir,relNotesStorageFile))]
	previousIssueType = ""
	for relNoteItemPrevious in relNotesPreviousList:		
# check it is a wiki line
# in basic case, it should have some pipe characters
		relNotePrevious = re.split('(?<!=)\|',relNoteItemPrevious)
		if len(relNotePrevious) != 4:
			relNotePreviousString = " ".join(relNotePrevious)
			if re.search("Planned Improvements",relNotePreviousString):
				previousIssueType = "Improvement"
			if re.search("Known Issues",relNotePreviousString):
				previousIssueType = "Issue"				
		else:
#			print "Previous | %s | %s | %s |" % (previousIssueType, str(relNotePrevious[1].strip()),relNotePrevious[2].strip())
			previousIssue = Issue(str(relNotePrevious[1].strip()),previousIssueType,relNotePrevious[2].strip())
			previousStore[str(relNotePrevious[1].strip())] = previousIssue

	relNotesCurrentList = [reln.strip() for reln in open(os.path.join(inputSubdir,relNotesInputFile))]
	currentIssueType = ""
	for relNoteItemCurrent in relNotesCurrentList:		
# check it is a wiki line
# in basic case, it should have some pipe characters
		relNoteCurrent = re.split('(?<!=)\|',relNoteItemCurrent)
		if len(relNoteCurrent) != 4:
			relNoteCurrentString = " ".join(relNoteCurrent)
			if re.search("Improvement",relNoteCurrentString):
				currentIssueType = "Improvement"
			if re.search("Bug",relNoteCurrentString):
				currentIssueType = "Issue"				
		else:
#			print "Current | %s | %s | %s |" % (currentIssueType, str(relNoteCurrent[1].strip()),relNoteCurrent[2].strip())
			currentIssue = Issue(str(relNoteCurrent[1].strip()),currentIssueType,relNoteCurrent[2].strip())
			currentStore[str(relNoteCurrent[1]).strip()] = currentIssue

	validSelection = {"c","p"}

	for currentKey in currentStore:
		reviseSelection = ""
		mySelection = ""		
		print "%s : %s - %s" % (currentStore[currentKey].issueType, currentKey, currentStore[currentKey].issueDesc)
		if currentKey in previousStore:
			print "c: %s" %  currentStore[currentKey].issueDesc	
			print "p: %s" %  previousStore[currentKey].issueDesc
			while mySelection not in validSelection:
				mySelection = raw_input("p = previous, c = current: ").strip()
			else:	
				editedStore[currentKey] = currentStore[currentKey]
				if re.match("p",mySelection):
					editedStore[currentKey].issueDesc = previousStore[currentKey].issueDesc
				# elif re.match("e",mySelection):
				# 	newDescription = raw_input("Enter a new description:").strip()
				# 	confirmNewDesc = raw_input("Enter 'y' to save new description': %s" % newDescription).strip()
				# 	if confirmNewDesc == "y":
				# 		editedStore[currentKey].issueDesc = newDescription		
				# if re.search("r",mySelection):
				# 	revisionList.append(currentKey)
		else:
			editedStore[currentKey] = currentStore[currentKey]

			# mySelection = ""
			# newValidSelection = {"c","cr"}
			# print "c: %s" % currentStore[currentKey].issueDesc
			# while mySelection not in newValidSelection: 
			# 	mySelection = raw_input("c = current, cr=+revise: ").strip()
			# else:	
			# 	editedStore[currentKey] = currentStore[currentKey]		
			# 	# if re.match("e",mySelection):
			# 	# 	newDescription = raw_input("Enter a new description:").strip()
			# 	# 	confirmNewDesc = raw_input("Enter 'y' to save new description': %s" % newDescription).strip()
			# 	# 	if confirmNewDesc == "y":
			# 	# 		editedStore[currentKey].issueDesc = newDescription					
			# 	if re.search("r",mySelection):
			# 		revisionList.append(currentKey)

	outputStore = collections.OrderedDict(sorted(editedStore.iteritems(), key=lambda t: t[1]))			

	outfileWiki = open(os.path.join(outputSubdir,relNotesOutputFile), 'w')

	wikiHeader = "|| Key || Summary || ||"

	headerImprovementPrinted = False
	headerIssuePrinted = False

	for outputKey in outputStore:
	#	print "| %s | %s | %s |" % (outputStore[outputKey].issueType, outputStore[outputKey].issueNo,outputStore[outputKey].issueDesc)					
	# for revisionItem in revisionList:
	# 	print "Revise: %s" % revisionItem

		(currentIssue,outWikiString) = outputStore[outputKey].wikiIssueString()
	
		if currentIssue == "Improvement" and headerImprovementPrinted == False:
			currentIssueHeader = "h4. %s \n" % currentIssue
			outfileWiki.write (currentIssueHeader)

			print ("|| Key || Summary || ||") 
			headerImprovementPrinted = True

		if currentIssue == "Issue" and headerIssuePrinted == False:
			currentIssueHeader = "h4. %s \n" % currentIssue
			outfileWiki.write (currentIssueHeader)

			print "h4. %s \n" % currentIssue
			headerIssuePrinted = True

		outfileWiki.write (outWikiString)	
		print "%s" % outWikiString		

# Calls the main() function
if __name__ == '__main__':
	main()
