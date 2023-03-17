import os
import subprocess
from pathlib import Path

import supervisely as sly
from supervisely.io.fs import get_file_ext, get_file_name, get_file_name_with_ext

import sly_globals as g
import download_progress


def get_project_name_from_input_path(input_path: str) -> str:
    """Returns project name from target sly folder name."""
    return os.path.basename(input_path)


def convert_to_mp4(remote_video_path, video_size):
    # download from server
    video_name = get_file_name_with_ext(remote_video_path)
    local_video_path = os.path.join(g.STORAGE_DIR, video_name)

    progress_cb = download_progress.get_progress_cb(
        g.api, g.TASK_ID, f"Downloading {video_name}", video_size, is_size=True
    )
    if not g.IS_ON_AGENT:
        g.api.file.download(g.TEAM_ID, remote_video_path, local_video_path, progress_cb=progress_cb)
    else:
        g.api.file.download_from_agent(
            remote_path=remote_video_path, local_save_path=local_video_path, progress_cb=progress_cb
        )

    # convert
    convert_progress = sly.Progress(message=f"Converting {video_name}", total_cnt=1)
    output_video_name = f"{get_file_name(video_name)}{g.base_video_extension}"
    output_video_path = f"{local_video_path.split('.')[0]}_h264{g.base_video_extension}"

    # read video meta_data
    try:
        vid_meta = sly.video.get_info(local_video_path)
        need_video_transc, need_audio_transc = check_codecs(vid_meta)
    except:
        need_video_transc, need_audio_transc = True, True

    # convert videos
    convert(
        input_path=local_video_path,
        output_path=output_video_path,
        need_video_transc=need_video_transc,
        need_audio_transc=need_audio_transc,
    )
    convert_progress.iter_done_report()

    return output_video_name, output_video_path


def check_codecs(video_meta):
    need_video_transc, need_audio_transc = False, False
    for stream in video_meta["streams"]:
        codec_type = stream["codecType"]
        if codec_type not in ["video", "audio"]:
            continue
        codec_name = stream["codecName"]
        if codec_type == "video" and codec_name != "h264":
            need_video_transc = True
        elif codec_type == "audio" and codec_name != "aac":
            need_audio_transc = True
    return need_video_transc, need_audio_transc


def convert(input_path, output_path, need_video_transc, need_audio_transc):
    video_codec = "libx264" if need_video_transc else "copy"
    audio_codec = "aac" if need_audio_transc else "copy"
    subprocess.call(
        [
            "ffmpeg",
            "-y",
            "-i",
            f"{input_path}",
            "-c:v",
            f"{video_codec}",
            "-c:a",
            f"{audio_codec}",
            f"{output_path}",
        ]
    )


def get_datasets_videos_map(dir_info: list) -> tuple:
    """Creates a dictionary map based on api response from the target sly folder data."""
    datasets_images_map = {}
    for file_info in dir_info:
        full_path_file = file_info["path"]
        if g.IS_ON_AGENT:
            agent_id, full_path_file = g.api.file.parse_agent_id_and_path(full_path_file)
            full_path_file = f"agent://{agent_id}{full_path_file}"
        try:
            file_ext = get_file_ext(full_path_file)
            if file_ext.lower() not in g.SUPPORTED_VIDEO_EXTS:
                sly.image.validate_ext(full_path_file)
        except Exception as e:
            sly.logger.warn(
                "File skipped {!r}: error occurred during processing {!r}".format(
                    full_path_file, str(e)
                )
            )
            continue

        file_name = get_file_name_with_ext(full_path_file)
        file_size = file_info["meta"]["size"]

        try:
            ds_name = get_dataset_name(full_path_file.lstrip("/"))
        except:
            ds_name = "ds0"
        if ds_name not in datasets_images_map.keys():
            datasets_images_map[ds_name] = {
                "video_names": [],
                "video_paths": [],
                "video_sizes": [],
            }

        if file_name in datasets_images_map[ds_name]["video_names"]:
            temp_name = sly.fs.get_file_name(full_path_file)
            temp_ext = sly.fs.get_file_ext(full_path_file)
            new_file_name = f"{temp_name}_{sly.rand_str(5)}{temp_ext}"
            sly.logger.warn(
                "Name {!r} already exists in dataset {!r}: renamed to {!r}".format(
                    file_name, ds_name, new_file_name
                )
            )
            file_name = new_file_name

        datasets_images_map[ds_name]["video_names"].append(file_name)
        datasets_images_map[ds_name]["video_paths"].append(full_path_file)
        datasets_images_map[ds_name]["video_sizes"].append(file_size)

    datasets_names = list(datasets_images_map.keys())
    return datasets_names, datasets_images_map


def get_dataset_name(file_path: str, default: str = "ds0") -> str:
    """Dataset name from image path."""
    dir_path = os.path.split(file_path)[0]
    ds_name = default
    path_parts = Path(dir_path).parts
    if len(path_parts) != 1:
        if g.INPUT_PATH.startswith("/import/import-videos/"):
            ds_name = path_parts[3]
        else:
            ds_name = path_parts[-1]
    return ds_name
