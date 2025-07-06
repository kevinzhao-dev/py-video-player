#!/usr/bin/env python3
"""
Simple Python-based CLI video player (pp - python player)
"""

import argparse
import cv2
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

__version__ = "0.0.1"

class VideoPlayer:
    def __init__(self, path: str, seek_short: int = 10, seek_long: int = 60):
        self.path = Path(path)
        self.seek_short = seek_short  # seconds
        self.seek_long = seek_long    # seconds
        self.video_files = []
        self.current_index = 0
        self.is_playing = True
        self.is_muted = False
        self.timestamps = {}  # Store last watched timestamps
        self.cap = None
        self.fps = 30
        self.frame_count = 0
        self.current_frame = 0

        # Supported video extensions
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

        # Load video files
        self.load_video_files()

        # Load saved timestamps
        self.load_timestamps()

    def load_video_files(self):
        """Load all video files from the given path"""
        if self.path.is_file():
            # If it's a file, get all videos from its directory
            directory = self.path.parent
        else:
            # If it's a directory, use it directly
            directory = self.path

        if not directory.exists():
            print(f"Error: Path {directory} does not exist")
            sys.exit(1)

        # Find all video files
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.video_extensions:
                self.video_files.append(file_path)

        # Sort files for consistent ordering
        self.video_files.sort()

        if not self.video_files:
            print(f"No video files found in {directory}")
            sys.exit(1)

        # If a specific file was provided, set it as current
        if self.path.is_file() and self.path in self.video_files:
            self.current_index = self.video_files.index(self.path)

        print(f"Found {len(self.video_files)} video files")

    def load_timestamps(self):
        """Load saved timestamps from file"""
        timestamp_file = Path.home() / '.pp_timestamps.json'
        if timestamp_file.exists():
            try:
                with open(timestamp_file, 'r') as f:
                    self.timestamps = json.load(f)
            except:
                self.timestamps = {}

    def save_timestamps(self):
        """Save current timestamps to file"""
        timestamp_file = Path.home() / '.pp_timestamps.json'
        try:
            with open(timestamp_file, 'w') as f:
                json.dump(self.timestamps, f)
        except:
            pass

    def load_video(self, index: int):
        """Load video at given index"""
        if 0 <= index < len(self.video_files):
            # Save current timestamp before switching
            if self.cap is not None:
                current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                self.timestamps[str(self.video_files[self.current_index])] = current_time

            self.current_index = index
            video_path = self.video_files[self.current_index]

            if self.cap:
                self.cap.release()

            self.cap = cv2.VideoCapture(str(video_path))
            if not self.cap.isOpened():
                print(f"Error: Cannot open video {video_path}")
                return False

            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Restore timestamp if available
            saved_time = self.timestamps.get(str(video_path), 0)
            if saved_time > 0:
                self.cap.set(cv2.CAP_PROP_POS_MSEC, saved_time * 1000)

            print(f"Playing: {video_path.name} ({self.current_index + 1}/{len(self.video_files)})")
            return True
        return False

    def seek(self, seconds: float):
        """Seek forward or backward by given seconds"""
        if self.cap is None:
            return

        current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        new_time = max(0, current_time + seconds)

        # Don't seek beyond video duration
        duration = self.frame_count / self.fps
        new_time = min(new_time, duration)

        self.cap.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)

    def play(self):
        """Main playback loop"""
        if not self.load_video(self.current_index):
            return

        cv2.namedWindow('Video Player', cv2.WINDOW_NORMAL)

        while True:
            if self.is_playing:
                ret, frame = self.cap.read()
                if not ret:
                    # End of video, go to next
                    self.next_video()
                    continue

                cv2.imshow('Video Player', frame)

            # Handle keyboard input
            key = cv2.waitKey(1 if self.is_playing else 0) & 0xFF

            if key == ord('q') or key == 27:  # ESC key
                break
            elif key == ord(' '):  # Space - pause/play
                self.is_playing = not self.is_playing
                print("Paused" if not self.is_playing else "Playing")
            elif key == ord('m'):  # Mute toggle
                self.is_muted = not self.is_muted
                print("Muted" if self.is_muted else "Unmuted")
            elif key == 81 or key == 2:  # Left arrow - seek backward (short)
                self.seek(-self.seek_short)
                print(f"Seeking backward {self.seek_short}s")
            elif key == 83 or key == 3:  # Right arrow - seek forward (short)
                self.seek(self.seek_short)
                print(f"Seeking forward {self.seek_short}s")
            elif key == 82 or key == 0:  # Up arrow - seek forward (long)
                self.seek(self.seek_long)
                print(f"Seeking forward {self.seek_long}s")
            elif key == 84 or key == 1:  # Down arrow - seek backward (long)
                self.seek(-self.seek_long)
                print(f"Seeking backward {self.seek_long}s")
            elif key == ord('j'):  # Previous video
                self.prev_video()
            elif key == ord('k') or key == 13:  # Next video (k or Enter)
                self.next_video()

        # Cleanup
        if self.cap:
            # Save current timestamp
            current_time = self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            self.timestamps[str(self.video_files[self.current_index])] = current_time
            self.cap.release()

        cv2.destroyAllWindows()
        self.save_timestamps()

    def next_video(self):
        """Switch to next video"""
        next_index = (self.current_index + 1) % len(self.video_files)
        self.load_video(next_index)

    def prev_video(self):
        """Switch to previous video"""
        prev_index = (self.current_index - 1) % len(self.video_files)
        self.load_video(prev_index)


def main():
    parser = argparse.ArgumentParser(description='Simple Python Video Player (pp)')
    parser.add_argument('path', nargs='?', default='.', 
                       help='Path to video file or directory (default: current directory)')
    parser.add_argument('--seek-short', type=int, default=10,
                       help='Short seek duration in seconds (default: 10)')
    parser.add_argument('--seek-long', type=int, default=60,
                       help='Long seek duration in seconds (default: 60)')

    args = parser.parse_args()

    player = VideoPlayer(args.path, args.seek_short, args.seek_long)

    print("Controls:")
    print("  Space: Pause/Play")
    print("  Left/Right: Seek ±10s (or custom)")
    print("  Up/Down: Seek ±1min (or custom)")
    print("  j: Previous video")
    print("  k/Enter: Next video")
    print("  m: Mute/Unmute")
    print("  q/ESC: Quit")
    print()

    try:
        player.play()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()