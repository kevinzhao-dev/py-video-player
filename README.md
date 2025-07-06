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

### Option 1: Install as CLI tool (Recommended)

```bash
# Install from source
git clone https://github.com/kevinzhao-dev/py-video-player.git
cd py-video-player
pip install -e .

# Or install directly from PyPI (when published)
pip install simple-video-player
```

After installation, you can use `pp` command from anywhere:

```bash
pp ~/Movies
pp video.mp4
```

### Option 2: Run from source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kevinzhao-dev/py-video-player.git
   cd py-video-player
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the script**:
   ```bash
   python pp.py
   ```

## Usage

### Basic Usage

```bash
# Using installed CLI tool
pp                      # Play all videos in current directory
pp path/to/video.mp4    # Play a specific video file
pp path/to/directory    # Play all videos in a directory

# Or using Python script directly
python pp.py            # Play all videos in current directory
python pp.py path/to/video.mp4    # Play a specific video file
python pp.py path/to/directory    # Play all videos in a directory
```

### Command Line Options

```bash
pp [PATH] [OPTIONS]

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
pp ~/Movies --seek-short 5 --seek-long 30

# Play a specific video
pp vacation.mp4

# Play all videos in Downloads folder
pp ~/Downloads
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

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=pp --cov-report=html
```

### Building the Package

```bash
# Install build dependencies
pip install build

# Build the package
python -m build
```

## Requirements

- Python 3.6+
- OpenCV Python (`opencv-python>=4.5.0`)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

This project is open source and available under the MIT License.