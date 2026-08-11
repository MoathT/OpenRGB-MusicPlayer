# OpenRGB Media Sync

A lightweight script that syncs **OpenRGB** with whatever music player is active on your system.

---

## Prerequisites

Before running the script, ensure you have:

* **OpenRGB** installed and set up with your RGB hardware. https://openrgb.org/
* **Python 3.x** installed (if running the `.py` source file directly). i used MC version 

---
##  ⚠️⚠️ BEFORE START MAKE SURE ALL OF YOUR PC LED ARE ON IN OPENRGB AND IN DIRECT MODE
## Step-by-Step Setup

### 1. Enable OpenRGB SDK Server
For the script to talk to OpenRGB, the SDK server **must be running**:

1. Open **OpenRGB**.
2. Go to the **SDK Server** tab at the top.
3. Click **Start Server**.
4. *(Optional)* Check **Set OpenRGB to start at login / launch** so you don't have to do this manually every time.

<img width="864" height="169" alt="OpenRGB SDK Server Tab" src="https://github.com/user-attachments/assets/72652173-8ff0-4ff2-a149-c828af07ab60" />

---

### 2. Check Windows Media Overlay
The script reads active media information directly from Windows:

1. Open your preferred music player (**Spotify**, **Apple Music**, **SoundCloud**, etc.).
   > **Note:** Web browsers (like **Brave**) are **not supported**. Use standalone apps.
2. Play any track.
3. Press your keyboard's volume keys to make sure the **Windows Media Control popup** appears showing the song title and album art.
4. **Important:** If multiple apps are open, **click the right arrow icon** on the overlay until it switches to your current playing song.

<img width="382" height="197" alt="Windows Media Overlay" src="https://github.com/user-attachments/assets/3da0c49e-b1a0-40c9-bf06-b525b2986b42" />

---

### 3. Run the Script

1. Download or clone this repository.
2. Run `openrgb_Music.py`.
3. The script will **automatically generate `openrgb.log`** in the same folder on its first run and start syncing.

---

## Troubleshooting

* **Script creates `openrgb.log` but LEDs don't sync:** Verify that the **SDK Server** inside OpenRGB is active and running on port **`6742`**.
* **Track info isn't updating:** Ensure your media player supports **Windows System Media Transport Controls**. Try pressing a volume key to see if the song overlay pops up.
