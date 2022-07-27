import logging
import os

import ftrack_api


class ImportThumbnailsAction(object):
    """Batch import thumbnails to a project."""

    label = "Batch Import Thumbnails"
    identifier = "ftrack.batch.import.thumbnails"
    description = "TODO..."

    priority = 100

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
        """Return action config if triggered on a show entity."""
        data = event["data"]

        # If selection contains more than one item return early since
        # this action can only handle a single version.
        selection = data.get("selection", [])
        self.logger.info("Selection: {}".format(selection))
        if (
            len(selection) != 1
            or selection[0]["entityType"] != "show"
        ):
            return

        return {
            "items": [{
                "label": self.label,
                "description": self.description,
                "actionIdentifier": self.identifier
            }]
        }

    def launch(self, event):
        project_id = event["data"]["selection"][0]["entityId"]
        project_entity = self.session.query(
            "Project where id is {}".format(project_id)
        ).one()
        project_name = project_entity["full_name"]
        self.logger.info("Project name: {}".format(project_name))

        try:
            input_values = event["data"]["values"]
        except KeyError:
            input_values = None
        print("input_values: {}".format(input_values))

        #TODO: display error message when invalid input path
        if not self.validate_input(input_values):
            return {
                "items": [{
                    "type": "label",
                    "value": (
                        "The action will batch import thumbnails to"
                        " the selected project.\n\n"
                        "Specify a *folder path* to a folder"
                        " containing the images to use.\n\n"
                        "The images should be named to match the entity"
                        " path in ftrack.\n\n"
                        "For example:\n\n"
                        "    0010.png\n"
                        "    0010.010.png\n"
                        "    0010.010.generic.png\n"
                        "\n"
                        "This will set the thumbnail for the *sequence*,"
                        " *shot* and the *generic task*."
                    )
                },
                {
                    "type": "text",
                    "label": "Folder path",
                    "name": "folder_path"
                }]
            }


        files = self.get_files(input_values['folder_path'], project_name)
        #self.logger.debug("files: {}".format(files))

        self.upload_files_as_thumbnails(project_entity, files)


        return {
            "success": True,
            "message": "Batch Import Thumbnails action completed successfull"
        }


    '''
    def get_child_elements_from_entity(self, session, entity, children=[]):

        if entity.entity_type.lower() == "project" or entity.entity_type.lower() == "folder":
            if entity.entity_type.lower() == "project":
                children.append(entity)
            for child in entity['children']:
                self.get_child_elements_from_entity(
                    session, child, children
                )

        if entity.entity_type.lower() == "shot" or entity.entity_type.lower() == "assetbuild":

            query = "AssetVersion where asset.parent.id is '{0}'".format(
                entity["id"]
            )
            children.append(entity)
            for assetversion in session.query(query):
                self.get_child_elements_from_entity(
                    session, assetversion, children
                )

        return children
    '''
    '''
    def get_child_elements_from_entity(self, session, entity, children={}):
        for child in entity["children"]:
            ancestors = []
            for ancestor in child["ancestors"]:
                ancestors.append(ancestor["name"])
            entity_path = ".".join(ancestors + [child["name"]])
            #print("PATH: {}".format(entity_path))

            children[entity_path] = child
            if entity.entity_type.lower() != "task":
                self.get_child_elements_from_entity(
                    session, child, children
                )

        return children
    '''
    @classmethod
    def get_child_elements_from_entity(cls, session, entity):
        children = {}
        for child in entity["children"]:
            ancestors = []
            for ancestor in child["ancestors"]:
                ancestors.append(ancestor["name"])
            entity_path = ".".join(ancestors + [child["name"]])
            #print("PATH: {}".format(entity_path))

            children[entity_path] = child
            if entity.entity_type.lower() != "task":
                children.update(
                    cls.get_child_elements_from_entity(
                        session, child
                    )
                )

        return children



    @staticmethod
    def validate_input(input_values):
        """Validate the input parameters."""

        if not input_values:
            return False

        try:
            folder_path = input_values["folder_path"]
        except:
            folder_path = None

        if not folder_path:
            return False

        if not os.path.isdir(folder_path):
            return False

        return True

    #TODO: add option to have full path (=> add project_name)
    # (also need to do it to entity paths)
    '''
    def get_files(self, folder_path, project_name):
        """Return a list of tuples with ftrack path and filepaths."""
        all_files = []
        for filename in os.listdir(folder_path):
            absolute_file_path = os.path.join(folder_path, filename)
            if os.path.isfile(absolute_file_path):
                ftrack_path, _ = os.path.splitext(filename)
                all_files.append(
                    (
                        #'{}.{}'.format(project_name, ftrack_path),
                        ftrack_path,
                        absolute_file_path
                    )
                )

        return all_files
    '''
    def get_files(self, folder_path, project_name):
        """Return a list of tuples with ftrack path and filepaths."""
        all_files = {}
        for filename in os.listdir(folder_path):
            absolute_file_path = os.path.join(folder_path, filename)
            if os.path.isfile(absolute_file_path):
                ftrack_path, _ = os.path.splitext(filename)
                all_files[ftrack_path] = absolute_file_path

        return all_files


    '''
    def upload_files_as_thumbnails(self, files):
        """Upload the files as thumbnails."""
        job = ftrack.createJob(
            "Creating thumbnails.", "running"
        )

        try:
            for ftrack_path, file_path in files:
                try:
                    entity = ftrack.getFromPath(ftrack_path)
                except ftrack.FTrackError:
                    print('Could not find entity with path "{}"'.format(
                        ftrack_path
                    ))
                    continue

                entity.createThumbnail(file_path)
        except Exception:
            # Except anything and fail the job.
            job.setStatus('failed')
            job.setDescription('Creating thumbnails failed.')

        job.setStatus('done')
        job.setDescription('Creating thumbnails done.')
    '''
    def upload_files_as_thumbnails(self, project, files):
        """Upload the files as thumbnails.

        TODO: REPHRASE!!!!
        "getFromPath" being removed from the API,
        Instead of getting the path from the image file names,
        get all entities, and for each check if the image file names are contained in the path

        + only checking end of path, so file names dont need full paths of entities (and can be shared in 1+ entities)

        (+ could propagate (optional) thumbnails to children if don't have any (at end of process))
            ? => done automatically

        mention sources:
        * original project
        * ftrack api doc (+baseaction package for other version - TODO!)
        * ftrack doc:
            ftrack-python-api\doc\example\thumbnail.rst

        ? use ordered dict for children?

        """

        # Add project entity
        entities = {
            project["full_name"]: project
        }
        entities.update(
            self.get_child_elements_from_entity(self.session, project)
        )
        #print("entities: {}".format(entities))

        ########
        #TODO: make separate function
        found_entities = {}
        for entity_path in entities:
            #for ftrack_path, _ in files:
            for ftrack_path in files:
                if entity_path.endswith(ftrack_path):
                    # stop at first image match
                    break
            else:
                continue

            # found an image
            print("found match: '{}' - '{}'".format(entity_path, ftrack_path))
            '''
            entities.pop(entity_path)
            '''
            if ftrack_path not in found_entities:
                found_entities[ftrack_path] = []
            found_entities[ftrack_path].append(entities[entity_path])
        print("found_entities: {}".format(found_entities))
        ########


        self.session._configure_locations()
        server_location = self.session.query(
            "Location where name is \"ftrack.server\""
        ).one()

        try:
            for ftrack_path in found_entities:
                file = files[ftrack_path]
                print("file: {}".format(file))

                entities = found_entities[ftrack_path]
                for entity in entities:
                    print("entity: {}".format(entity))



                thumbnail_component = self.session.create_component(
                    file,
                    dict(name="thumbnail"),
                    location=server_location
                )
                entity["thumbnail"] = thumbnail_component

            #TODO: after or in loop?
            self.session.commit()

        except Exception as exc:
            #TODO: filter exception type
            print("exception {}".format(exc))

            #TODO: rollback?


        return


def register(session, **kw):
    '''Register plugin.'''
    if not isinstance(session, ftrack_api.Session):
        return

    action = ImportThumbnailsAction(session)
    action.register()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    session = ftrack_api.Session()
    register(session)

    session.event_hub.connect()

    session.event_hub.wait()