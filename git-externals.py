import sys
import os
import re
import subprocess
from os.path import join, abspath, isdir, dirname, split, exists, isfile, relpath
from os      import listdir, mkdir, linesep

# Globals
svnIdentifier = "SVN"
gitIdentifier = "GIT"
acceptedRepoTypes = [svnIdentifier, gitIdentifier]

# Find .gitexternals files
##########################
def findGitExternals(dirToCheck):
  extFiles = []
  for root, dirs, files in os.walk(dirToCheck):
    if '.gitexternals' in files:
      extFiles.append(join(root,".gitexternals"))
  
  return extFiles;
  
# Retrieve repos from files
###########################
def getRepos(extFiles):
  repos = {}

  for fileIndex, extFile in enumerate(extFiles):
    baseDir = split(extFile)
    fileStream = open(extFile, 'r')
    
    repoType = ''
    
    for index, line in enumerate(fileStream):
      # Ignore whitespace
      line = line.strip()
            
      # First, check for comments
      if line == '' or not(line.find('#') and line.find('//')):
        continue
        
      # Then, check for types
      elif not(line.find('[')) and not(line.find(']') == -1):
        repoType = line.strip("[] ").upper()
        
        if not(repoType in acceptedRepoTypes):
          exString  = "I don't know how to handle repositories of type '" + repoType + "'.\n"
          exString += "Have a look in file: '" + extFile + "', on line " + str(index) + " and amend this."
          raise Exception(exString)
        
      # Lastly, check for repo lines
      else:
        # Check that a repo type is set
        if repoType == '':
          exString = "\nYou must declare the type of repository using a header, for example:\n  [svn]\n  repoName1 = svn://example.com/svnRepo"
          exString += "\n\n  [git]\n  repoName2 = git://github.com/eneroth/git-externals.git"
          exString += "\n\nHave a look in file: '" + extFile + "' and amend this."
          raise Exception(exString)
          
        else:    
          parts = line.split("=")
          
          # Check for improperly formated strings
          if not(len(parts) == 2) or parts[0] == '' or parts[1] == '':
            exString = 'Line ' + str(index) + ' looks weird: "' + line.replace("\n","") + '" in file: "' + extFile + '". Dunno what to do with it.'
            raise Exception(exString)      
          
          else:
            repoName = join(baseDir[0], parts[0].strip())
            repoUrl  = parts[1].strip()
          
            if not(repoType in repos):
              repos[repoType] = {}
            
            repos[repoType][repoName] = repoUrl

  
  return repos

# Update git ignore files
#########################
def updateGitIgnore(repos):
  if svnIdentifier in repos:
    xxxRepos = {}
    xxxRepos.update(repos[svnIdentifier])
  
    # Make list of SVN folder names and .gitignore-files
    gitIgnoreFiles = {}
    
    for index, localFolder in enumerate(xxxRepos.keys()):
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

# Update repositories
#####################
def updateRepos(repos):
  log = {}
  
  # Get list of existing remotes
  remoteList = subprocess.check_output(['git', 'remote']).decode("utf-8").split()
  
  for repoGroup, xxxRepos in repos.items():    
    print("\nUpdating " + repoGroup + ":")
    for index, val in enumerate(xxxRepos.items()):
      localFolder  = val[0]
      remoteFolder = val[1]
      
      if split(localFolder)[1] in sys.argv or not(len(sys.argv) - 1):
        retCode = ''
        printString = renderRepoCounter(index + 1, len(xxxRepos.items()))
        localName = split(localFolder)[1]
      
        # If SVN
        if repoGroup.upper() == svnIdentifier:
          if isdir(localFolder):
            printString += " Updating: " + localName
            print(printString)
            
            retCode += updateSVN(localFolder, remoteFolder)
  
          else:
            printString += " Creating: " + localName
            print(printString)
  
            retCode += checkoutSVN(localFolder, remoteFolder)
        
        # If GIT
        elif repoGroup.upper() == gitIdentifier:        
          if localName in remoteList:
            printString += " Updating: " + localName
            print(printString)
            
            retCode += updateGIT(localFolder, remoteFolder)
          elif isdir(localFolder):
            printString += " Reestablishing: " + localName
            print(printString)
            
            retCode += reestablishGIT(localFolder, remoteFolder)
          else:
            printString += " Creating: " + localName
            print(printString)
  
            retCode += checkoutGIT(localFolder, remoteFolder)   
            
        # Log writing
        if retCode:
          tmpLog = ""
          retCode = retCode.strip()
          
          if retCode.count("\n"):
            tmpLog += re.sub(r'\n+', '\n\t', "\n" + retCode)
          else:
            tmpLog += retCode
            
          tmpLog += "\n"
          
          log[split(localFolder)[1]] = tmpLog
    
  printLog(log)

# Print log
def printLog(log):
  longestName = 0;
  for key in log.keys():
    if len(key) > longestName:
      longestName = len(key)
  
  print("Results:")
  for key, val in log.items():
    repoName = key + ": " + " " * (longestName - len(key))
    
    sys.stdout.write(repoName + val)
      

# Update and check out functions
# ----------------------------------------------------------------------------------------------
def updateSVN(localFolder, remoteFolder):
  retcode = ''
  retcode = subprocess.check_output(["svn", "update", localFolder]).decode("utf-8")
  return retcode
  
def checkoutSVN(localFolder, remoteFolder):
  retcode = ''
  retcode = subprocess.check_output(['svn', 'co', remoteFolder, localFolder]).decode("utf-8")
  return retcode
  
def updateGIT(localFolder, remoteFolder):
  remoteName = split(localFolder)[1]
  retcode = subprocess.check_output(['git', 'pull', '-s', 'subtree', remoteName, 'master']).decode("utf-8")
  return retcode
  
def reestablishGIT(localFolder, remoteFolder):
  localName = split(localFolder)[1]
  remoteName = split(localFolder)[1]
  
  retcode  = subprocess.check_output(['git', 'remote', 'add', '-f', localName, remoteFolder]).decode("utf-8")
  retcode += subprocess.check_output(['git', 'pull', '-s', 'subtree', remoteName, 'master']).decode("utf-8")
  return retcode
  
def checkoutGIT(localFolder, remoteFolder):
  localName = split(localFolder)[1]
  branchName = localName + "/master"
  
  retcode = subprocess.check_output(['git', 'remote', 'add', '-f', localName, remoteFolder]).decode("utf-8")
  retcode += subprocess.check_output(['git', 'merge', '-s', 'ours', '--no-commit', branchName]).decode("utf-8")
  retcode += subprocess.check_output(['git', 'read-tree', '--prefix=' + relpath(localFolder), '-u', branchName]).decode("utf-8")
  retcode += subprocess.check_output(['git', 'commit', '-m', "Merge " + branchName + " as part of our subdirectory"]).decode("utf-8")
  return retcode

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