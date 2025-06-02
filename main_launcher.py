"""
YouTube Playlist to MP3 Downloader - Interactive Launcher
=========================================================

This script provides an interactive interface to choose between different
YouTube downloading implementations and configure download options.

Legal Notice:
This tool is intended for educational purposes only. Please respect YouTube's Terms of Service
and copyright laws. Only download content you have permission to use.

Author: Educational Project
Version: 1.0
License: MIT (Educational Use Only)
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        YouTube Playlist to MP3 Downloader                   ║
    ║                   Interactive Launcher                       ║
    ║                                                              ║
    ║                    Educational Use Only                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_legal_notice():
    """Print legal notice and disclaimer."""
    notice = """
    ⚖️  IMPORTANT LEGAL NOTICE:

    This tool is provided for educational purposes only. By using this software,
    you acknowledge and agree that:

    • You will respect YouTube's Terms of Service
    • You will only download content you have permission to use
    • You understand that downloading copyrighted material without permission
      may violate copyright laws in your jurisdiction
    • The developers are not responsible for any misuse of this tool
    • You will consider YouTube Premium for legal offline viewing

    Do you understand and agree to these terms? (y/N): """

    response = input(notice).strip().lower()
    if response != 'y' and response != 'yes':
        print("\n❌ You must agree to the terms to continue.")
        sys.exit(1)

def check_dependencies():
    """Check which dependencies are available."""
    dependencies = {
        'pytubefix': False,
        'moviepy': False,
        'yt-dlp': False,
        'requests': False,
        'beautifulsoup4': False,
        'google-api-python-client': False
    }

    try:
        import pytubefix
        dependencies['pytubefix'] = True
    except ImportError:
        pass

    try:
        import moviepy
        dependencies['moviepy'] = True
    except ImportError:
        pass

    try:
        import yt_dlp
        dependencies['yt-dlp'] = True
    except ImportError:
        pass

    try:
        import requests
        dependencies['requests'] = True
    except ImportError:
        pass

    try:
        import bs4
        dependencies['beautifulsoup4'] = True
    except ImportError:
        pass

    try:
        import googleapiclient
        dependencies['google-api-python-client'] = True
    except ImportError:
        pass

    return dependencies

def print_dependency_status(dependencies: Dict[str, bool]):
    """Print the status of dependencies."""
    print("\n📦 Dependency Status:")
    print("=" * 50)

    for dep, available in dependencies.items():
        status = "✅ Installed" if available else "❌ Missing"
        print(f"  {dep:<25} {status}")

    print()

def print_implementation_comparison():
    """Print a comparison of available implementations."""
    comparison = """
    🔍 Implementation Comparison:
    ════════════════════════════════════════════════════════════════

    📌 PyTubeFix Implementation:
       • Uses PyTubeFix library (fork of original PyTube)
       • Audio conversion with MoviePy
       • Good for learning and customization
       • May have occasional compatibility issues
       • Requires: pytubefix, moviepy

    📌 yt-dlp Implementation (Recommended):
       • Uses yt-dlp library (most robust option)
       • Built-in audio processing with FFmpeg
       • Better error handling and resilience
       • Regular updates for YouTube compatibility
       • Faster downloads and better quality options
       • Requires: yt-dlp, FFmpeg

    💡 Recommendation: Use yt-dlp for production use
    """
    print(comparison)

def get_available_implementations(dependencies: Dict[str, bool]) -> Dict[str, bool]:
    """Determine which implementations are available based on dependencies."""
    implementations = {
        'pytubefix': dependencies['pytubefix'] and dependencies['moviepy'],
        'yt-dlp': dependencies['yt-dlp']
    }
    return implementations

def select_implementation(available_implementations: Dict[str, bool]) -> str:
    """Let user select which implementation to use."""
    if not any(available_implementations.values()):
        print("❌ No implementations are available. Please install required dependencies.")
        print("\n💡 Quick installation:")
        print("   For yt-dlp: pip install yt-dlp")
        print("   For PyTubeFix: pip install pytubefix moviepy")
        sys.exit(1)

    print("\n🚀 Select Implementation:")
    print("=" * 30)

    options = []

    if available_implementations['yt-dlp']:
        options.append(('1', 'yt-dlp', '(Recommended - Most reliable)'))
        print("  1. yt-dlp Implementation (Recommended)")

    if available_implementations['pytubefix']:
        options.append(('2', 'pytubefix', '(Educational - Good for learning)'))
        print("  2. PyTubeFix Implementation")

    if len(options) == 1:
        print(f"\n📋 Only one implementation available: {options[0][1]}")
        return options[0][1]

    while True:
        choice = input("\nChoose implementation (1-2): ").strip()
        for option in options:
            if choice == option[0]:
                return option[1]
        print("❌ Invalid choice. Please try again.")

def get_download_configuration() -> Dict[str, Any]:
    """Get download configuration from user."""
    config = {}

    print("\n⚙️  Download Configuration:")
    print("=" * 35)

    # URL input
    config['url'] = input("📎 YouTube URL (playlist or video): ").strip()
    if not config['url']:
        print("❌ URL is required!")
        return get_download_configuration()

    # Output directory
    default_output = "downloads"
    config['output_dir'] = input(f"📁 Output directory (default: {default_output}): ").strip() or default_output

    # Quality settings for yt-dlp
    if 'yt-dlp' in config.get('implementation', ''):
        config['quality'] = input("🎵 Audio quality in kbps (default: 320): ").strip() or "320"

    # YouTube API key (optional)
    config['api_key'] = input("🔑 YouTube API key (optional, press Enter to skip): ").strip() or None

    # Create output directory if it doesn't exist
    Path(config['output_dir']).mkdir(exist_ok=True)

    return config

def run_pytubefix_implementation(config: Dict[str, Any]):
    """Run the PyTubeFix implementation."""
    try:
        from youtube_downloader_pytubefix import YouTubePlaylistDownloader

        print("\n🚀 Starting PyTubeFix downloader...")
        downloader = YouTubePlaylistDownloader(
            output_dir=config['output_dir'],
            api_key=config.get('api_key')
        )

        if 'list=' in config['url']:
            # Playlist download
            print("📋 Detected playlist URL")
            stats = downloader.download_playlist(config['url'])
            print_download_summary(stats)
        else:
            # Single video download
            print("🎥 Detected single video URL")
            success = downloader.download_single_video(config['url'])
            print(f"\n{'✅ Download successful!' if success else '❌ Download failed!'}")

    except ImportError as e:
        print(f"❌ Failed to import PyTubeFix implementation: {e}")
        print("💡 Make sure the youtube_downloader_pytubefix.py file is in the same directory")
    except Exception as e:
        print(f"❌ Error during download: {e}")

def run_ytdlp_implementation(config: Dict[str, Any]):
    """Run the yt-dlp implementation."""
    try:
        from youtube_downloader_ytdlp import YouTubePlaylistDownloaderYTDLP

        print("\n🚀 Starting yt-dlp downloader...")
        downloader = YouTubePlaylistDownloaderYTDLP(
            output_dir=config['output_dir'],
            quality=config.get('quality', '320')
        )

        if 'list=' in config['url']:
            # Playlist download with mode selection
            print("📋 Detected playlist URL")
            print("\nSelect download mode:")
            print("  1. Standard download")
            print("  2. Bulk download (faster)")
            print("  3. Download with metadata")

            mode = input("Choose mode (1-3, default: 1): ").strip() or "1"

            if mode == "2":
                max_concurrent = int(input("Max concurrent downloads (default: 3): ").strip() or "3")
                stats = downloader.download_playlist_bulk(config['url'], max_concurrent)
            elif mode == "3":
                include_thumbs = input("Download thumbnails? (y/N): ").strip().lower() == 'y'
                stats = downloader.download_with_metadata(config['url'], include_thumbs)
            else:
                stats = downloader.download_playlist(config['url'])

            print_download_summary(stats)
        else:
            # Single video download
            print("🎥 Detected single video URL")
            custom_name = input("Custom filename (optional): ").strip() or None
            success = downloader.download_single_video(config['url'], custom_name)
            print(f"\n{'✅ Download successful!' if success else '❌ Download failed!'}")

    except ImportError as e:
        print(f"❌ Failed to import yt-dlp implementation: {e}")
        print("💡 Make sure the youtube_downloader_ytdlp.py file is in the same directory")
    except Exception as e:
        print(f"❌ Error during download: {e}")

def print_download_summary(stats: Dict[str, int]):
    """Print download summary statistics."""
    summary = f"""
    📊 Download Summary:
    ══════════════════════════════════════════════════════════════
    📁 Total videos:      {stats['total_videos']}
    ✅ Successful:        {stats['successful_downloads']}
    ❌ Failed:            {stats['failed_downloads']}
    ⏭️  Skipped:           {stats['skipped_videos']}
    ══════════════════════════════════════════════════════════════
    """
    print(summary)

def main():
    """Main launcher function."""
    try:
        # Clear screen and show banner
        clear_screen()
        print_banner()

        # Show legal notice
        print_legal_notice()

        # Check dependencies
        print("\n🔍 Checking dependencies...")
        dependencies = check_dependencies()
        print_dependency_status(dependencies)

        # Show implementation comparison
        print_implementation_comparison()

        # Get available implementations
        available_implementations = get_available_implementations(dependencies)

        # Select implementation
        implementation = select_implementation(available_implementations)
        print(f"\n✅ Selected: {implementation}")

        # Get download configuration
        config = get_download_configuration()
        config['implementation'] = implementation

        # Confirm configuration
        print("\n📋 Configuration Summary:")
        print("=" * 40)
        print(f"  Implementation: {config['implementation']}")
        print(f"  URL: {config['url']}")
        print(f"  Output directory: {config['output_dir']}")
        if 'quality' in config:
            print(f"  Audio quality: {config['quality']} kbps")
        if config.get('api_key'):
            print(f"  API key: {'*' * 20}")

        confirm = input("\n🚀 Start download? (Y/n): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            start_time = time.time()

            # Run selected implementation
            if implementation == 'pytubefix':
                run_pytubefix_implementation(config)
            elif implementation == 'yt-dlp':
                run_ytdlp_implementation(config)

            elapsed_time = time.time() - start_time
            print(f"\n⏱️  Total time: {elapsed_time:.2f} seconds")
            print(f"📁 Files saved to: {os.path.abspath(config['output_dir'])}")
        else:
            print("❌ Download cancelled.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check the error log for more details.")

if __name__ == "__main__":
    main()
