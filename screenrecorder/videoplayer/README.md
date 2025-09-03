# Tkinter VideoPlayer Component

A reusable video player component for Tkinter, built with OpenCV and Pillow.

## Features
- Play, pause, stop, and seek video files
- Customizable controls and themes
- Seconds counter, toggle play/pause with a button or click or spacebar
- Looks reasonable, and can be customized from `theme.py`
- Frame-by-frame rendering using OpenCV
- Image processing with Pillow

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Import the component in your Tkinter project.

## Quick Start

```python
from videoplayer import VideoPlayerComponent
import tkinter as tk

root = tk.Tk()
player = VideoPlayerComponent(root, video_path='sample.mp4')
player.frame.pack(fill='both', expand=True)
root.mainloop()
```

## Public API

### `VideoPlayer(parent, video_path, **options)`

- `parent`: Tkinter parent widget
- `video_path`: Path to the video file
- `**options`: Additional options to customize the player:
   - `autoplay` (bool): Start playback automatically when loaded. Default: `False`.
   - `loop` (bool): Loop the video when it reaches the end. Default: `False`.
   - `controls` (bool): Show playback controls (play, pause, seek, etc.). Default: `True`.
   - `width` (int): Width of the video player in pixels. Default: video width or parent width.
   - `height` (int): Height of the video player in pixels. Default: video height or parent height.

You can also edit the default theme by modifying `theme.py`.

#### Methods
- `play()`: Start or resume playback
- `pause()`: Pause playback
- `stop()`: Stop playback and reset

#### Properties
- `autoplay` (bool): Whether playback starts automatically when loaded.
- `loop` (bool): Whether playback loops when the video ends.
- `controls_enabled` (bool): Whether playback controls are shown.
- `currentTime` (float): Current playback time in seconds (get/set).
- `duration` (float): Duration of the loaded video in seconds (read-only).

#### Events
- `play`: Called when playback starts
- `pause`: Called when playback pauses
- `ended`: Called when playback ends
- `load`: Called when the video loads

## Usage Example

```python
from videoplayer import VideoPlayerComponent
import tkinter as tk

root = tk.Tk()
player = VideoPlayerComponent(root, video_path='sample.mp4', width=640, height=360)
player.frame.pack()

# Control playback
player.play()
player.pause()
player.stop()

# Add event handlers
def handle_play():
   print("Video started!")

def handle_pause():
   print("Video paused.")

def handle_ended():
   print("Video ended.")

player.add_event_listener("play", handle_play)
player.add_event_listener("pause", handle_pause)
player.add_event_listener("stop", handle_stop)

root.mainloop()
```
