# Simple Video Player (pp)

A lightweight command-line video player built with Python and OpenCV.

## Features

- **Multi-format support**: Plays MP4, AVI, MKV, MOV, WMV, FLV, WebM, and M4V files
- **Directory browsing**: Automatically discovers and plays all videos in a directory
- **Resume playback**: Remembers where you left off in each video
- **Playlist navigation**: Navigate between videos with keyboard shortcuts
- **Seeking controls**: Jump forward/backward with customizable intervals
- **Pause/resume**: Simple playback control

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Make the script executable** (optional):
   ```bash
   chmod +x pp.py
   ```

## Usage

### Basic Usage

```bash
# Play all videos in current directory
python pp.py

# Play a specific video file
python pp.py path/to/video.mp4

# Play all videos in a directory
python pp.py path/to/video/directory
```

### Command Line Options

```bash
python pp.py [PATH] [OPTIONS]

Options:
  --seek-short SECONDS    Short seek duration (default: 10 seconds)
  --seek-long SECONDS     Long seek duration (default: 60 seconds)
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| **Space** | Pause/Play |
| **Left/Right Arrow** | Seek backward/forward (short interval) |
| **Up/Down Arrow** | Seek forward/backward (long interval) |
| **j** | Previous video |
| **k** or **Enter** | Next video |
| **m** | Mute/Unmute |
| **q** or **ESC** | Quit |

## Examples

```bash
# Play videos with custom seek intervals
python pp.py ~/Movies --seek-short 5 --seek-long 30

# Play a specific video
python pp.py vacation.mp4

# Play all videos in Downloads folder
python pp.py ~/Downloads
```

## Features in Detail

### Resume Playback
The player automatically saves your position in each video to `~/.pp_timestamps.json`. When you reopen a video, it will resume from where you left off.

### Automatic Playlist
When you specify a directory or a single video file, the player automatically creates a playlist of all supported video files in that directory, sorted alphabetically.

### Supported Formats
- MP4
- AVI
- MKV
- MOV
- WMV
- FLV
- WebM
- M4V

## Requirements

- Python 3.6+
- OpenCV Python (`opencv-python>=4.5.0`)

## License

This project is open source and available under the MIT License.