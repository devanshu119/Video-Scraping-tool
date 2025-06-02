# YouTube Playlist to MP3 Downloader

A comprehensive educational project that demonstrates how to download YouTube playlists and convert them to MP3 format using multiple implementation approaches.

## ⚖️ Legal Notice

**IMPORTANT: This tool is intended for educational purposes only.**

By using this software, you acknowledge and agree that:

- You will respect YouTube's Terms of Service
- You will only download content you have permission to use
- You understand that downloading copyrighted material without permission may violate copyright laws
- The developers are not responsible for any misuse of this tool
- You will consider YouTube Premium for legal offline viewing

## 🚀 Features

### Two Robust Implementations

1. **PyTubeFix Implementation**
   - Uses PyTubeFix library (fork of original PyTube)
   - Audio conversion with MoviePy
   - Good for learning and customization
   - Web scraping fallback for playlist parsing

2. **yt-dlp Implementation** (Recommended)
   - Uses yt-dlp library (most robust option)
   - Built-in audio processing with FFmpeg
   - Better error handling and resilience
   - Regular updates for YouTube compatibility
   - Multiple download modes (standard, bulk, metadata)

### Key Features

- ✅ Download single videos or entire playlists
- ✅ Convert to high-quality MP3 (320kbps)
- ✅ YouTube Data API integration (optional)
- ✅ Progress tracking and error handling
- ✅ Automatic filename sanitization
- ✅ Skip already downloaded files
- ✅ Comprehensive logging
- ✅ Interactive launcher with dependency checking
- ✅ Multiple quality options and metadata extraction

## 📦 Installation

### Prerequisites

- **Python 3.7 or higher**
- **FFmpeg** (required for audio conversion)

### Quick Setup

1. **Clone or download the project files:**
   ```bash
   # Download all project files to a directory
   ```

2. **Run the setup script:**
   ```bash
   python setup.py
   ```
   This will check dependencies and guide you through installation.

3. **Install dependencies:**
   
   **For yt-dlp implementation (recommended):**
   ```bash
   pip install -r requirements_ytdlp.txt
   ```
   
   **For PyTubeFix implementation:**
   ```bash
   pip install -r requirements_pytubefix.txt
   ```
   
   **For both implementations:**
   ```bash
   pip install -r requirements.txt
   ```

### FFmpeg Installation

**Windows:**
```bash
# Using chocolatey
choco install ffmpeg

# Using winget
winget install Gyan.FFmpeg

# Or download from: https://ffmpeg.org/download.html#build-windows
```

**macOS:**
```bash
# Using Homebrew
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

## 🎯 Quick Start

### Using the Interactive Launcher

```bash
python main_launcher.py
```

The launcher will:
- Check dependencies
- Let you choose between implementations
- Guide you through configuration
- Start the download process

### Direct Usage

**yt-dlp Implementation:**
```python
from youtube_downloader_ytdlp import YouTubePlaylistDownloaderYTDLP

downloader = YouTubePlaylistDownloaderYTDLP(output_dir="my_music")

# Download a playlist
stats = downloader.download_playlist("https://www.youtube.com/playlist?list=...")

# Download a single video
success = downloader.download_single_video("https://www.youtube.com/watch?v=...")
```

**PyTubeFix Implementation:**
```python
from youtube_downloader_pytubefix import YouTubePlaylistDownloader

downloader = YouTubePlaylistDownloader(output_dir="my_music")

# Download a playlist
stats = downloader.download_playlist("https://www.youtube.com/playlist?list=...")

# Download a single video
success = downloader.download_single_video("https://www.youtube.com/watch?v=...")
```

## 📚 Examples

Run the examples to see different usage scenarios:

```bash
python examples.py
```

Available examples:
- Single video download
- Playlist download
- Custom progress tracking
- YouTube Data API integration
- Bulk download with concurrency
- Enhanced metadata extraction
- Error handling demonstrations

## 🔧 Advanced Usage

### YouTube Data API Integration

1. Get an API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Use the API key with the downloader:

```python
downloader = YouTubePlaylistDownloader(api_key="YOUR_API_KEY")
```

### Custom Progress Tracking

```python
def my_progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d.get('_percent_str', 'N/A')}")
    elif d['status'] == 'finished':
        print(f"Downloaded: {d['filename']}")

