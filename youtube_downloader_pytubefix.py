"""
YouTube Playlist to MP3 Downloader - PyTubeFix Implementation
==============================================================

This module provides functionality to download YouTube playlists and convert them to MP3 format
using the PyTubeFix library and MoviePy for audio conversion.

Legal Notice:
This tool is intended for educational purposes only. Please respect YouTube's Terms of Service
and copyright laws. Only download content you have permission to use.

Author: Educational Project
Version: 1.0
License: MIT (Educational Use Only)
"""

import os
import re
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
from urllib.parse import urlparse, parse_qs

# Third-party imports
try:
    from pytubefix import YouTube, Playlist
    from pytubefix.cli import on_progress
    PYTUBEFIX_AVAILABLE = True
except ImportError:
    PYTUBEFIX_AVAILABLE = False
    print("PyTubeFix not available. Install with: pip install pytubefix")

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("MoviePy not available. Install with: pip install moviepy")

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Web scraping libraries not available. Install with: pip install requests beautifulsoup4")

try:
    from googleapiclient.discovery import build
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("YouTube API client not available. Install with: pip install google-api-python-client")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_downloader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class YouTubePlaylistDownloader:
    """
    A comprehensive YouTube playlist downloader using PyTubeFix.

    Features:
    - Playlist scraping with BeautifulSoup fallback
    - YouTube Data API integration (optional)
    - Individual video downloading with PyTubeFix
    - Audio extraction and MP3 conversion with MoviePy
    - Progress tracking and error handling
    - Automatic cleanup of temporary files
    """

    def __init__(self, output_dir: str = "downloads", api_key: Optional[str] = None):
        """
        Initialize the YouTube downloader.

        Args:
            output_dir: Directory to save downloaded MP3 files
            api_key: Optional YouTube Data API key for enhanced functionality
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.api_key = api_key
        self.youtube_service = None

        # Initialize YouTube API service if key provided
        if self.api_key and API_AVAILABLE:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("YouTube Data API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube API: {e}")

        # Statistics
        self.stats = {
            'total_videos': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'skipped_videos': 0
        }

    def validate_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        if not PYTUBEFIX_AVAILABLE:
            logger.error("PyTubeFix is required but not installed")
            return False
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy is required but not installed")
            return False
        return True

    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from YouTube URL."""
        try:
            parsed_url = urlparse(url)
            if 'list' in parse_qs(parsed_url.query):
                return parse_qs(parsed_url.query)['list'][0]
            return None
        except Exception as e:
            logger.error(f"Failed to extract playlist ID: {e}")
            return None

    def get_playlist_videos_pytubefix(self, playlist_url: str) -> List[Dict]:
        """
        Get playlist videos using PyTubeFix directly.

        Args:
            playlist_url: Full YouTube playlist URL

        Returns:
            List of video information dictionaries
        """
        videos = []
        try:
            playlist = Playlist(playlist_url)

            for video in playlist.videos:
                video_info = {
                    'video_id': video.video_id,
                    'title': video.title,
                    'url': video.watch_url
                }
                videos.append(video_info)

        except Exception as e:
            logger.error(f"PyTubeFix playlist parsing failed: {e}")

        return videos

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200] + "..."

        return sanitized

    def download_video_audio(self, video_url: str, output_path: str, 
                           progress_callback: Optional[Callable] = None) -> bool:
        """
        Download video and extract audio to MP3.

        Args:
            video_url: YouTube video URL
            output_path: Path to save the MP3 file
            progress_callback: Optional progress callback function

        Returns:
            True if successful, False otherwise
        """
        temp_video_path = None
        try:
            # Download video using PyTubeFix
            yt = YouTube(video_url, on_progress_callback=progress_callback or on_progress)

            # Get the highest quality audio stream or video with audio
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

            if not stream:
                logger.error(f"No suitable stream found for {video_url}")
                return False

            # Download to temporary location
            temp_video_path = stream.download(output_path=self.output_dir, filename_prefix="temp_")

            # Convert to MP3 using MoviePy
            video_clip = VideoFileClip(temp_video_path)
            audio_clip = video_clip.audio

            # Write MP3 with high quality
            audio_clip.write_audiofile(
                output_path,
                codec='mp3',
                bitrate='320k',
                verbose=False,
                logger=None
            )

            # Cleanup
            audio_clip.close()
            video_clip.close()

            # Remove temporary video file
            if temp_video_path and os.path.exists(temp_video_path):
                os.remove(temp_video_path)

            logger.info(f"Successfully converted to MP3: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download/convert {video_url}: {e}")

            # Cleanup on failure
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except:
                    pass

            return False

    def download_playlist(self, playlist_url: str, 
                         progress_callback: Optional[Callable] = None) -> Dict:
        """
        Download entire playlist and convert to MP3.

        Args:
            playlist_url: YouTube playlist URL
            progress_callback: Optional progress callback function

        Returns:
            Dictionary with download statistics
        """
        if not self.validate_dependencies():
            return self.stats

        logger.info(f"Starting playlist download: {playlist_url}")

        # Extract playlist ID
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            logger.error("Failed to extract playlist ID from URL")
            return self.stats

        # Get video list using PyTubeFix
        videos = self.get_playlist_videos_pytubefix(playlist_url)
        logger.info(f"PyTubeFix method found {len(videos)} videos")

        if not videos:
            logger.error("No videos found in playlist")
            return self.stats

        self.stats['total_videos'] = len(videos)

        # Download each video
        for i, video in enumerate(videos, 1):
            try:
                title = self.sanitize_filename(video['title'])
                output_filename = f"{i:03d}_{title}.mp3"
                output_path = self.output_dir / output_filename

                # Skip if already exists
                if output_path.exists():
                    logger.info(f"Skipping existing file: {output_filename}")
                    self.stats['skipped_videos'] += 1
                    continue

                logger.info(f"Downloading ({i}/{len(videos)}): {title}")

                success = self.download_video_audio(
                    video['url'], 
                    str(output_path), 
                    progress_callback
                )

                if success:
                    self.stats['successful_downloads'] += 1
                else:
                    self.stats['failed_downloads'] += 1

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing video {i}: {e}")
                self.stats['failed_downloads'] += 1

        logger.info(f"Download complete. Stats: {self.stats}")
        return self.stats

    def download_single_video(self, video_url: str, custom_filename: Optional[str] = None) -> bool:
        """
        Download a single video and convert to MP3.

        Args:
            video_url: YouTube video URL
            custom_filename: Optional custom filename for output

        Returns:
            True if successful, False otherwise
        """
        if not self.validate_dependencies():
            return False

        try:
            yt = YouTube(video_url)
            title = custom_filename or self.sanitize_filename(yt.title)

            if not title.endswith('.mp3'):
                title += '.mp3'

            output_path = self.output_dir / title

            logger.info(f"Downloading single video: {title}")

            success = self.download_video_audio(video_url, str(output_path))

            if success:
                self.stats['successful_downloads'] += 1
                self.stats['total_videos'] += 1
            else:
                self.stats['failed_downloads'] += 1
                self.stats['total_videos'] += 1

            return success

        except Exception as e:
            logger.error(f"Failed to download single video: {e}")
            return False


