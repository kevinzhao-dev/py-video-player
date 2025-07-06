# Simple Video Player (pp) v0.1.0

A powerful command-line video player built with Python and OpenCV, featuring audio synchronization, speed control, and professional on-screen status display.

## ✨ Features

### 🎥 **Core Video Playback**
- **Multi-format support**: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- **Directory browsing**: Automatically discovers and plays all videos in a directory
- **Resume playback**: Remembers where you left off in each video
- **Playlist navigation**: Navigate between videos with keyboard shortcuts

### 🔊 **Audio Integration** 
- **Synchronized audio**: Full audio playback using ffmpeg/ffplay
- **Audio seeking**: Audio stays in sync when seeking forward/backward
- **Mute control**: Toggle audio on/off with visual feedback
- **Speed-matched audio**: Audio speed adjusts with video speed changes

### ⚡ **Speed Control**
- **Variable playback speed**: 0.1x to 3.0x (10% to 300%)
- **Fine control**: Adjust speed in 10% increments with `[` and `]` keys
- **Real-time audio sync**: Audio speed matches video speed instantly
- **Visual feedback**: Speed indicator in window title and status overlay

### 📺 **Professional Status Display**
- **On-screen overlay**: Status messages appear directly on video (top-left)
- **Smooth animations**: 2.5-second display with fade-out effect
- **Font fallback**: Automatic font compatibility across different systems
- **Visual indicators**: Icons for seeking (◀▶), speed, pause/play status

### 📝 **Logging & Monitoring**
- **Structured logging**: All events logged to `~/.pp_player.log`
- **Clean terminal**: No console spam, organized log output
- **Error handling**: Graceful failure recovery with detailed logging
- **Debug friendly**: Comprehensive error messages and warnings

### 🧪 **Quality Assurance**
- **Comprehensive testing**: 32+ unit tests with 57% code coverage
- **CI/CD integration**: Automated testing on macOS with Python 3.12+
- **Error resilience**: Robust handling of font, audio, and video issues
- **Cross-system compatibility**: Tested font rendering and audio systems

## 🚀 Installation

### Option 1: Install as CLI tool (Recommended)

```bash
# Install from source
git clone https://github.com/kevinzhao-dev/py-video-player.git
cd py-video-player
pip install -e .

# Or install directly from PyPI (when published)
pip install simple-video-player
```

After installation, use the `pp` command from anywhere:

```bash
pp ~/Movies                    # Play all videos in directory
pp video.mp4                   # Play specific video
pp ~/Downloads --seek-short 5  # Custom seek intervals
```

### Option 2: Run from source

```bash
git clone https://github.com/kevinzhao-dev/py-video-player.git
cd py-video-player
pip install -r requirements.txt
python pp.py ~/Movies
```

## 🎮 Controls

| Key | Action | Status Display |
|-----|--------|----------------|
| **Space** | Pause/Play | `Playing` / `Paused` |
| **Left/Right** | Seek ±10s (configurable) | `◀ 10s` / `▶ 10s` |
| **Up/Down** | Seek ±60s (configurable) | `◀◀ 60s` / `▶▶ 60s` |
| **]** | Speed up 10% | `Speed: 1.3x` |
| **[** | Speed down 10% | `Speed: 0.9x` |
| **j** | Previous video | `Playing: filename.mp4` |
| **k/Enter** | Next video | `Playing: filename.mp4` |
| **m** | Mute/Unmute | `Muted` / `Unmuted` |
| **q/ESC** | Quit | - |

## 💡 Usage Examples

### Basic Playback
```bash
pp                              # Play videos in current directory
pp ~/Movies                     # Play all videos in Movies folder
pp "vacation video.mp4"         # Play specific video (handles spaces)
```

### Custom Speed Control
```bash
pp ~/Movies --seek-short 5 --seek-long 30
# Then use [ ] keys to adjust speed: 0.1x → 3.0x
# Audio automatically matches video speed
```

### Advanced Features
```bash
# The player automatically:
# - Resumes from last position
# - Shows status overlay with fade effects
# - Logs all activity to ~/.pp_player.log
# - Handles font rendering issues gracefully
# - Synchronizes audio with video and speed changes
```

## 🔧 Dependencies

### Required
- **Python 3.12+** (recommended)
- **OpenCV**: `opencv-python>=4.5.0`
- **NumPy**: `numpy>=1.19.0`

### Audio Support (Optional but Recommended)
- **FFmpeg**: Install via homebrew on macOS
  ```bash
  brew install ffmpeg
  ```
  
  Without ffmpeg, video playback works but audio is disabled.

## 🏗️ Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=pp --cov-report=html

# Run specific test categories
pytest tests/test_advanced_features.py -v
```

### Building Package
```bash
pip install build
python -m build
```

### CI/CD
The project includes GitHub Actions workflow optimized for macOS:
- Python 3.12+ compatibility testing
- Automated testing with audio dependencies
- Code coverage reporting
- Package building and validation

## 📊 Technical Details

### Audio Synchronization
- Uses `ffplay` subprocess for audio playback
- Implements `atempo` filter for speed matching
- Restarts audio stream when seeking to maintain sync
- Graceful fallback when audio system unavailable

### Status Display System
- OpenCV-based overlay rendering with alpha blending
- Font fallback system tests 8 different OpenCV fonts
- Position calculation with boundary checking
- Fade-out animation using time-based alpha interpolation

### Performance Optimizations
- Frame rate calculation: `1.0 / (fps * playback_speed)`
- Font testing done once at startup, not per frame
- Audio process management with proper cleanup
- Efficient timestamp persistence with JSON storage

## 🎯 Version History

### v0.1.0 (Current)
- ✅ **Full audio synchronization** with ffmpeg integration
- ✅ **Variable speed control** (0.1x - 3.0x) with audio sync
- ✅ **Professional status overlay** with fade effects and font fallback
- ✅ **Comprehensive logging system** with file and console output
- ✅ **32+ unit tests** with CI/CD integration
- ✅ **Robust error handling** for audio, fonts, and video issues

### v0.0.1 (Initial)
- Basic video playback with OpenCV
- Simple seeking and playlist navigation
- Resume playback functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run tests: `pytest`
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for seamless video playback on macOS**