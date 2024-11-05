<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/import-videos-supervisely/releases/download/v0.0.1/poster.png"/>

# Import Videos

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#Preparation">Preparation</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/import-videos-supervisely)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-videos-supervisely)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/import-videos-supervisely.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/import-videos-supervisely.png)](https://supervisely.com)

</div>

## Overview

Application imports selected Videos without annotations to Supervisely.

**Supported video formats:** .avi, .mov, .wmv, .webm, .3gp, .mp4, .flv

⚠️ All videos will be converted to `.mp4` format during import.

Single video file size limits:
- 📚 `Community` plan: **100MB**
- 🏢 `Pro` plan: **500MB**
- 🚀 `Enterprise` edition: **no limits**

**App updates:**

📄 `v1.3.20` Starting from this version application supports uploading the files from TeamFiles and drag and drop option.

🏋️ Starting from version `v1.1.3` application supports import from a special directory on your local computer. It is made for Enterprise Edition customers who need to upload tens or even hundreds of gigabytes of data without using a drag-and-drop mechanism:

1. Run the agent on your computer where data is stored. Watch the [how-to video](https://youtu.be/aO7Zc4kTrVg).
2. Copy your data to the special folder on your computer that was created by the agent. Agent mounts this directory to your Supervisely instance and it becomes accessible in Team Files. Learn more in the [documentation](https://docs.supervisely.com/customization/agents/agent-storage). Watch the [how-to video](https://youtu.be/63Kc8Xq9H0U).
3. Go to `Team Files` -> `Supervisely Agent` and find your folder there.
4. Right-click to open the context menu and start the app. Now the app will upload data directly from your computer to the platform.

📥 Starting from version `v1.2.0` application supports import to existing projects and datasets and has 3 modes:

   1. Create new project

      <img width=460 src="https://github.com/supervisely-ecosystem/import-videos-supervisely/assets/57998637/0641e5e7-5309-4f88-b1d5-43f91e079dcb">

   2. Upload to an existing project

      <img width=460 src="https://github.com/supervisely-ecosystem/import-videos-supervisely/assets/57998637/58d9e05d-761d-4bf4-ab77-3b3c8bd8be55">

   3. Upload to an existing dataset. ⚠️ When uploading to an existing dataset, make sure videos have unique names!
      
      <img width=460 src="https://github.com/supervisely-ecosystem/import-videos-supervisely/assets/57998637/c5268beb-dd7f-4305-80b0-0ca5169e9629">

## Preparation
The directory name defines the project name, subdirectories define the dataset names.  
Videos in the root directory will be moved to the dataset with the name "ds0".<br>
ℹ️ You can download the archive with data example [here](https://github.com/supervisely-ecosystem/import-videos-supervisely/files/12537259/my_videos_project.zip).

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
    
As a result, we will get project `my_videos_project` with 3 datasets named: `ds0`, `my_folder1`, and `my_folder2`.  
