# Git-externals

Git-externals is designed to integrate SVN repositories in a git project. 

## The Problem
Working with git projects that depend on SVN repositories is a hassle. Yet, SVN repositories are more useful than git submodules for numerous reasons, such as being able to check out any subfolder in the repository.

## The solution
A script that makes it easy to add and use SVN repositories as a part of a git project. The script reads a "git externals" file and sets up SVN repositories appropriately. The repositories are then added to ".gitignore" in order not to get versioned by git.

The first time the script is run, the repositories will be checked out. Any subsequent run will update them to the latest revision.

### Example
Your project looks like this:
    ProjectDir/
      SomeFile.php
      libs/

In the empty **libs** folder, you add a **.gitexternals** file. The project now looks like this:
    ProjectDir/
      SomeFile.php
      libs/
        .gitexternals

Since you wish check out two repositories there, you specify their local names and URLs in the **.gitexternals** file. The contents of **.gitexternals** now look like this:
    symfony = http://svn.symfony-project.com/branches/1.4
    Zend    = http://framework.zend.com/svn/framework/standard/branches/release-1.10/library/Zend

Afterwards, you save the file and run:
    python3 git-externals.py

Your local project folder structure now looks like this:
    ProjectDir/
      SomeFile.php
      libs/
        .gitexternals
        .gitignore
        symfony/   (SVN-dir)
        Zend/      (SVN-dir)

However, when you commit and/or push, it looks like this:
    ProjectDir/
      SomeFile.php
      libs/
        .gitexternals
        .gitignore

This is because the SVN repositories are automatically added to **.gitignore**. 

When the git project is cloned, all the user has to do is to run **python3 git-externals.py** again to restore the project to a structure identical to your own.


## Usage
1. Create a file called _.gitexternals_ in the folder where you wish to check out your SVN repository.
		$ touch .gitexternals

2. In the file, add a name for the local folder, and the URL to the SVN repository.
		symfony = http://svn.symfony-project.com/branches/1.4
		Zend    = http://framework.zend.com/svn/framework/standard/branches/release-1.10/library/Zend

3. Repeat steps 1 and 2 for any folders in your project.
4. From the main project folder, run the script.
		$ python3 git-externals.py

### Updating specific repositories
Any subsequent execution of the script will update all repositories. If you wish to update only specific repositories, give their local folder names as parameters to the script.
		$ python3 git-externals.py symfony Zend

### Updating git and svn repos with one command
#### Unix/Linux/Mac OS X
Create a file with the following content:
    #!/bin/bash
    git pull
    python3 git-externals.py

Save it and name it "update" or something sensible like that. Now, make it executable:
    chmod u+x update

#### Windows 7 (PowerShell)
Create a file with the following content:
    git pull
    python3 git-externals.py

Save it and name it "update.ps1" or something sensible like that. Now, sign it or run the following command to enable all scripts (WARNING: read up on PowerShell security before doing this):
    Set-ExecutionPolicy Unrestricted

## Limitations
The SVN externals are treated as "read only" by the script. At this point, there's no support for commiting them.