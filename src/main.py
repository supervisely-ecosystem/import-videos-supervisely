import supervisely as sly
from supervisely.app.widgets import SlyTqdm
from supervisely.io.fs import get_file_ext

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
    elif g.IMPORT_MODE in ["project", "dataset"]:
        project = api.project.get_info_by_id(id=g.PROJECT_ID)
        project_name = project.name

    datasets_names, datasets_videos_map = f.get_datasets_videos_map(dir_info)

    for dataset_name in datasets_names:
        if g.IMPORT_MODE != "dataset":
            dataset_info = api.dataset.create(
                project_id=project.id, name=dataset_name, change_name_if_conflict=True
            )
        else:
            dataset_info = api.dataset.get_info_by_name(parent_id=project.id, name=g.DATASET_NAME)

        videos_names = datasets_videos_map[dataset_name]["video_names"]
        videos_hashes = datasets_videos_map[dataset_name]["video_hashes"]
        videos_paths = datasets_videos_map[dataset_name]["video_paths"]

        for video_name, video_path, video_hash in progress_bar(
            zip(videos_names, videos_paths, videos_hashes),
            total=len(videos_hashes),
            message="Dataset: {!r}".format(dataset_info.name),
        ):
            try:
                video_info = f.convert_to_mp4(remote_video_path=video_path)
                video_name = video_info.name
                video_hash = video_info.hash
                if g.IS_ON_AGENT:
                    for remote_file_info in dir_info:
                        if remote_file_info["name"] != video_name:
                            continue
                        g.api.file.download(g.TEAM_ID, remote_file_info["path"], video_path)
                        g.api.video.upload_paths(
                            dataset_id=dataset_info.id,
                            names=[video_name],
                            paths=[video_path],
                        )
                        break
                else:
                    g.api.video.upload_hash(
                        dataset_id=dataset_info.id, name=video_name, hash=video_hash
                    )
            except Exception as ex:
                sly.logger.warn(ex)

    if g.REMOVE_SOURCE and not g.IS_ON_AGENT:
        api.file.remove(team_id=g.TEAM_ID, path=g.INPUT_PATH)
        source_dir_name = g.INPUT_PATH.lstrip("/").rstrip("/")
        sly.logger.info(msg=f"Source directory: '{source_dir_name}' was successfully removed.")

    api.task.set_output_project(task_id=task_id, project_id=project.id, project_name=project.name)


if __name__ == "__main__":
    sly.logger.info(
        "Script arguments",
        extra={
            "context.teamId": g.TEAM_ID,
            "context.workspaceId": g.WORKSPACE_ID,
            "modal.state.slyFolder": g.INPUT_PATH,
        },
    )

    import_videos(g.api, g.TASK_ID)
    try:
        sly.app.fastapi.shutdown()
    except KeyboardInterrupt:
        sly.logger.info("Application shutdown successfully")