downloader.ydl_opts['progress_hooks'] = [my_progress_hook]
```

### Bulk Download with yt-dlp

```python
downloader = YouTubePlaylistDownloaderYTDLP()
stats = downloader.download_playlist_bulk(playlist_url, max_concurrent=5)
```

### Download with Enhanced Metadata

```python
stats = downloader.download_with_metadata(url, include_thumbnails=True)
```

## 📁 Project Structure

```
youtube-playlist-downloader/
├── main_launcher.py                  # Interactive launcher
├── youtube_downloader_pytubefix.py   # PyTubeFix implementation
├── youtube_downloader_ytdlp.py       # yt-dlp implementation
├── setup.py                          # Setup and dependency checker
├── examples.py                       # Usage examples
├── requirements.txt                  # Complete dependencies
├── requirements_pytubefix.txt        # PyTubeFix-specific
├── requirements_ytdlp.txt            # yt-dlp-specific
├── downloads/                        # Default output directory
└── README.md                         # This file
```

## 🔍 Implementation Comparison

| Feature | PyTubeFix | yt-dlp |
|---------|-----------|--------|
| **Reliability** | Good | Excellent |
| **Speed** | Moderate | Fast |
| **Error Handling** | Basic | Advanced |
| **YouTube Compatibility** | Occasional issues | Very robust |
| **Audio Quality** | 320kbps MP3 | Multiple formats/quality |
| **Metadata Support** | Basic | Comprehensive |
| **Concurrent Downloads** | No | Yes |
| **Learning Value** | High | Moderate |
| **Maintenance** | Community fork | Active development |

**Recommendation:** Use yt-dlp for production use, PyTubeFix for learning purposes.

## 🐛 Troubleshooting

### Common Issues

**"No module named 'pytubefix'"**
```bash
pip install pytubefix
```

**"FFmpeg not found"**
- Install FFmpeg and ensure it's in your system PATH
- Run `ffmpeg -version` to verify installation

**"Download failed" errors**
- Check your internet connection
- Verify the URL is accessible
- Try the yt-dlp implementation (more robust)
- Check if the video is private or region-blocked

**"API quota exceeded"**
- YouTube Data API has daily quotas
- Wait for quota reset or remove API key to use scraping

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check log files:
- `youtube_downloader.log` (PyTubeFix)
- `youtube_downloader_ytdlp.log` (yt-dlp)

## 🔄 Updates and Maintenance

### Keeping Dependencies Updated

```bash
# Update yt-dlp (recommended regularly)
pip install --upgrade yt-dlp

# Update all dependencies
pip install --upgrade -r requirements.txt
```

### YouTube Compatibility

YouTube frequently changes its systems. If downloads start failing:

1. Update yt-dlp: `pip install --upgrade yt-dlp`
2. Check for newer versions of PyTubeFix
3. Review project issues and documentation

## 🤝 Contributing

This is an educational project. Contributions that improve the educational value are welcome:

- Bug fixes and error handling improvements
- Better documentation and examples
- Additional educational features
- Code quality improvements

## 📄 License

MIT License (Educational Use Only)

This project is intended for educational purposes. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws.

## 🔗 Related Resources

- [YouTube Terms of Service](https://www.youtube.com/static?template=terms)
- [Copyright and Fair Use](https://support.google.com/youtube/answer/9783148)
- [YouTube Premium](https://www.youtube.com/premium) - Official offline viewing
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp#readme)
- [PyTubeFix Documentation](https://pytubefix.readthedocs.io/)

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. The authors and contributors are not responsible for any misuse or legal consequences resulting from the use of this software. Users must ensure they have proper authorization to download and use any content they obtain through this tool.

Remember: When in doubt about copyright permissions, use YouTube Premium for legal offline viewing of copyrighted content.