import supervisely as sly
from supervisely.app.widgets import SlyTqdm

import sly_functions as f
import sly_globals as g
import workflow as w

progress_bar = SlyTqdm()


def import_videos(api: sly.Api):
    dir_info = api.file.list(g.team_id, g.INPUT_PATH)
    if len(dir_info) == 0:
        raise Exception(f"There are no files in selected directory: {g.INPUT_PATH}")

    sly.logger.info(f"Number of files in selected directory: {len(dir_info)}")

    datasets_names, datasets_videos_map = f.get_datasets_videos_map(dir_info)

    # Count what we plan to import vs what is actually uploaded, so the source is only
    # removed from Team Files when every video made it into the project.
    planned_cnt = sum(len(m["video_names"]) for m in datasets_videos_map.values())
    uploaded_cnt = 0

    if planned_cnt == 0:
        # Nothing importable: fail before creating a project, so no empty project is left
        # behind. The source is kept as is.
        supported = ", ".join(dict.fromkeys(ext.lower() for ext in g.SUPPORTED_VIDEO_EXTS))
        raise RuntimeError(
            f"No supported videos found in '{g.INPUT_PATH}' "
            f"({len(g.SKIPPED_FILES)} files skipped as unsupported). "
            f"Supported extensions: {supported}. "
            "Nothing was imported, no project was created and the source in Team Files was kept."
        )

    project = None
    project_created = False
    if g.IMPORT_MODE in ["project", "dataset"] and g.project_id is None:
        project_name = (
            f.get_project_name_from_input_path(g.INPUT_PATH)
            if len(g.OUTPUT_PROJECT_NAME) == 0
            else g.OUTPUT_PROJECT_NAME
        )
        sly.logger.warning("Existing project wasn`t selected. Creating new project...")
        project = api.project.create(
            workspace_id=g.workspace_id,
            name=project_name,
            change_name_if_conflict=True,
            type=sly.ProjectType.VIDEOS,
        )
        project_created = True
        sly.logger.info(
            f'New project has been created - "{project.name}" (ID: {project.id})'
        )
        
    elif g.IMPORT_MODE in ["project", "dataset"]:
        project = api.project.get_info_by_id(id=g.project_id)
        if project is None:
            sly.logger.warning("Existing project not found. Creating new project...")
    if g.IMPORT_MODE == "new" or project is None:
        project_name = (
            f.get_project_name_from_input_path(g.INPUT_PATH)
            if len(g.OUTPUT_PROJECT_NAME) == 0
            else g.OUTPUT_PROJECT_NAME
        )
        project = api.project.create(
            workspace_id=g.workspace_id,
            name=project_name,
            change_name_if_conflict=True,
            type=sly.ProjectType.VIDEOS,
        )
        project_created = True
        sly.logger.info(
            f'New project has been created - "{project.name}" (ID: {project.id})'
        )
    project_name = project.name

    for dataset_name in datasets_names:
        dataset_info = None
        if g.IMPORT_MODE == "dataset" and g.dataset_id is not None:
            dataset_info = api.dataset.get_info_by_id(g.dataset_id)
        if dataset_info is None:
            dataset_info = api.dataset.create(
                project_id=project.id, name=dataset_name, change_name_if_conflict=True
            )
            sly.logger.info(f'New dataset "{dataset_info.name}" has been created.')

        videos_names = datasets_videos_map[dataset_name]["video_names"]
        videos_paths = datasets_videos_map[dataset_name]["video_paths"]
        videos_sizes = datasets_videos_map[dataset_name]["video_sizes"]

        result_video_paths = []
        result_video_names = []

        convert_progress = sly.Progress(
            message="Converting videos", total_cnt=len(videos_names)
        )
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

            uploaded = g.api.video.upload_paths(
                dataset_id=dataset_info.id,
                names=batch_video_names,
                paths=batch_video_paths,
                progress_cb=lambda m: _print_progress(m, upload_progress),
            )
            # upload_paths logs "File skipped ..." and drops videos the server rejects;
            # a video with several streams returns several infos with the same name.
            uploaded_cnt += min(
                len(batch_video_names), len({info.name for info in uploaded})
            )

    failed_cnt = planned_cnt - uploaded_cnt
    skipped_cnt = len(g.SKIPPED_FILES)
    sly.logger.info(
        f"Import summary: {uploaded_cnt} of {planned_cnt} videos imported, "
        f"{failed_cnt} failed, {skipped_cnt} files skipped as unsupported."
    )
    import_complete = planned_cnt > 0 and failed_cnt == 0 and skipped_cnt == 0

    source_kept = False
    if g.REMOVE_SOURCE and not g.IS_ON_AGENT:
        source_dir_name = g.INPUT_PATH.lstrip("/").rstrip("/")
        if import_complete:
            api.file.remove(team_id=g.team_id, path=g.INPUT_PATH)
            sly.logger.info(
                msg=f"Source directory: '{source_dir_name}' was successfully removed."
            )
        else:
            source_kept = True
            reasons = []
            if failed_cnt > 0:
                reasons.append(f"{failed_cnt} of {planned_cnt} videos failed to import")
            if skipped_cnt > 0:
                reasons.append(f"{skipped_cnt} files were skipped as unsupported")
            if planned_cnt == 0:
                reasons.append("no videos were found to import")
            sly.logger.warning(
                f"Source directory: '{source_dir_name}' was NOT removed from Team Files "
                f"because the import was not complete ({'; '.join(reasons)}). "
                "Check the warnings above; the source is kept so no data is lost.",
                extra={"skipped_files": g.SKIPPED_FILES[:100]},
            )

    # Nothing made it into a project this run created: remove it rather than leave an
    # empty project behind (only if the server confirms it is still empty).
    project_removed = (
        uploaded_cnt == 0 and project_created and f.remove_project_if_empty(api, project)
    )

    if not project_removed:
        api.task.set_output_project(
            task_id=g.task_id, project_id=project.id, project_name=project.name
        )
        w.workflow_output(api, project.id)

    if failed_cnt > 0:
        # Do not report success when videos were lost on the way; what was imported
        # stays in the project.
        msg = f"{failed_cnt} of {planned_cnt} videos failed to import (see warnings above)."
        if project_removed:
            msg += (
                f" Nothing was imported, so the empty project '{project.name}' "
                "created by this run was removed."
            )
        else:
            msg += (
                f" {uploaded_cnt} videos were imported into project '{project.name}' "
                f"(id: {project.id})."
            )
        if source_kept:
            msg += " The source in Team Files was kept."
        raise RuntimeError(msg)

if __name__ == "__main__":
    import_videos(g.api)
