#!/usr/bin/env python3
"""
Unit tests for advanced features: speed control, status display, logging
"""

import unittest
import tempfile
import time
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import cv2
import numpy as np

# Add parent directory to path to import pp module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pp import VideoPlayer


class TestSpeedControl(unittest.TestCase):
    """Test cases for playback speed control"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Create test video files
        self.test_files = [
            self.temp_path / "video1.mp4",
            self.temp_path / "video2.avi",
        ]

        for file_path in self.test_files:
            file_path.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_initial_playback_speed(self, mock_ffplay):
        """Test initial playback speed is 1.0"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))
        self.assertEqual(player.playback_speed, 1.0)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_speed_increase(self, mock_ffplay):
        """Test speed increase functionality"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Test speed increase
        original_speed = player.playback_speed
        player.change_playback_speed(0.1)
        self.assertAlmostEqual(player.playback_speed, original_speed + 0.1, places=1)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_speed_decrease(self, mock_ffplay):
        """Test speed decrease functionality"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Test speed decrease
        player.playback_speed = 1.5  # Set to higher speed first
        player.change_playback_speed(-0.1)
        self.assertAlmostEqual(player.playback_speed, 1.4, places=1)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_speed_limits(self, mock_ffplay):
        """Test speed limits (min 0.1x, max 3.0x)"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Test minimum speed limit
        player.playback_speed = 0.2
        player.change_playback_speed(-0.5)  # Should cap at 0.1
        self.assertEqual(player.playback_speed, 0.1)

        # Test maximum speed limit
        player.playback_speed = 2.9
        player.change_playback_speed(0.5)  # Should cap at 3.0
        self.assertEqual(player.playback_speed, 3.0)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_speed_no_change_threshold(self, mock_ffplay):
        """Test that very small speed changes are ignored"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        with patch.object(player, 'show_status') as mock_status:
            # Very small change should be ignored
            player.change_playback_speed(0.005)
            mock_status.assert_not_called()

    @patch('pp.VideoPlayer.check_ffplay_available')
    @patch('pp.cv2.VideoCapture')
    def test_speed_with_audio_restart(self, mock_cv2_capture, mock_ffplay):
        """Test that audio restarts when speed changes"""
        mock_ffplay.return_value = True
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 30.0
        mock_cv2_capture.return_value = mock_cap

        player = VideoPlayer(str(self.temp_path))
        player.audio_process = Mock()

        with patch.object(player, 'stop_audio') as mock_stop, \
             patch.object(player, 'play_audio') as mock_play:
            player.change_playback_speed(0.1)
            mock_stop.assert_called_once()
            mock_play.assert_called_once()