def main():
    """Example usage of the YouTube Playlist Downloader."""
    print("YouTube Playlist to MP3 Downloader (PyTubeFix)")
    print("=" * 50)
    print()
    print("LEGAL NOTICE:")
    print("This tool is for educational purposes only.")
    print("Please respect YouTube's Terms of Service and copyright laws.")
    print("Only download content you have permission to use.")
    print()

    # Get user input
    url = input("Enter YouTube playlist or video URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        return

    output_dir = input("Enter output directory (default: downloads): ").strip() or "downloads"
    api_key = input("Enter YouTube API key (optional, press Enter to skip): ").strip() or None

    # Initialize downloader
    downloader = YouTubePlaylistDownloader(output_dir=output_dir, api_key=api_key)

    # Determine if URL is playlist or single video
    if 'list=' in url:
        # Download playlist
        stats = downloader.download_playlist(url)
        print(f"\nDownload Summary:")
        print(f"Total videos: {stats['total_videos']}")
        print(f"Successful: {stats['successful_downloads']}")
        print(f"Failed: {stats['failed_downloads']}")
        print(f"Skipped: {stats['skipped_videos']}")
    else:
        # Download single video
        success = downloader.download_single_video(url)
        print(f"\nDownload {'successful' if success else 'failed'}")


if __name__ == "__main__":
    main()
