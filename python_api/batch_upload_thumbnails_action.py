# :coding: utf-8
import logging
import os

import ftrack_api


class ImportThumbnailsAction(object):
    """Batch import thumbnails to a project."""

    label = "Batch Import Thumbnails"
    identifier = "ftrack.batch.import.thumbnails"
    description = "Batch import thumbnails from folder to project."

    priority = 100

    ui_label = (
        "The action will batch import thumbnails to the selected project.\n\n"
        "Specify a *folder path* to a folder containing the images.\n\n"
        "The images should be named to match the entity path in ftrack.\n\n"
        "For example:\n\n"
        "    0010.png\n"
        "    0010.010.png\n"
        "    0010.010.generic.png\n"
        "\n"
        "This will set the thumbnail for the *sequence*, *shot*"
        " and the *generic task*."
    )


    def __init__(self, session):
        super(ImportThumbnailsAction, self).__init__()
        self.session = session
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def register(self):
        discover_subscription = (
            "topic=ftrack.action.discover"
            " and source.user.username={}"
        ).format(
            self.session.api_user
        )
        self.session.event_hub.subscribe(
            discover_subscription,
            self.discover,
            priority=self.priority
        )

        launch_subscription = (
            "topic=ftrack.action.launch"
            " and data.actionIdentifier={}"
            " and source.user.username={}"
        ).format(
            self.identifier,
            self.session.api_user
        )
        self.session.event_hub.subscribe(
            launch_subscription,
            self.launch
        )

    def discover(self, event):
        if not self.validate_selection(event):
            return

        return {
            "items": [{
                "label": self.label,
                "description": self.description,
                "actionIdentifier": self.identifier
            }]
        }

    def launch(self, event):
        input_values = event["data"].get("values", {})
        #TODO: display error message when invalid input path
        if not self.validate_input(input_values):
            return {
                "items": [{
                    "type": "label",
                    "value": self.ui_label
                },
                {
                    "type": "text",
                    "label": "Folder path",
                    "name": "folder_path"
                }]
            }

        # Project entity
        project_id = event["data"]["selection"][0]["entityId"]
        project_entity = self.session.query(
            "Project where id is {}".format(project_id)
        ).one()
        project_name = project_entity["full_name"]
        self.logger.info("Project name: {}".format(project_name))

        # Files
        folder_path = input_values["folder_path"]
        files = self.get_files(folder_path, project_name)

        # Batch process
        try:
            self.upload_files_as_thumbnails(project_entity, files)
            self.session.commit()
        except Exception as exc:
            #TODO: filter exception type?
            self.logger.error("Error during process: {}".format(str(exc)))
            self.session.rollback()
            raise

        message = "Batch Import Thumbnails action completed successfully"
        self.logger.info(message)
        return {
            "success": True,
            "message": message
        }

    def upload_files_as_thumbnails(self, project, files):
        """Upload the files as thumbnails."""

        # Get project entity and all its children entities
        entities = {
            project["full_name"]: project
        }
        entities.update(
            self.get_child_elements_from_entity(self.session, project)
        )

        # Find matching entities
        filtered_entities = self.filter_entities(entities, files)

        self.session._configure_locations()
        server_location = self.session.query(
            "Location where name is \"ftrack.server\""
        ).one()

        for ftrack_path in filtered_entities:
            file = files[ftrack_path]
            entities = filtered_entities[ftrack_path]
            for entity in entities:
                self.logger.debug(
                    "Setting thumbnail '{}' for entity '{}'".format(file,
                                                                    entity)
                )
                thumbnail_component = self.session.create_component(
                    file,
                    dict(name="thumbnail"),
                    location=server_location
                )
                entity["thumbnail"] = thumbnail_component

    @staticmethod
    def validate_selection(event):
        """Return True if selection is valid.

        Selection is valid if consists of a single 'show' entity.
        """

        selection = event["data"].get("selection", None)
        if (
            not selection
            or len(selection) != 1
            or selection[0]["entityType"] != "show"
        ):
            return False

        return True

    @staticmethod
    def validate_input(input_values):
        """Validate the input parameters."""

        if not input_values:
            return False

        folder_path = input_values.get("folder_path", None)
        if not folder_path:
            return False

        if not os.path.isdir(folder_path):
            return False

        return True

    #TODO: add option to have full path (=> add project_name)
    # (also need to do it to entity paths)
    @staticmethod
    def get_files(folder_path, project_name):
        """Return a list of tuples with ftrack path and filepaths."""
        all_files = {}
        for filename in os.listdir(folder_path):
            absolute_file_path = os.path.join(folder_path, filename)
            if os.path.isfile(absolute_file_path):
                ftrack_path, _ = os.path.splitext(filename)
                all_files[ftrack_path] = absolute_file_path

        return all_files

    @staticmethod
    def filter_entities(entities, files):
        filtered_entities = {}
        for entity_path in entities:
            entity_path_lower = entity_path.lower()
            for ftrack_path in files:
                if entity_path_lower.endswith(ftrack_path.lower()):
                    # Stop at first match
                    break
            else:
                continue

            # Found a match
            if ftrack_path not in filtered_entities:
                filtered_entities[ftrack_path] = []
            filtered_entities[ftrack_path].append(entities[entity_path])

        return filtered_entities

    @classmethod
    def get_child_elements_from_entity(cls, session, entity):
        children = {}
        for child in entity["children"]:
            ancestors = []
            for ancestor in child["ancestors"]:
                ancestors.append(ancestor["name"])
            entity_path = ".".join(ancestors + [child["name"]])

            children[entity_path] = child
            if entity.entity_type.lower() != "task":
                children.update(
                    cls.get_child_elements_from_entity(
                        session, child
                    )
                )

        return children


def register(session, **kw):
    if not isinstance(session, ftrack_api.Session):
        return

    action = ImportThumbnailsAction(session)
    action.register()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    session = ftrack_api.Session()
    register(session)

    session.event_hub.connect()

    logging.info("Registered actions and listening for events."
                 " Use Ctrl-C to abort.")
    try:
        session.event_hub.wait()
    except KeyboardInterrupt:
        logging.info("Process terminated by Ctrl-C.")
