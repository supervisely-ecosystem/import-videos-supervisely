import supervisely as sly
from supervisely.app.widgets import SlyTqdm
from supervisely.io.fs import get_file_name

import sly_functions as f
import sly_globals as g

progress_bar = SlyTqdm()


@sly.timeit
def import_videos(api: sly.Api, task_id: int):
    dir_info = api.file.list(g.TEAM_ID, g.INPUT_PATH)
    if len(dir_info) == 0:
        raise Exception(f"There are no files in selected directory: '{g.INPUT_PATH}'")

    if g.IMPORT_MODE == "new":
        project_name = (
            f.get_project_name_from_input_path(g.INPUT_PATH)
            if len(g.OUTPUT_PROJECT_NAME) == 0
            else g.OUTPUT_PROJECT_NAME
        )
        project = api.project.create(
            workspace_id=g.WORKSPACE_ID,
            name=project_name,
            change_name_if_conflict=True,
            type=sly.ProjectType.VIDEOS,
        )
    if g.IMPORT_MODE in ["project", "dataset"] and g.PROJECT_ID is None:
        project_name = f.get_project_name_from_input_path(g.INPUT_PATH)
        sly.logger.warning("Existing project wasn`t selected. Creating new project...")
        project = api.project.create(
            workspace_id=g.WORKSPACE_ID,
            name=project_name,
            change_name_if_conflict=True,
            type=sly.ProjectType.VIDEOS,
        )
        project_name = project.name
        sly.logger.info(f'New project has been created - "{project_name}" (ID: {project.id})')
    elif g.IMPORT_MODE in ["project", "dataset"]:
        project = api.project.get_info_by_id(id=g.PROJECT_ID)
        project_name = project.name

    datasets_names, datasets_videos_map = f.get_datasets_videos_map(dir_info)

    for dataset_name in datasets_names:
        if g.IMPORT_MODE != "dataset" or g.DATASET_NAME is None:
            dataset_info = api.dataset.create(
                project_id=project.id, name=dataset_name, change_name_if_conflict=True
            )
            sly.logger.info(f'New dataset "{dataset_name}" has been created.')
        else:
            dataset_info = api.dataset.get_info_by_name(parent_id=project.id, name=g.DATASET_NAME)

        videos_names = datasets_videos_map[dataset_name]["video_names"]
        videos_paths = datasets_videos_map[dataset_name]["video_paths"]
        videos_sizes = datasets_videos_map[dataset_name]["video_sizes"]

        result_video_paths = []
        result_video_names = []

        convert_progress = sly.Progress(message="Converting videos", total_cnt=len(videos_names))
        for video_name, video_path, video_size in progress_bar(
            zip(videos_names, videos_paths, videos_sizes),
            total=len(videos_paths),
            message="Dataset: {!r}".format(dataset_info.name),
        ):
            try:
                video_name, video_path = f.convert_to_mp4(
                    remote_video_path=video_path, video_size=video_size
                )
                result_video_paths.append(video_path)
                result_video_names.append(video_name)

            except Exception as ex:
                sly.logger.warn(ex)
            convert_progress.iter_done_report()

        for batch_video_paths, batch_video_names in zip(
            sly.batched(result_video_paths), sly.batched(result_video_names)
        ):

            upload_progress = []

            def _print_progress(monitor, upload_progress):
                if len(upload_progress) == 0:
                    upload_progress.append(
                        sly.Progress(
                            message="Upload {!r}".format(video_name),
                            total_cnt=monitor,
                            ext_logger=sly.logger,
                            is_size=True,
                        )
                    )
                upload_progress[0].set_current_value(monitor)

            g.api.video.upload_paths(
                dataset_id=dataset_info.id,
                names=batch_video_names,
                paths=batch_video_paths,
                progress_cb=lambda m: _print_progress(m, upload_progress),
            )

    if g.REMOVE_SOURCE and not g.IS_ON_AGENT:
        api.file.remove(team_id=g.TEAM_ID, path=g.INPUT_PATH)
        source_dir_name = g.INPUT_PATH.lstrip("/").rstrip("/")
        sly.logger.info(msg=f"Source directory: '{source_dir_name}' was successfully removed.")

    api.task.set_output_project(task_id=task_id, project_id=project.id, project_name=project.name)


@sly.handle_exceptions
def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "context.teamId": g.TEAM_ID,
            "context.workspaceId": g.WORKSPACE_ID,
            "modal.state.slyFolder": g.INPUT_PATH,
        },
    )
    import_videos(g.api, g.TASK_ID)

if __name__ == "__main__":
    sly.main_wrapper("main", main)