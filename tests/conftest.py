"""Offline test harness: runs src/main.py against a small in-memory fake of sly.Api.

No Supervisely server is contacted and ffmpeg is not needed (download+convert is
replaced by a fake). Run from the repo root:
    python -m pytest tests
with the SDK version from dev_requirements.txt installed (plus pytest).
"""
import importlib
import os
import sys
from types import SimpleNamespace

import pytest

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
APP_MODULES = ("sly_globals", "sly_functions", "main", "workflow", "download_progress")


class FakeFileApi:
    def __init__(self, files):
        self.files = list(files)
        self.removed = []

    def list(self, team_id, path, *args, **kwargs):
        return [
            {"path": p, "name": os.path.basename(p), "meta": {"size": 1024}}
            for p in self.files
            if p.startswith(path)
        ]

    def is_on_agent(self, remote_path):
        return remote_path.startswith("agent://")

    def remove(self, team_id, path):
        self.removed.append(path)


class FakeVideoApi:
    def __init__(self, server_rejects=()):
        self.server_rejects = set(server_rejects)
        self.uploaded = []

    def upload_paths(self, dataset_id, names, paths, progress_cb=None, **kwargs):
        # Like the SDK: a video the server fails to process is logged as
        # "File skipped ..." and simply missing from the returned infos.
        infos = []
        for name in names:
            if name in self.server_rejects:
                continue
            self.uploaded.append((dataset_id, name))
            infos.append(SimpleNamespace(id=len(self.uploaded), name=name))
        return infos


class FakeApi:
    def __init__(self, files, server_rejects=()):
        self.file = FakeFileApi(files)
        self.video = FakeVideoApi(server_rejects)
        self._ds = 0
        self.project = SimpleNamespace(
            get_info_by_id=lambda id: None,
            create=lambda workspace_id, name, change_name_if_conflict=False, type=None: (
                SimpleNamespace(id=100, name=name)
            ),
        )
        self.dataset = SimpleNamespace(create=self._create_dataset, get_info_by_id=None)
        self.output_project = None
        self.task = SimpleNamespace(set_output_project=self._set_output_project)
        self.app = SimpleNamespace(
            workflow=SimpleNamespace(add_output_project=lambda project_id: None)
        )

    def _create_dataset(self, project_id, name, change_name_if_conflict=False):
        self._ds += 1
        return SimpleNamespace(id=self._ds, name=name)

    def _set_output_project(self, task_id, project_id, project_name=None):
        self.output_project = project_id


@pytest.fixture
def run_app(tmp_path, monkeypatch):
    """Import the app for the given Team Files content and return (main, g, api).

    `download_fails` are remote paths whose download raises (e.g. api.file.download
    giving up after retries, or OSError: disk full).
    """
    import supervisely as sly

    def _run(files, input_path="/videos/", remove_source=True, download_fails=(),
             server_rejects=()):
        api = FakeApi(files, server_rejects)
        monkeypatch.chdir(tmp_path)  # sly_globals creates ./storage_dir
        monkeypatch.setenv("ENV", "production")
        monkeypatch.setenv("TASK_ID", "1")
        monkeypatch.setenv("context.teamId", "8")
        monkeypatch.setenv("context.workspaceId", "9")
        monkeypatch.setenv("modal.state.slyFolder", input_path)
        monkeypatch.setenv("modal.state.removeSource", "true" if remove_source else "false")
        for name in ("modal.state.files", "modal.state.slyFile", "context.projectId",
                     "context.datasetId", "modal.state.projectName"):
            monkeypatch.delenv(name, raising=False)
        monkeypatch.setattr(sly.Api, "from_env", classmethod(lambda cls, *a, **k: api))
        monkeypatch.syspath_prepend(SRC_DIR)
        for mod in APP_MODULES:
            sys.modules.pop(mod, None)
        main = importlib.import_module("main")
        g = importlib.import_module("sly_globals")

        def fake_convert_to_mp4(remote_video_path, video_size):
            if remote_video_path in download_fails:
                raise OSError(f"[Errno 28] No space left on device: {remote_video_path}")
            name = os.path.splitext(os.path.basename(remote_video_path))[0] + ".mp4"
            local = os.path.join(g.STORAGE_DIR, name)
            open(local, "wb").close()
            return name, local

        monkeypatch.setattr(main.f, "convert_to_mp4", fake_convert_to_mp4)
        return main, g, api

    yield _run
    for mod in APP_MODULES:
        sys.modules.pop(mod, None)
