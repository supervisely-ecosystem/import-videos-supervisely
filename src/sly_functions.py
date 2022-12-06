import os
from pathlib import Path

import supervisely as sly
from moviepy.editor import VideoFileClip
from supervisely.io.fs import get_file_ext, get_file_name_with_ext, get_file_name

import sly_globals as g


def get_project_name_from_input_path(input_path: str) -> str:
    """Returns project name from target sly folder name."""
    full_path_dir = os.path.dirname(input_path)
    return os.path.basename(full_path_dir)


def download_project(api: sly.Api, input_path):
    """Download target directory from Team Files"""
    remote_proj_dir = input_path
    if api.file.is_on_agent(input_path):
        agent_id, path_on_agent = api.file.parse_agent_id_and_path(input_path)
        local_save_dir = f"{g.STORAGE_DIR}{path_on_agent}/"
    else:
        local_save_dir = f"{g.STORAGE_DIR}{remote_proj_dir}/"
    local_save_dir = local_save_dir.replace("//", "/")
    api.file.download_directory(
        g.TEAM_ID, remote_path=remote_proj_dir, local_save_path=local_save_dir
    )
    return local_save_dir


def convert_to_mp4(remote_video_path):
    # download from server
    video_name = get_file_name_with_ext(remote_video_path)
    local_video_path = os.path.join(g.STORAGE_DIR, video_name)
    g.api.file.download(g.TEAM_ID, remote_video_path, local_video_path)

    # convert
    clip = VideoFileClip(local_video_path)
    local_video_path = local_video_path.split(".")[0] + g.base_video_extension
    remote_video_path = os.path.join(
        os.path.dirname(remote_video_path),
        f"{get_file_name(remote_video_path)}{g.base_video_extension}",
    )
    clip.write_videofile(local_video_path)

    # upload && return info
    return g.api.file.upload(g.TEAM_ID, local_video_path, remote_video_path)


def get_datasets_videos_map(dir_info: list) -> tuple:
    """Creates a dictionary map based on api response from the target sly folder data."""
    datasets_images_map = {}
    for file_info in dir_info:
        full_path_file = file_info["path"]
        if g.IS_ON_AGENT:
            agent_id, full_path_file = g.api.file.parse_agent_id_and_path(
                full_path_file
            )
        try:
            file_ext = get_file_ext(full_path_file)
            if file_ext not in g.SUPPORTED_VIDEO_EXTS:
                sly.image.validate_ext(full_path_file)
        except Exception as e:
            sly.logger.warn(
                "File skipped {!r}: error occurred during processing {!r}".format(
                    full_path_file, str(e)
                )
            )
            continue

        file_name = get_file_name_with_ext(full_path_file)
        file_hash = file_info["hash"]
        ds_name = get_dataset_name(full_path_file.lstrip("/"))
        if ds_name not in datasets_images_map.keys():
            datasets_images_map[ds_name] = {
                "video_names": [],
                "video_paths": [],
                "video_hashes": [],
            }

        if file_name in datasets_images_map[ds_name]["video_names"]:
            temp_name = sly.fs.get_file_name(full_path_file)
            temp_ext = sly.fs.get_file_ext(full_path_file)
            new_file_name = f"{temp_name}_{sly.rand_str(5)}{temp_ext}"
            sly.logger.warning(
                "Name {!r} already exists in dataset {!r}: renamed to {!r}".format(
                    file_name, ds_name, new_file_name
                )
            )
            file_name = new_file_name

        datasets_images_map[ds_name]["video_names"].append(file_name)
        datasets_images_map[ds_name]["video_paths"].append(full_path_file)
        datasets_images_map[ds_name]["video_hashes"].append(file_hash)

    datasets_names = list(datasets_images_map.keys())
    return datasets_names, datasets_images_map


def get_dataset_name(file_path, default="ds0"):
    dir_path = os.path.split(file_path)[0]
    ds_name = default
    path_parts = Path(dir_path).parts
    if len(path_parts) != 1:
        if g.IS_ON_AGENT:
            return path_parts[-1]
        ds_name = path_parts[1]
    return ds_name
