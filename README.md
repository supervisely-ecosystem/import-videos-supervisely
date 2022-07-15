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
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-videos-supervisely&counter=views&label=views)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-videos-supervisely&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

Application imports selected Videos without annotations to Supervisely.

**Supported video formats:** .avi, .mov, .wmv, .webm, .3gp, .mp4, .flv

**Note:** all videos will be converted to `.mp4` format during import.

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
