<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/import-videos-supervisely/releases/download/v0.0.1/poster.png"/>



# Import Videos

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a> 
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-videos-supervisely)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-videos-supervisely)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/import-videos-supervisely.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/import-videos-supervisely.png)](https://supervise.ly)

</div>

## Overview

Application imports selected Videos without annotations to Supervisely.

**Supported video formats:** .avi, .mov, .wmv, .webm, .3gp, .mp4, .flv

**Note:** all videos will be converted to `.mp4` format during import.

🏋️ Starting from version `v1.1.1` application supports import from special directory on your local computer. It is made for Enterprise Edition customers who need to upload tens or even hundreds of gigabytes of data without using drag-ang-drop mechanism:

1. Run agent on your computer where data is stored.
2. Copy your data to special folder on your computer that was created by agent. Agent mounts this directory to your Supervisely instance and it becomes accessible in Team Files. Learn more [in documentation](https://github.com/supervisely/docs/blob/master/customization/agents/agent-storage/agent-storage.md).
3. Go to `Team Files` -> `Supervisely Agent` and find your folder there.
4. Right click to open context menu and start app. Now app will upload data directly from your computer to the platform.

## Preparation
Directory name defines project name, subdirectories define dataset names.  
Videos in root directory will be moved to dataset with name "ds0".

```
.
my_videos_project
├── video_01.mp4
├── ...
├── video_01.mov
├── my_folder1
│   ├── video_03.mp4
│   ├── video_04.mp4
└── my_folder2
    ├── video_05.mp4
    ├── video_06.mp4
    └── video_07.mp4
```
    
As a result we will get project my_videos_project with 3 datasets with the names: ds0, my_folder1, my_folder2.  
