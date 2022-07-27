# Ftrack Batch Thumbnails

## Description

Ftrack action to batch import thumbnails from a specified folder path to a selected project.

### Origin

The project is based on the existing snippet "[Action - Batch upload thumbnails (Legacy API)](https://bitbucket.org/ftrack/workspace/snippets/yK6p)" originally created by Carl Larsson.

For reference, the original script is provided in the "legacy" directory of this repository.

### Motivation

The latest code revision of the original project dates from December 2015.
It uses the Ftrack Legacy API.
As a consequence, it is also not compatible with Python 3.

The motivation for this project is to rewrite the script with the following main tasks:
* Change from the "Legacy API" to the newer "Ftrack Python API"
* Update usage of Python 2 to Python 3


## Additional Changes

**TODO:** Add changes.
* Doesn't need the full entity path in image file names
* ...


## Reference

From the original project page:

### Batch upload thumbnails action

This action will batch import thumbnails from a specified folder path to selected project.


#### Using the action

Navigate to a project in the web interface and select the project in the spreadsheet and select Actions from the context menu. Click on Batch import thumbnails.

Specify a folder path to a folder on your disk which contains images you want to use. The images should be named to match the entity path in ftrack.

For example:
```
0010.png
0010.010.png
0010.010.generic.png
```
This will set the thumbnail for the sequence, shot and the generic task.


#### Available on

* Project


#### Running the action

Start the listener from the terminal using the following command:
```
python batch_upload_thumbnails_action.py
```

If you wish to see debugging information, set the verbosity level by appending -v debug to the command.
