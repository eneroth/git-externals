import sys
import os
import re
import subprocess
from os.path import join, abspath, isdir, dirname, split, exists, isfile
from os      import listdir, mkdir, linesep

# Find .gitexternals files
def findGitExternals(dirToCheck):
  extFiles = []
  for root, dirs, files in os.walk(dirToCheck):
    if '.gitexternals' in files:
      extFiles.append(join(root,".gitexternals"))
  
  return extFiles;
  
def getRepos(extFiles):
  repos = {}

  for fileIndex, extFile in enumerate(extFiles):
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

# Update git ignore files
# ----------------------------------------------------------------------------------------------
def updateGitIgnore(repos):
  # Make list of SVN folder names and .gitignore-files
  gitIgnoreFiles = {}
  
  for index, localFolder in enumerate(repos.keys()):
    tmp     = split(localFolder)
    baseDir = tmp[0]
    name    = tmp[1]
    gitFile = join(baseDir, '.gitignore')
    
    if gitFile in gitIgnoreFiles:
      gitIgnoreFiles[gitFile].append(name)
    else:
      gitIgnoreFiles[gitFile] = [name]
  
  # Modify .gitignore files
  gitExtMark = "# gitexternals"
  gitExtMessage = gitExtMark + '\n';
  gitExtMessage += "# The line above is a marker that the git-externals script looks for. DO NOT CHANGE IT!\n"
  gitExtMessage += "# Everything beneath this section is automatically added by git-externals script\n"
  gitExtMessage += "# Please add anything else ABOVE this section\n"
  gitExtMessage += "# -------------------------------------------------------------------------------------"
  
  for gitIgnoreFile, subFolders in gitIgnoreFiles.items():
    # Read file, if it exists
    toWrite = ''
    
    if isfile(gitIgnoreFile):
      fileStream = open(gitIgnoreFile, 'r')
      
      for index, line in enumerate(fileStream):
        if not(line.strip().find(gitExtMark)):
          break
        else:
          toWrite += line
      
    
    toWrite += gitExtMessage

    for subFolder in subFolders:
      toWrite += '\n' + subFolder

    fileStream = open(gitIgnoreFile, 'w')
    fileStream.write(toWrite)  

def updateRepos(repos):
  
  for index, val in enumerate(repos.items()):
    localFolder  = val[0]
    remoteFolder = val[1]
    log = 'Results of SVN update:\n'

    if split(localFolder)[1] in sys.argv or not(len(sys.argv) - 1):
      retCode = ''
      if isdir(localFolder):
        printString = renderPercentage(index + 1, len(repos.items())) + " Updating repository: " + split(localFolder)[1]
        retcode = subprocess.check_output(["svn", "update", localFolder])
      else:
        printString = renderPercentage(index + 1, len(repos.items())) + " Checking out repository: " + split(localFolder)[1]
        retcode = subprocess.check_output(['svn', 'co', remoteFolder, localFolder])
      print(printString)
      
      log += split(localFolder)[1] + "\n" + retCode
      
    print(log)
# Formatting functions
# ----------------------------------------------------------------------------------------------
def getEscapeChars(inString):
  return '\b' * len(inString)

def getLeadingFiller(num, maxSize):
  numLength     = len(str(num))
  maxSizeLength = len(str(maxSize))
  return (' ' * (maxSizeLength - numLength))

def renderRepoCounter(num, maxSize):
  maxSizeString = str(maxSize)
  numString     = getLeadingFiller(num, maxSize) + str(num)
  return "(" + numString + "/" + maxSizeString + ")"

def renderPercentage(num, max):
  percentage = int(num/max*100)
  return getLeadingFiller(percentage, 100) + str(percentage) +  "%"

# Default settings
# ----------------------------------------------------------------------------------------------
startDir = abspath(os.getcwd())          # Start in current directory
extFiles = findGitExternals(startDir)    # Find the locations of the .gitexternals files
repos    = getRepos(extFiles)            # Get a dictionary of repositories and their local paths
updateGitIgnore(repos)                   # Update the .gitignore file appropriately        
updateRepos(repos)                       # Update/check out the repositories