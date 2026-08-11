Prerequisites

Before running the script, ensure you have:

OpenRGB installed and working with your RGB hardware.

Python 3.x installed (if running the source code directly).

Step-by-Step Setup
-----------------------
1. Enable OpenRGB SDK Server
For the script to talk to OpenRGB, the SDK server must be running:

Open OpenRGB.

Go to the SDK Server tab at the top.

Click Start Server.

(Optional) Check Start at launch so you don't have to do this manually every time.

<img width="864" height="169" alt="image" src="https://github.com/user-attachments/assets/72652173-8ff0-4ff2-a149-c828af07ab60" />


2. Configure Windows Media Overlay
The script reads active media information directly from Windows:

Open your preferred music player (Spotify, Apple Music, SoundCloud, etc.). --- browser are not supported i tested Brave only ------

Play any track.

Use your keyboard's volume keys or media keys to verify that the Windows Media Control popup appears in the corner of your screen showing the song name and album art.
<img width="382" height="197" alt="image" src="https://github.com/user-attachments/assets/3da0c49e-b1a0-40c9-bf06-b525b2986b42" />

CLICK IN THE ARROW RIGHT IF IT DIDNT SWITCH TO YOUR SONG



3. Run the Script
Clone or download this repository.

Run openrgb_Music.py script file.

The script will automatically create openrgb.log in the same directory on its first launch and begin monitoring your media playback.





Troubleshooting
Script creates openrgb.log but doesn't sync: Make sure the SDK server in OpenRGB is currently running on the default port (6742).

Track info isn't updating: Check if your media player supports Windows System Media Transport Controls. Try adjusting the volume using media keys to see if the Windows mini-player pops up.



PHOTO WILL SHOW IT SHOULD BE LOOK LIKE - 
