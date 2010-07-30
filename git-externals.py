import sys
import os
import re
from os.path import join, abspath, isdir, dirname, split, exists
from os 		 import listdir, mkdir, linesep

# Find .gitexternals files
def findGitExternals(dirToCheck):
	extFiles = []
	for root, dirs, files in os.walk(dirToCheck):
	  if '.gitexternals' in files:
	    extFiles.append(join(root,".gitexternals"))
	
	return extFiles;
	
def getRepos(extFiles):
	repos = {}

	for extFile in extFiles:
		baseDir = split(extFile)
		fileStream = open(extFile, 'r')
		for index, line in enumerate(fileStream):
			line = line.strip()
						
			# Check for comments
			r = line.find('#')
			p = line.find('//')
			if line == '' or not(p and r):
				continue
				
			parts = line.split("=")
			
			# Check for improperly formated strings
			if not(len(parts) == 2) or parts[0] == '' or parts[1] == '':
				exString = 'Line ' + str(index) + ' looks weird: "' + line.replace("\n","") + '" in file: "' + extFile + '". Dunno what to do with it.'
				raise Exception(exString)			
			
			repos[join(baseDir[0], parts[0].strip())] = parts[1].strip()
	return repos

def updateGitIgnore(repos):
	for localFolder in repos.keys():
		gitIgnoreFile = join(split(localFolder)[0], '.gitignore')
		
		# Create .gitignore if it doesn't exist
		if not(exists(gitIgnoreFile)):
			fileStream = open(gitIgnoreFile, 'w')
			fileStream.write('')

# Default settings
# ------------------------------------------------------
startDir = abspath(os.getcwd())					# Start in current directory
extFiles = findGitExternals(startDir)		# Find the locations of the .gitexternals files
repos    = getRepos(extFiles)						# Get a dictionary of repositories and their local paths
print(repos)
updateGitIgnore(repos)
