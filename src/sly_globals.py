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
PROJECT_ID = sly.env.project_id(False)

OUTPUT_PROJECT_NAME = os.environ.get("modal.state.projectName", "")

IMPORT_MODE = os.environ["modal.state.importMode"]
if IMPORT_MODE == "dataset":
    DATASET_NAME = os.environ["modal.state.datasets"]

INPUT_PATH = os.environ.get("modal.state.slyFolder", None)
IS_ON_AGENT = api.file.is_on_agent(INPUT_PATH)
REMOVE_SOURCE = bool(strtobool(os.getenv("modal.state.removeSource")))

SUPPORTED_VIDEO_EXTS = ALLOWED_VIDEO_EXTENSIONS

base_video_extension = ".mp4"
files_sizes = {}

STORAGE_DIR = os.path.join(sly.app.get_data_dir(), "storage_dir")
mkdir(STORAGE_DIR, True)
