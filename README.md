# Screen Recorder
A Python-based screen recording application with video editing capabilities.

Yes, there are alternatives (e.g. the Windows Snipping Tool's video-recording mode). But I needed certain specific features for my workflow, like persistent recording regions (across restarts), quick video resize etc.

And it was fun to learn Tkinter and build something real with it. Also ended up building [tkinter-videoplayer](https://github.com/cmdr2/tkinter-videoplayer), which is a useful video player component for Tkinter.

## Features
- Screen recording functionality
- Built-in video preview and editing
- User-friendly interface
- Persistent recording regions
- Trim and Resize tools

## Run using:
`python -m screenrecorder.main`

## Third-Party Software

This application includes FFmpeg for video processing:
- **FFmpeg**: Licensed under GPL v3 
- Full licensing details and license text available in `THIRD-PARTY-LICENSES.md`

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

Note: While this project's source code is under MIT license, the bundled FFmpeg binary is under GPL v3 license.

## Requirements

See `requirements.txt` for Python dependencies.