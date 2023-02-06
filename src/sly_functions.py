import json
import shlex
import subprocess
from os import listdir, walk
from os.path import basename, isdir, isfile, join

import supervisely as sly
from supervisely.io.fs import get_file_ext, get_file_name, get_file_name_with_ext
from supervisely.video.video import ALLOWED_VIDEO_EXTENSIONS
from supervisely._utils import generate_free_name


def get_files(directory):
    dir_files = []
    for root, dirs, files in walk(directory):
        files = [join(root, file) for file in files]
        dir_files.extend(files)
    return dir_files


def get_ds_files_map(directory, default_ds_name="ds0"):
    ds_image_map = {
        default_ds_name: [
            join(directory, file) for file in listdir(directory) if isfile(join(directory, file))
        ]
    }
    ds_paths = [
        join(directory, subdir) for subdir in listdir(directory) if isdir(join(directory, subdir))
    ]
    for ds_path in ds_paths:
        ds_name = basename(ds_path)
        ds_files = get_files(ds_path)
        ds_image_map[ds_name] = ds_files
    return ds_image_map


def convert_to_mp4(file_name, file_path, used_ds_names):
    convert_progress = sly.Progress(message=f"Converting {file_name}", total_cnt=1)
    output_file_path = f"{file_path.split('.')[0]}_h264.mp4"
    output_file_name = get_file_name_with_ext(output_file_path)
    if output_file_name in used_ds_names:
        output_file_name = generate_free_name(
            used_names=used_ds_names, possible_name=output_file_name, with_ext=True
        )
    # read video meta data
    try:
        vid_meta = json.loads(
            subprocess.run(
                shlex.split(
                    f"ffprobe -loglevel error -show_format -show_streams -of json {file_path}"
                ),
                capture_output=True,
            ).stdout
        )

        need_video_transc, need_audio_transc = check_codecs(vid_meta)
    except:
        sly.logger.warn(
            msg=(
                f"Couldn't read meta of {file_name}, probably because of spaces in the video file name. "
                "Video will be converted to default audio (aac) and video (h264) codecs. "
                "You can safely ignore this warning."
            )
        )
        need_video_transc, need_audio_transc = True, True

    # convert videos
    convert(
        input_path=file_path,
        output_path=output_file_path,
        need_video_transc=need_video_transc,
        need_audio_transc=need_audio_transc,
    )

    convert_progress.iter_done_report()

    return output_file_name, output_file_path


def check_codecs(video_meta):
    need_video_transc = False
    need_audio_transc = False
    for stream in video_meta["streams"]:
        codec_type = stream["codec_type"]
        if codec_type not in ["video", "audio"]:
            continue
        codec_name = stream["codec_name"]
        if codec_type == "audio":
            if codec_name != "aac":
                need_audio_transc = True
        elif codec_type == "video":
            if codec_name != "h264":
                need_video_transc = True
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
