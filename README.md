# AtomTest Project - Project Spectra Private Preview 

## Confidentiality; Pre-Release Access  

Welcome to the Project Spectra Private Preview.  This is a confidential pre-release project; your use is subject to the nondisclosure agreement between you (or your organization) and Amazon.  Do not disclose the existence of this project, your participation in it, or any of the  materials provided, to any unauthorized third party.  To request access for a third party, please contact [Royal O'Brien, obriroya@amazon.com](mailto:obriroya@amazon.com).

## Download and Install

This repository uses Git LFS for storing large binary files.  You will need to create a Github personal access token to authenticate with the LFS service.


### Create a Git Personal Access Token

You will need your personal access token credentials to authenticate when you clone the repository.

[Create a personal access token with the 'repo' scope.](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)


### (Recommended) Verify you have a credential manager installed to store your credentials 

Recent versions of Git install a credential manager to store your credentials so you don't have to put in the credentials for every request.  
It is highly recommended you check that you have a [credential manager installed and configured](https://github.com/microsoft/Git-Credential-Manager-Core)



### Clone the repository 

There are two options when installing a project

#### Option #1 (Recommended) - Clone into a folder outside the engine

This option lets you keep engine and project files in separate locations.

```shell
# clone the project into a folder outside your engine repository folder
> git clone https://github.com/aws/o3de-atomtest.git
Cloning into 'o3de-atomtest'...

# register the engine
> c:/path/to/o3de/scripts/o3de register --this-engine

# register the o3de-atomtest project 
> c:/path/to/o3de/scripts/o3de register -p c:/path/to/o3de-atomtest

# use the full path to your project for LY_PROJECTS in the configure step

# example configure command
> cmake c:/path/to/o3de -b c:/path/to/o3de-atomtest/build -G "Studio 16 2019" -A x64 -T host=x64 -DLY_3RDPARTY_PATH="c:/3rdparty" -DLY_PROJECTS="c:/path/to/o3de-atomtest" 

# example build command
> cmake --build c:/path/to/o3de-atomtest/build --target Editor;AtomTest.GameLauncher --configure profile -- /m /nologo 
```

#### Option #2 - Clone into a folder in the engine folder 

This option models the legacy folder layout where all projects were in the same folder as the engine.
If you use this approach you must also modify your engine's local git exclude file to ignore the project folder.

```shell
# clone the project in a folder named 'AtomTest' in your existing engine repository folder
> git clone https://github.com/aws/o3de-atomtest.git c:/path/to/engine/AtomTest
Cloning into 'AtomTest'...

# modify the local engine git exclude file to ignore the project folder
> echo AtomTest > c:/path/to/engine/.git/info/exclude

# the project now exists inside the engine folder but your engine repository will ignore all files in the project folder

# example configure command
> cmake c:/path/to/o3de -b c:/path/to/o3de/build -G "Studio 16 2019" -A x64 -T host=x64 -DLY_3RDPARTY_PATH="c:/3rdparty" -DLY_PROJECTS=AtomTest 

# example build command
> cmake --build c:/path/to/o3de/build --target Editor;AtomTest.GameLauncher --configure profile -- /m /nologo 

```

If you have a Git credential helper configured, you should not be prompted for your credentials anymore.


## License

For terms please see the LICENSE*.TXT file at the root of this distribution.


