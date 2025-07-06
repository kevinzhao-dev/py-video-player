#!/usr/bin/env python3
"""
Unit tests for VideoPlayer class
"""

import unittest
import tempfile
import json
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import pp module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pp import VideoPlayer


class TestVideoPlayer(unittest.TestCase):
    """Test cases for VideoPlayer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test video files
        self.test_files = [
            self.temp_path / "video1.mp4",
            self.temp_path / "video2.avi",
            self.temp_path / "video3.mkv",
            self.temp_path / "not_video.txt"
        ]

        # Create the files
        for file_path in self.test_files:
            file_path.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_init_with_directory(self):
        """Test VideoPlayer initialization with directory path"""
        player = VideoPlayer(str(self.temp_path))

        # Should find 3 video files (excluding .txt)
        self.assertEqual(len(player.video_files), 3)
        self.assertEqual(player.current_index, 0)
        self.assertTrue(player.is_playing)
        self.assertFalse(player.is_muted)
        self.assertEqual(player.seek_short, 10)
        self.assertEqual(player.seek_long, 60)

    def test_init_with_specific_file(self):
        """Test VideoPlayer initialization with specific video file"""
        video_file = self.test_files[1]  # video2.avi
        player = VideoPlayer(str(video_file))

        # Should find all video files but set current index to the specified file
        self.assertEqual(len(player.video_files), 3)
        self.assertEqual(player.current_index, 1)  # video2.avi is at index 1

    def test_init_with_custom_seek_times(self):
        """Test VideoPlayer initialization with custom seek times"""
        player = VideoPlayer(str(self.temp_path), seek_short=5, seek_long=30)

        self.assertEqual(player.seek_short, 5)
        self.assertEqual(player.seek_long, 30)

    def test_load_video_files(self):
        """Test loading video files from directory"""
        player = VideoPlayer(str(self.temp_path))

        # Check that only video files are loaded
        video_extensions = {'.mp4', '.avi', '.mkv'}
        for video_file in player.video_files:
            self.assertIn(video_file.suffix.lower(), video_extensions)

    def test_video_extensions_filtering(self):
        """Test that non-video files are filtered out"""
        player = VideoPlayer(str(self.temp_path))

        # Should not include .txt file
        txt_file = self.temp_path / "not_video.txt"
        self.assertNotIn(txt_file, player.video_files)

    def test_timestamps_functionality(self):
        """Test timestamp saving and loading"""
        player = VideoPlayer(str(self.temp_path))

        # Test setting and getting timestamps
        test_timestamp = 123.45
        test_file = str(self.test_files[0])
        player.timestamps[test_file] = test_timestamp

        self.assertEqual(player.timestamps[test_file], test_timestamp)

    @patch('pp.cv2.VideoCapture')
    def test_load_video_success(self, mock_cv2_capture):
        """Test successful video loading"""
        # Mock cv2.VideoCapture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 1800.0,
            cv2.CAP_PROP_POS_MSEC: 0.0
        }.get(prop, 0.0)
        mock_cv2_capture.return_value = mock_cap

        player = VideoPlayer(str(self.temp_path))
        player.cap = None  # Reset cap

        result = player.load_video(0)

        self.assertTrue(result)
        mock_cv2_capture.assert_called_once()

    @patch('pp.cv2.VideoCapture')
    def test_load_video_failure(self, mock_cv2_capture):
        """Test video loading failure"""
        # Mock cv2.VideoCapture to fail
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_cv2_capture.return_value = mock_cap

        player = VideoPlayer(str(self.temp_path))
        player.cap = None  # Reset cap

        result = player.load_video(0)

        self.assertFalse(result)

    def test_load_video_invalid_index(self):
        """Test loading video with invalid index"""
        player = VideoPlayer(str(self.temp_path))

        # Test with negative index
        result = player.load_video(-1)
        self.assertFalse(result)

        # Test with index beyond range
        result = player.load_video(len(player.video_files))
        self.assertFalse(result)

    @patch('pp.cv2.VideoCapture')
    def test_seek_functionality(self, mock_cv2_capture):
        """Test seeking functionality"""
        # Mock cv2.VideoCapture
        mock_cap = Mock()
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_POS_MSEC: 10000.0,  # 10 seconds
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 1800.0
        }.get(prop, 0.0)
        mock_cv2_capture.return_value = mock_cap

        player = VideoPlayer(str(self.temp_path))
        player.cap = mock_cap
        player.fps = 30.0
        player.frame_count = 1800

        # Test seeking forward
        player.seek(10)
        mock_cap.set.assert_called_with(cv2.CAP_PROP_POS_MSEC, 20000.0)

        # Test seeking backward
        player.seek(-5)
        mock_cap.set.assert_called_with(cv2.CAP_PROP_POS_MSEC, 5000.0)

    def test_next_video(self):
        """Test next video functionality"""
        player = VideoPlayer(str(self.temp_path))
        initial_index = player.current_index

        with patch.object(player, 'load_video') as mock_load:
            player.next_video()
            expected_index = (initial_index + 1) % len(player.video_files)
            mock_load.assert_called_once_with(expected_index)

    def test_prev_video(self):
        """Test previous video functionality"""
        player = VideoPlayer(str(self.temp_path))
        initial_index = player.current_index

        with patch.object(player, 'load_video') as mock_load:
            player.prev_video()
            expected_index = (initial_index - 1) % len(player.video_files)
            mock_load.assert_called_once_with(expected_index)

    def test_save_load_timestamps(self):
        """Test timestamp persistence"""
        player = VideoPlayer(str(self.temp_path))

        # Set some test timestamps
        test_data = {
            "video1.mp4": 123.45,
            "video2.avi": 67.89
        }
        player.timestamps = test_data

        # Save timestamps
        player.save_timestamps()

        # Create new player instance and load timestamps
        new_player = VideoPlayer(str(self.temp_path))

        # Check if timestamps were loaded correctly
        timestamp_file = Path.home() / '.pp_timestamps.json'
        if timestamp_file.exists():
            with open(timestamp_file, 'r') as f:
                loaded_data = json.load(f)

            # Clean up
            timestamp_file.unlink()

            # Verify data matches
            for key, value in test_data.items():
                if key in loaded_data:
                    self.assertEqual(loaded_data[key], value)


class TestVideoPlayerIntegration(unittest.TestCase):
    """Integration tests for VideoPlayer"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test video files
        self.test_files = [
            self.temp_path / "test1.mp4",
            self.temp_path / "test2.avi",
        ]

        for file_path in self.test_files:
            file_path.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_full_initialization_flow(self):
        """Test complete initialization flow"""
        player = VideoPlayer(str(self.temp_path))

        # Verify all components are initialized
        self.assertIsNotNone(player.video_files)
        self.assertIsNotNone(player.timestamps)
        self.assertIsNotNone(player.video_extensions)
        self.assertGreater(len(player.video_files), 0)


if __name__ == '__main__':
    unittest.main()