class TestStatusDisplay(unittest.TestCase):
    """Test cases for status display functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        test_file = self.temp_path / "test.mp4"
        test_file.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_show_status(self, mock_ffplay):
        """Test status display functionality"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Test showing status
        test_message = "Test Status"
        start_time = time.time()
        player.show_status(test_message)

        self.assertEqual(player.status_text, test_message)
        self.assertGreaterEqual(player.status_start_time, start_time)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_status_timeout(self, mock_ffplay):
        """Test that status messages timeout after duration"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))
        player.status_duration = 0.1  # Short duration for testing

        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Show status and check it's active
        player.show_status("Test")
        self.assertTrue(player.status_text)

        # Wait for timeout
        time.sleep(0.15)

        # Status should be cleared after drawing overlay
        result_frame = player.draw_status_overlay(test_frame)
        self.assertEqual(player.status_text, "")

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_draw_status_overlay(self, mock_ffplay):
        """Test drawing status overlay on frame"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Test with no status
        result = player.draw_status_overlay(test_frame)
        np.testing.assert_array_equal(result, test_frame)

        # Test with active status
        player.show_status("Test Status")
        result = player.draw_status_overlay(test_frame)

        # Should return a modified frame (not exactly equal)
        self.assertFalse(np.array_equal(result, test_frame))

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_status_fade_effect(self, mock_ffplay):
        """Test status fade effect calculation"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))
        player.status_duration = 1.0

        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        player.show_status("Fade Test")

        # Test during normal display (should be full opacity)
        player.status_start_time = time.time() - 0.3  # 0.3 seconds ago
        result1 = player.draw_status_overlay(test_frame)

        # Test during fade period (should be fading)
        player.status_start_time = time.time() - 0.8  # 0.8 seconds ago (in fade period)
        result2 = player.draw_status_overlay(test_frame)

        # Both should be different from original, but fade should be more subtle
        self.assertFalse(np.array_equal(result1, test_frame))
        self.assertFalse(np.array_equal(result2, test_frame))

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_font_fallback_system(self, mock_ffplay):
        """Test font fallback system"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Test that available fonts list is populated
        self.assertIsInstance(player.available_fonts, list)
        self.assertGreater(len(player.available_fonts), 0)

        # Test getting working font
        font = player.get_working_font()
        self.assertIsInstance(font, int)  # OpenCV font constants are integers

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_status_position_top_left(self, mock_ffplay):
        """Test that status is positioned at top-left"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Create a test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Show status
        player.show_status("Top Left Test")

        # Get the result frame
        result = player.draw_status_overlay(test_frame)

        # Check that top-left area has been modified (has non-zero pixels)
        top_left_region = result[0:50, 0:200]  # Top-left corner region
        has_modification = np.any(top_left_region > 0)
        self.assertTrue(has_modification, "Status should appear in top-left region")

        # Check that bottom area is unchanged (should be all zeros)
        bottom_region = result[400:480, 0:640]  # Bottom region
        is_bottom_unchanged = np.all(bottom_region == 0)
        self.assertTrue(is_bottom_unchanged, "Bottom region should be unchanged")


class TestLoggingSystem(unittest.TestCase):
    """Test cases for logging system"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        test_file = self.temp_path / "test.mp4"
        test_file.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_logging_setup(self, mock_ffplay):
        """Test logging system setup"""
        mock_ffplay.return_value = False

        with patch('logging.basicConfig') as mock_config, \
             patch('logging.getLogger') as mock_logger:
            player = VideoPlayer(str(self.temp_path))

            # Verify logging was configured
            mock_config.assert_called_once()
            mock_logger.assert_called_once()
            self.assertIsNotNone(player.logger)

    @patch('pp.VideoPlayer.check_ffplay_available')
    def test_status_calls_logger(self, mock_ffplay):
        """Test that show_status calls logger"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        with patch.object(player.logger, 'info') as mock_log:
            test_message = "Test Log Message"
            player.show_status(test_message)
            mock_log.assert_called_once_with(test_message)


class TestAudioSynchronization(unittest.TestCase):
    """Test cases for audio synchronization features"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        test_file = self.temp_path / "test.mp4"
        test_file.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('pp.subprocess.run')
    def test_ffplay_detection(self, mock_run):
        """Test ffplay availability detection"""
        # Test when ffplay is available
        mock_run.return_value = Mock()
        player = VideoPlayer(str(self.temp_path))
        self.assertTrue(player.audio_available)

        # Test when ffplay is not available
        mock_run.side_effect = FileNotFoundError()
        player2 = VideoPlayer(str(self.temp_path))
        self.assertFalse(player2.audio_available)

    @patch('pp.VideoPlayer.check_ffplay_available')
    @patch('pp.subprocess.Popen')
    def test_audio_speed_filter(self, mock_popen, mock_ffplay):
        """Test that audio filters include speed adjustment"""
        mock_ffplay.return_value = True
        mock_process = Mock()
        mock_popen.return_value = mock_process

        player = VideoPlayer(str(self.temp_path))
        player.playback_speed = 1.5

        video_path = self.temp_path / "test.mp4"
        player.play_audio(video_path, 0)

        # Check that the command includes atempo filter
        args, kwargs = mock_popen.call_args
        cmd = args[0]
        self.assertIn('-af', cmd)

        # Find the filter argument
        af_index = cmd.index('-af')
        filters = cmd[af_index + 1]
        self.assertIn('atempo=1.5', filters)

    @patch('pp.VideoPlayer.check_ffplay_available')
    @patch('pp.subprocess.Popen')
    def test_audio_mute_and_speed_filters(self, mock_popen, mock_ffplay):
        """Test combined audio filters for mute and speed"""
        mock_ffplay.return_value = True
        mock_process = Mock()
        mock_popen.return_value = mock_process

        player = VideoPlayer(str(self.temp_path))
        player.playback_speed = 1.2
        player.is_muted = True

        video_path = self.temp_path / "test.mp4"
        player.play_audio(video_path, 0)

        # Check that the command includes both filters
        args, kwargs = mock_popen.call_args
        cmd = args[0]
        af_index = cmd.index('-af')
        filters = cmd[af_index + 1]

        self.assertIn('volume=0', filters)
        self.assertIn('atempo=1.2', filters)
        self.assertIn(',', filters)  # Should be comma-separated


class TestWindowTitleUpdates(unittest.TestCase):
    """Test cases for window title updates"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        test_file = self.temp_path / "test_video.mp4"
        test_file.touch()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('pp.VideoPlayer.check_ffplay_available')
    @patch('pp.cv2.setWindowTitle')
    def test_window_title_with_speed(self, mock_set_title, mock_ffplay):
        """Test window title includes speed when not 1.0x"""
        mock_ffplay.return_value = False
        player = VideoPlayer(str(self.temp_path))

        # Test normal speed (no speed indicator)
        player.playback_speed = 1.0
        player.update_window_title("test_video.mp4")

        args = mock_set_title.call_args[0]
        title = args[1]
        self.assertNotIn('[', title)  # No speed indicator

        # Test with speed change
        player.playback_speed = 1.5
        player.update_window_title("test_video.mp4")

        args = mock_set_title.call_args[0]
        title = args[1]
        self.assertIn('[1.5x]', title)  # Speed indicator present


if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSpeedControl))
    suite.addTests(loader.loadTestsFromTestCase(TestStatusDisplay))
    suite.addTests(loader.loadTestsFromTestCase(TestLoggingSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAudioSynchronization))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowTitleUpdates))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)