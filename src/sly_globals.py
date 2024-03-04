import os
from distutils.util import strtobool

import supervisely as sly
from dotenv import load_dotenv
from fastapi import FastAPI
from supervisely.app.fastapi import create
from supervisely.io.fs import mkdir
from supervisely.video.video import ALLOWED_VIDEO_EXTENSIONS

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

api = sly.Api.from_env()

TASK_ID = sly.env.task_id()
TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()

PROJECT_ID = sly.env.project_id(raise_not_found=False)
DATASET_ID = sly.env.dataset_id(raise_not_found=False)

if DATASET_ID is not None:
    IMPORT_MODE = "dataset"
elif PROJECT_ID is not None:
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

SUPPORTED_VIDEO_EXTS = ALLOWED_VIDEO_EXTENSIONS

base_video_extension = ".mp4"
files_sizes = {}

STORAGE_DIR = os.path.join(sly.app.get_data_dir(), "storage_dir")
mkdir(STORAGE_DIR, True)
