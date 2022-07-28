# Ftrack Batch Thumbnails

## Description

Ftrack action to batch import thumbnails from a specified folder path to a selected project.

### Origin

The project is based on the existing snippet "[Action - Batch upload thumbnails (Legacy API)](https://bitbucket.org/ftrack/workspace/snippets/yK6p)" originally created by Carl Larsson.

For reference, the original script is provided in the "legacy" directory of this repository.

### Motivation

The latest code revision of the original project dates from December 2015:
* Uses the "Ftrack Legacy API"
* Is not compatible with Python 3

The motivation for this project is to rewrite the script with the following main tasks:
* Change from the "Legacy API" to the newer "Ftrack Python API".
* Update code for Python 3 compatibility (while keeping Python 2 compatibility).


## Additional Changes

The main process had be modified due to some API changes.

Essentially, the ```getFromPath``` function has been removed from the Ftrack API.

Instead of getting the Ftrack entities from the image file names:
* Get all the children entities of the project
* For each entity check if its Ftrack path ends with any image file name

It allows image file names to be part of the Ftrack paths, instead of requiring the full path.

E.g.: The name "char1.png" can be used, instead of the full path "assets.char.char1.png".


It also allows a thumbnail to be used by several entities.

E.g.: An image "model.png" could be used for every task named "model" in the project.


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
