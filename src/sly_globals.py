import os
import sys
from distutils.util import strtobool

import supervisely as sly
from fastapi import FastAPI
from supervisely.app.fastapi import create
from supervisely.video.video import ALLOWED_VIDEO_EXTENSIONS
from supervisely.io.fs import mkdir

app_root_directory = os.path.dirname(os.getcwd())
sys.path.append(app_root_directory)
sys.path.append(os.path.join(app_root_directory, "src"))
print(f"App root directory: {app_root_directory}")
sly.logger.info(f'PYTHONPATH={os.environ.get("PYTHONPATH", "")}')

# order matters
from dotenv import load_dotenv
load_dotenv(os.path.join(app_root_directory, "secret_debug.env"))
load_dotenv(os.path.join(app_root_directory, "debug.env"))

app = FastAPI()

sly_app = create()

api = sly.Api.from_env()

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])
INPUT_PATH = os.environ.get("modal.state.slyFolder", None)
OUTPUT_PROJECT_NAME = os.environ.get("modal.state.project_name", "")

IS_ON_AGENT = api.file.is_on_agent(INPUT_PATH)
REMOVE_SOURCE = bool(strtobool(os.getenv("modal.state.remove_source")))

DEFAULT_DATASET_NAME = "ds0"
SUPPORTED_VIDEO_EXTS = ALLOWED_VIDEO_EXTENSIONS

base_video_extension = '.mp4'


STORAGE_DIR = os.path.join(app_root_directory, "debug", "data", "storage_dir")
mkdir(STORAGE_DIR, True)
