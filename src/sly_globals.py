import os
from distutils.util import strtobool

import supervisely as sly
from dotenv import load_dotenv
from supervisely.io.fs import mkdir
from supervisely.video.video import ALLOWED_VIDEO_EXTENSIONS

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

# region envvars
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()

task_id = sly.env.task_id(raise_not_found=False)
if sly.is_development():
    sly.logger.warning("Development mode: task_id set to 1...")
    task_id = 1

project_id = sly.env.project_id(raise_not_found=False)
dataset_id = sly.env.dataset_id(raise_not_found=False)
# endregion

sly.logger.info(
    f"Team ID: {team_id}, Workspace ID: {workspace_id}, "
    f"Project ID: {project_id}, Dataset ID: {dataset_id}."
)

api = sly.Api.from_env()

# region modalvars
if dataset_id is not None:
    IMPORT_MODE = "dataset"
elif project_id is not None:
    IMPORT_MODE = "project"
else:
    IMPORT_MODE = "new"
INPUT_FILES = os.environ.get("modal.state.files", None)
INPUT_FOLDER = sly.env.folder(raise_not_found=False)
INPUT_FILE = sly.env.file(raise_not_found=False)
sly.logger.info(
    f"App starting... INPUT_FILES: {INPUT_FILES}, INPUT_FOLDER: {INPUT_FOLDER}, INPUT_FILE: {INPUT_FILE}"
)


INPUT_PATH = INPUT_FILES or INPUT_FOLDER or INPUT_FILE
sly.logger.info(f"App starting... INPUT_PATH: {INPUT_PATH}")
CHECKED_INPUT_PATH = INPUT_PATH
if INPUT_PATH is None:
    raise RuntimeError("No input data. Please specify input files or folder.")

OUTPUT_PROJECT_NAME = os.environ.get("modal.state.projectName", "")
DEFAULT_DATASET_NAME = "ds0"

IS_ON_AGENT = api.file.is_on_agent(INPUT_PATH)
REMOVE_SOURCE = bool(strtobool(os.getenv("modal.state.removeSource", "False")))
# endregion

SUPPORTED_VIDEO_EXTS = ALLOWED_VIDEO_EXTENSIONS

base_video_extension = ".mp4"
accepted_video_codecs = ["h264", "h265", "avc", "hevc", "av1", "vp9"]
files_sizes = {}

STORAGE_DIR = os.path.join(os.getcwd(), "storage_dir")
mkdir(STORAGE_DIR, True)
