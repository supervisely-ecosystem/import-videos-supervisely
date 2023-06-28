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

⚠️ All videos will be converted to `.mp4` format during import.

🌎 Community version has a 300MB limitation for video size, no limits apply to Enterprise Edition 


**App updates:**

🏋️ Starting from version `v1.1.3` application supports import from a special directory on your local computer. It is made for Enterprise Edition customers who need to upload tens or even hundreds of gigabytes of data without using a drag-and-drop mechanism:

1. Run the agent on your computer where data is stored. Watch the [how-to video](https://youtu.be/aO7Zc4kTrVg).
2. Copy your data to the special folder on your computer that was created by the agent. Agent mounts this directory to your Supervisely instance and it becomes accessible in Team Files. Learn more in the [documentation](https://docs.supervise.ly/customization/agents/agent-storage). Watch the [how-to video](https://youtu.be/63Kc8Xq9H0U).
3. Go to `Team Files` -> `Supervisely Agent` and find your folder there.
4. Right-click to open the context menu and start the app. Now the app will upload data directly from your computer to the platform.

📥 Starting from version `v1.2.0` application supports import to existing projects and datasets:

1. The app now has 3 import modes in the modal window:
   1. Create new project
   2. Upload to an existing project
   3. Upload to an existing dataset

    ![new-modal](https://user-images.githubusercontent.com/48913536/199000700-426fbf14-dc1f-45af-885d-2fe3d0d47cb9.png)

2. When uploading to an existing dataset, make sure videos have unique names

## Preparation
The directory name defines the project name, subdirectories define the dataset names.  
Videos in the root directory will be moved to the dataset with the name "ds0".

```
.
📂my_videos_project
├──📜video_01.mp4
├──📜...
├──📜video_01.mov
│
├──📂my_folder1
│   ├──📜video_03.mp4
│   └──📜video_04.mp4
│
└──📂my_folder2
    ├──📜video_05.mp4
    ├──📜video_06.mp4
    └──📜video_07.mp4
```
    
As a result, we will get project **my_videos_project** with 3 datasets with the names: **ds0**, **my_folder1**, and **my_folder2**.  
