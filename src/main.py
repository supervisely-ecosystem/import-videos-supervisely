from os.path import basename, expanduser

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.widgets import SlyTqdm
from supervisely.io.fs import get_file_name_with_ext, remove_dir

from sly_functions import convert_to_mp4, get_ds_files_map

progress_bar = SlyTqdm()
DEFAULT_DATASET_NAME = "ds0"


# load ENV variables for debug, has no effect in production
if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(expanduser("~/supervisely.env"))


class MyImport(sly.app.Import):
    def process(self, context: sly.app.Import.Context):
        api = sly.Api.from_env()

        if context.project_id is None:
            project_name = basename(context.path)
            project = api.project.create(
                workspace_id=context.workspace_id,
                name=project_name,
                change_name_if_conflict=True,
                type=sly.ProjectType.VIDEOS,
            )
        else:
            project = api.project.get_info_by_id(id=context.project_id)
            project_name = project.name

        ds_files_map = get_ds_files_map(context.path, DEFAULT_DATASET_NAME)
        for ds_name in ds_files_map:
            if context.dataset_id is None:
                dataset_info = api.dataset.create(
                    project_id=project.id, name=ds_name, change_name_if_conflict=True
                )
            else:
                dataset_info = api.dataset.get_info_by_id(id=context.dataset_id)

            files_names = [get_file_name_with_ext(file_path) for file_path in ds_files_map[ds_name]]
            files_paths = list(ds_files_map[ds_name])
            used_ds_names = []

            for file_name, file_path in progress_bar(
                zip(files_names, files_paths),
                total=len(files_paths),
                message="Dataset: {!r}".format(dataset_info.name),
            ):
                try:
                    file_name, file_path = convert_to_mp4(file_name, file_path, used_ds_names)
                    used_ds_names.append(file_name)

                    api.video.upload_path(
                        dataset_id=dataset_info.id,
                        name=file_name,
                        path=file_path,
                    )
                except Exception as ex:
                    sly.logger.warn(ex)

        remove_dir(context.path)
        return context.project_id


app = MyImport()
app.run()
