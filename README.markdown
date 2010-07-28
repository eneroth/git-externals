# Git-externals

Git-externals is designed to integrate SVN repositories in a git project. 

## The Problem
Working with git projects that depend on SVN repositories is a hassle. Yet, SVN repositories are better than git submodules for numerous reasons, such as being able to check out any subfolder in the repository.

## The solution
A script that makes it easy to add SVN repositories as a part of a git project. The script reads a "git externals" file and sets up SVN repositories appropriately. The repositories are then added to ".gitignore" in order not to get versioned by git.

The first time the script is run, the repositories will be checked out. Any subsequent run will update them to the latest revision.

## Usage
1. Create a file called *.gitexternals* in the folder where you wish to check out your SVN repository.
		$ touch .gitexternals
  
2. In the file, add a name for the local folder, and the URL to the SVN repository.
		symfony = http://svn.symfony-project.com/branches/1.4
		Zend    = http://framework.zend.com/svn/framework/standard/branches/release-1.10/library/Zend
  
3. Repeat step 2 for any folders in your project.
4. From the main project folder, run the script.
		$ python3 git-externals.py

### Updating specific repositories
Any subsequent execution of the script will update all repositories. If you wish to update only specific repositories, give their local folder names as parameters to the script.
		$ python3 git-externals.py symfony Zend