"""`removeSource` must only delete the Team Files source after a complete import.

Before the fix download+convert was wrapped in `except Exception: logger.warn`, videos
the server rejected were dropped by `upload_paths`, and `api.file.remove(team_id,
INPUT_PATH)` ran unconditionally, so a partial import deleted the only copy of the
videos that did not make it into the project.
"""


def _videos(n, folder="/videos/"):
    return [f"{folder}clip_{i}.mp4" for i in range(n)]


def _import(main, api):
    """Run the import; return the exception the task would end with (None on success)."""
    try:
        main.import_videos(api)
    except Exception as e:  # noqa: BLE001 - the task's final error is what we check
        return e
    return None


def test_full_success_removes_source(run_app):
    main, g, api = run_app(_videos(3))

    assert _import(main, api) is None

    assert len(api.video.uploaded) == 3
    assert api.file.removed == ["/videos/"]
    assert api.output_project == 100


def test_download_failure_keeps_source_and_fails_task(run_app):
    main, g, api = run_app(_videos(3), download_fails={"/videos/clip_1.mp4"})

    err = _import(main, api)

    assert api.file.removed == []  # source kept: it holds the only copy of clip_1
    assert len(api.video.uploaded) == 2  # what was imported stays in the project
    assert api.output_project == 100
    assert err is not None and "1 of 3 videos failed" in str(err)


def test_server_rejection_keeps_source_and_fails_task(run_app):
    main, g, api = run_app(_videos(3), server_rejects={"clip_2.mp4"})

    err = _import(main, api)

    assert api.file.removed == []
    assert len(api.video.uploaded) == 2
    assert err is not None and "1 of 3 videos failed" in str(err)


def test_unsupported_files_keep_source(run_app):
    main, g, api = run_app(_videos(2) + ["/videos/notes.txt"])

    assert _import(main, api) is None  # skipping non-videos is not an error

    assert len(api.video.uploaded) == 2
    assert api.file.removed == []


def test_remove_source_off_never_removes(run_app):
    main, g, api = run_app(_videos(2), remove_source=False)

    assert _import(main, api) is None

    assert api.file.removed == []
