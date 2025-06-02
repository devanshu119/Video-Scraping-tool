"""
YouTube Playlist to MP3 Downloader - yt-dlp Implementation
==========================================================

This module provides functionality to download YouTube playlists and convert them to MP3 format
using the yt-dlp library, which is more robust and actively maintained.

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
from typing import List, Dict, Optional, Callable, Any
from urllib.parse import urlparse, parse_qs

# Third-party imports
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    print("yt-dlp not available. Install with: pip install yt-dlp")

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
        logging.FileHandler('youtube_downloader_ytdlp.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class YouTubePlaylistDownloaderYTDLP:
    """
    A comprehensive YouTube playlist downloader using yt-dlp.

    Features:
    - Direct playlist processing with yt-dlp
    - Built-in audio extraction and MP3 conversion
    - Advanced error handling and retry mechanisms
    - Progress tracking and rate limiting
    - Support for various quality options
    - Robust against YouTube changes
    """

    def __init__(self, output_dir: str = "downloads", api_key: Optional[str] = None, quality: str = "320"):
        """
        Initialize the YouTube downloader.

        Args:
            output_dir: Directory to save downloaded MP3 files
            api_key: Optional YouTube Data API key (not used by yt-dlp but kept for compatibility)
            quality: Audio quality in kbps (default: 320)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.api_key = api_key
        self.quality = quality

        # Statistics
        self.stats = {
            'total_videos': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'skipped_videos': 0
        }

        # yt-dlp configuration
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': self.quality,
            'outtmpl': str(self.output_dir / '%(playlist_index)03d_%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'no_warnings': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            }],
            'postprocessor_args': [
                '-ar', '44100',  # Sample rate
                '-ac', '2',      # Stereo
            ],
        }

    def validate_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        if not YTDLP_AVAILABLE:
            logger.error("yt-dlp is required but not installed")
            return False
        return True

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200] + "..."

        return sanitized

    def progress_hook(self, d):
        """Progress hook for yt-dlp downloads."""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
            elif 'total_bytes_estimate' in d:
                percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                print(f"\rDownloading: ~{percent:.1f}%", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\nDownload completed: {d['filename']}")
        elif d['status'] == 'error':
            print(f"\nDownload error: {d.get('error', 'Unknown error')}")

    def get_playlist_info(self, playlist_url: str) -> Dict[str, Any]:
        """
        Get playlist information using yt-dlp.

        Args:
            playlist_url: YouTube playlist URL

        Returns:
            Dictionary with playlist information
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                return info
        except Exception as e:
            logger.error(f"Failed to get playlist info: {e}")
            return {}

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

        # Configure yt-dlp options for this download
        opts = self.ydl_opts.copy()
        if progress_callback:
            opts['progress_hooks'] = [progress_callback]
        else:
            opts['progress_hooks'] = [self.progress_hook]

        try:
            # First, get playlist info to count videos
            playlist_info = self.get_playlist_info(playlist_url)
            if playlist_info and 'entries' in playlist_info:
                self.stats['total_videos'] = len([e for e in playlist_info['entries'] if e])
                logger.info(f"Found {self.stats['total_videos']} videos in playlist")

            # Download the playlist
            with yt_dlp.YoutubeDL(opts) as ydl:
                try:
                    ydl.download([playlist_url])

                    # Count successful downloads by checking output directory
                    mp3_files = list(self.output_dir.glob("*.mp3"))
                    self.stats['successful_downloads'] = len(mp3_files)

                    if self.stats['total_videos'] > 0:
                        self.stats['failed_downloads'] = self.stats['total_videos'] - self.stats['successful_downloads']

                    logger.info(f"Download process completed")

                except Exception as e:
                    logger.error(f"Download failed: {e}")
                    self.stats['failed_downloads'] = self.stats['total_videos']

        except Exception as e:
            logger.error(f"Failed to process playlist: {e}")
            self.stats['failed_downloads'] = self.stats.get('total_videos', 1)

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
            # Configure options for single video
            opts = self.ydl_opts.copy()

            if custom_filename:
                sanitized_name = self.sanitize_filename(custom_filename)
                if not sanitized_name.endswith('.mp3'):
                    sanitized_name += '.mp3'
                opts['outtmpl'] = str(self.output_dir / sanitized_name.replace('.mp3', '.%(ext)s'))
            else:
                opts['outtmpl'] = str(self.output_dir / '%(title)s.%(ext)s')

            opts['progress_hooks'] = [self.progress_hook]

            logger.info(f"Downloading single video: {video_url}")

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])

            self.stats['successful_downloads'] += 1
            self.stats['total_videos'] += 1

            logger.info("Single video download completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to download single video: {e}")
            self.stats['failed_downloads'] += 1
            self.stats['total_videos'] += 1
            return False

    def download_playlist_bulk(self, playlist_url: str, max_concurrent: int = 3) -> Dict:
        """
        Download playlist with enhanced options for bulk downloads.

        Args:
            playlist_url: YouTube playlist URL
            max_concurrent: Maximum concurrent downloads

        Returns:
            Dictionary with download statistics
        """
        if not self.validate_dependencies():
            return self.stats

        logger.info(f"Starting bulk playlist download: {playlist_url}")

        # Enhanced options for bulk downloads
        opts = self.ydl_opts.copy()
        opts.update({
            'concurrent_fragment_downloads': max_concurrent,
            'retries': 3,
            'file_access_retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
            'writeinfojson': True,  # Save metadata
            'writethumbnail': False,  # Don't download thumbnails
            'progress_hooks': [self.progress_hook],
        })

        try:
            # Get playlist info first
            playlist_info = self.get_playlist_info(playlist_url)
            if playlist_info and 'entries' in playlist_info:
                valid_entries = [e for e in playlist_info['entries'] if e]
                self.stats['total_videos'] = len(valid_entries)
                logger.info(f"Found {self.stats['total_videos']} valid videos in playlist")

                # Log playlist title if available
                if 'title' in playlist_info:
                    logger.info(f"Playlist title: {playlist_info['title']}")

            # Download with enhanced options
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([playlist_url])

            # Count results
            mp3_files = list(self.output_dir.glob("*.mp3"))
            self.stats['successful_downloads'] = len(mp3_files)

            if self.stats['total_videos'] > 0:
                self.stats['failed_downloads'] = self.stats['total_videos'] - self.stats['successful_downloads']

            logger.info(f"Bulk download complete. Stats: {self.stats}")

        except Exception as e:
            logger.error(f"Bulk download failed: {e}")
            self.stats['failed_downloads'] = self.stats.get('total_videos', 0)

        return self.stats

    def download_with_metadata(self, url: str, include_thumbnails: bool = False) -> Dict:
        """
        Download with enhanced metadata extraction.

        Args:
            url: YouTube playlist or video URL
            include_thumbnails: Whether to download thumbnails

        Returns:
            Dictionary with download statistics
        """
        if not self.validate_dependencies():
            return self.stats

        logger.info(f"Starting download with metadata: {url}")

        # Enhanced options for metadata
        opts = self.ydl_opts.copy()
        opts.update({
            'writeinfojson': True,
            'writeautomaticsub': True,  # Download auto-generated subtitles
            'writesubtitles': True,     # Download manual subtitles
            'writethumbnail': include_thumbnails,
            'embedsubs': False,         # Don't embed subs in audio
            'progress_hooks': [self.progress_hook],
        })

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                if 'list=' in url:
                    # Playlist
                    playlist_info = self.get_playlist_info(url)
                    if playlist_info and 'entries' in playlist_info:
                        self.stats['total_videos'] = len([e for e in playlist_info['entries'] if e])

                    ydl.download([url])
                else:
                    # Single video
                    self.stats['total_videos'] = 1
                    ydl.download([url])

            # Count results
            mp3_files = list(self.output_dir.glob("*.mp3"))
            self.stats['successful_downloads'] = len(mp3_files)
            self.stats['failed_downloads'] = self.stats['total_videos'] - self.stats['successful_downloads']

        except Exception as e:
            logger.error(f"Download with metadata failed: {e}")
            self.stats['failed_downloads'] = self.stats.get('total_videos', 1)

        return self.stats


def main():
    """Example usage of the YouTube Playlist Downloader (yt-dlp)."""
    print("YouTube Playlist to MP3 Downloader (yt-dlp)")
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
    quality = input("Enter audio quality in kbps (default: 320): ").strip() or "320"

    # Download mode selection
    print("\nSelect download mode:")
    print("1. Standard download")
    print("2. Bulk download (faster for large playlists)")
    print("3. Download with metadata (includes subtitles)")
    mode = input("Choose mode (1-3, default: 1): ").strip() or "1"

    # Initialize downloader
    downloader = YouTubePlaylistDownloaderYTDLP(output_dir=output_dir, quality=quality)

    try:
        if mode == "2":
            # Bulk download mode
            max_concurrent = int(input("Max concurrent downloads (default: 3): ").strip() or "3")
            stats = downloader.download_playlist_bulk(url, max_concurrent)
        elif mode == "3":
            # Metadata download mode
            include_thumbs = input("Download thumbnails? (y/N): ").strip().lower() == 'y'
            stats = downloader.download_with_metadata(url, include_thumbs)
        else:
            # Standard download mode
            if 'list=' in url:
                stats = downloader.download_playlist(url)
            else:
                custom_name = input("Custom filename (optional): ").strip() or None
                success = downloader.download_single_video(url, custom_name)
                print(f"\nDownload {'successful' if success else 'failed'}")
                return

        # Print results for playlist downloads
        print(f"\nDownload Summary:")
        print(f"Total videos: {stats['total_videos']}")
        print(f"Successful: {stats['successful_downloads']}")
        print(f"Failed: {stats['failed_downloads']}")
        print(f"Skipped: {stats['skipped_videos']}")

    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
