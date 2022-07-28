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


## Implementation

The new implemetation is provided as [batch_upload_thumbnails_action.py](python_api/batch_upload_thumbnails_action.py).

It is based on the "User Interface" example of the "[Actions](https://help.ftrack.com/en/articles/1040465-actions)" documentation page from the Ftrack Help website.

### Additional Changes

The main process had be modified due to some API changes.

Essentially, the ```getFromPath``` function has been removed from the Ftrack API.

Instead of getting the Ftrack entities from the image file names:
* Get all the children entities of the project
* For each entity check if its Ftrack path ends with any image file name

It allows image file names to be part of the Ftrack paths, instead of requiring the full path.
> E.g.: The name "char1.png" can be used, instead of the full path "assets.char.char1.png".

It also allows a thumbnail to be used by several entities.
> E.g.: An image "model.png" could be used for every task named "model" in the project.

### Alternative

A different implementation is provided as [batch_upload_thumbnails_baseaction.py](python_api/batch_upload_thumbnails_baseaction.py).

The process is identical, but the action is based on the "Base Action" class provided by the "[ftrack-action-handler](https://ftrack-action-handler.readthedocs.io)" module.
The module is mentionned in the "Action Base Class" section of the "[Actions](https://help.ftrack.com/en/articles/1040465-actions)" documentation page.

The class has its own [API reference page](http://ftrack-action-handler.rtd.ftrack.com/en/latest/api_reference/index.html?highlight=baseaction#baseaction).


To use this implementation, it is thus required to have the module available.

The module can be obtained in different ways:
* From a PIP installation:
    ```
    pip install git+https://bitbucket.org/ftrack/ftrack-action-handler.git
    ```
* From [PyPI](https://pypi.org/project/ftrack-action-handler/)
* From the [BitBucket source repository](https://bitbucket.org/ftrack/ftrack-action-handler/src/master/source/ftrack_action_handler)


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
