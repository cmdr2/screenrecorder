# Screen Recorder
A simple, open source screen recorder. Drag-select and Record.

Yes, there are alternatives (e.g. the Windows Snipping Tool's video-recording mode). But I needed certain specific features for my workflow, like persistent recording regions (across restarts), quick video resize etc. And it's open source, so you can customize it for your needs as well.

And it was fun to learn Tkinter and build something real with it. Also ended up building [tkinter-videoplayer](https://github.com/cmdr2/tkinter-videoplayer), which is a useful video player component for Tkinter.

## Features
- Screen recording functionality
- Built-in video preview and editing
- Trim and Resize tools
- Persistent recording regions
- User-friendly interface
- Free and fully open source (MIT)

## Install
1. Install [Python](https://www.python.org/downloads/).
2. Then download screenrecorder for:
* [Windows](https://github.com/cmdr2/screenrecorder/releases/latest/download/screenrecorder-win-x86_64.zip)
* [Linux](https://github.com/cmdr2/screenrecorder/releases/latest/download/screenrecorder-linux-x86_64.zip)
3. Finally, extract the zip file.

## Run using:
* Windows: Double-click `screenrecorder.cmd`
* Linux: Run `./screenrecorder.sh`

## Third-Party Software

This application includes FFmpeg for video processing:
- **FFmpeg**: Licensed under GPL v3 
- Full licensing details and license text available in `THIRD-PARTY-LICENSES.md`

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

Note: While this project's source code is under MIT license, the bundled FFmpeg binary is under GPL v3 license.

## Requirements

See `requirements.txt` for Python dependencies.
