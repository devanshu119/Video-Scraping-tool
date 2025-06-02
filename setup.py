"""
YouTube Playlist to MP3 Downloader - Setup Script
=================================================

This script checks system requirements, validates dependencies, and provides
installation guidance for the YouTube downloader project.

Author: Educational Project
Version: 1.0
License: MIT (Educational Use Only)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple

def print_header():
    """Print setup script header."""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           YouTube Downloader Setup & Installation            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(header)

def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    version = sys.version_info
    required_major, required_minor = 3, 7

    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major == required_major and version.minor >= required_minor:
        print("   ✅ Python version is compatible")
        return True
    else:
        print(f"   ❌ Python {required_major}.{required_minor}+ required")
        return False

def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extract version from output
            lines = result.stdout.split('\n')
            version_line = next((line for line in lines if 'ffmpeg version' in line.lower()), '')
            print(f"🎬 FFmpeg: {version_line.split()[2] if len(version_line.split()) > 2 else 'Installed'}")
            print("   ✅ FFmpeg is installed and accessible")
            return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("🎬 FFmpeg: Not found")
    print("   ❌ FFmpeg is required for audio conversion")
    return False

def check_pip_package(package_name: str) -> Tuple[bool, str]:
    """Check if a pip package is installed."""
    try:
        if package_name == 'beautifulsoup4':
            import bs4
            return True, bs4.__version__
        elif package_name == 'google-api-python-client':
            import googleapiclient
            return True, googleapiclient.__version__
        elif package_name == 'pytubefix':
            import pytubefix
            return True, getattr(pytubefix, '__version__', 'unknown')
        elif package_name == 'yt-dlp':
            import yt_dlp
            return True, yt_dlp.__version__
        elif package_name == 'moviepy':
            import moviepy
            return True, moviepy.__version__
        elif package_name == 'requests':
            import requests
            return True, requests.__version__
        else:
            __import__(package_name)
            return True, 'unknown'
    except ImportError:
        return False, ''

def check_all_dependencies() -> Dict[str, Dict]:
    """Check all required and optional dependencies."""
    dependencies = {
        'core': {
            'name': 'Core Dependencies',
            'packages': ['requests']
        },
        'pytubefix': {
            'name': 'PyTubeFix Implementation',
            'packages': ['pytubefix', 'moviepy']
        },
        'ytdlp': {
            'name': 'yt-dlp Implementation', 
            'packages': ['yt-dlp']
        },
        'optional': {
            'name': 'Optional Features',
            'packages': ['beautifulsoup4', 'google-api-python-client']
        }
    }

    results = {}

    for category, info in dependencies.items():
        print(f"\n📦 {info['name']}:")
        print("   " + "=" * 40)

        category_results = {}
        for package in info['packages']:
            installed, version = check_pip_package(package)
            status = "✅ Installed" if installed else "❌ Missing"
            version_text = f"(v{version})" if installed and version != 'unknown' else ""

            print(f"   {package:<25} {status} {version_text}")
            category_results[package] = {'installed': installed, 'version': version}

        results[category] = category_results

    return results

def get_installation_commands(missing_packages: List[str]) -> Dict[str, List[str]]:
    """Get installation commands for missing packages."""
    commands = {
        'pip': [f"pip install {' '.join(missing_packages)}"],
        'pip3': [f"pip3 install {' '.join(missing_packages)}"],
        'conda': [f"conda install -c conda-forge {' '.join(missing_packages)}"]
    }
    return commands

def print_ffmpeg_installation():
    """Print FFmpeg installation instructions."""
    system = platform.system().lower()

    instructions = {
        'windows': [
            "Download from: https://ffmpeg.org/download.html#build-windows",
            "Or use chocolatey: choco install ffmpeg",
            "Or use winget: winget install Gyan.FFmpeg",
            "Add FFmpeg to your system PATH"
        ],
        'darwin': [  # macOS
            "Using Homebrew: brew install ffmpeg",
            "Using MacPorts: sudo port install ffmpeg"
        ],
        'linux': [
            "Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg",
            "CentOS/RHEL: sudo yum install ffmpeg",
            "Fedora: sudo dnf install ffmpeg",
            "Arch: sudo pacman -S ffmpeg"
        ]
    }

    print("\n🎬 FFmpeg Installation:")
    print("   " + "=" * 30)

    if system in instructions:
        for instruction in instructions[system]:
            print(f"   • {instruction}")
    else:
        print("   • Please visit https://ffmpeg.org/download.html for installation instructions")

    print("\n   💡 After installation, restart your terminal/command prompt")

def print_installation_guide(dependency_results: Dict[str, Dict]):
    """Print installation guide for missing dependencies."""
    all_missing = []
    implementation_status = {}

    # Collect missing packages and check implementation availability
    for category, packages in dependency_results.items():
        missing_in_category = []
        for package, info in packages.items():
            if not info['installed']:
                all_missing.append(package)
                missing_in_category.append(package)

        if category in ['pytubefix', 'ytdlp']:
            implementation_status[category] = len(missing_in_category) == 0

    # Print implementation status
    print("\n🚀 Implementation Availability:")
    print("   " + "=" * 35)

    if implementation_status.get('ytdlp', False):
        print("   ✅ yt-dlp implementation ready")
    else:
        print("   ❌ yt-dlp implementation unavailable")

    if implementation_status.get('pytubefix', False):
        print("   ✅ PyTubeFix implementation ready")
    else:
        print("   ❌ PyTubeFix implementation unavailable")

    if not any(implementation_status.values()):
        print("\n   ⚠️  No implementations are available!")

    # Print installation commands if packages are missing
    if all_missing:
        print("\n💾 Installation Commands:")
        print("   " + "=" * 25)

        commands = get_installation_commands(all_missing)
        for cmd_type, cmd_list in commands.items():
            print(f"\n   Using {cmd_type}:")
            for cmd in cmd_list:
                print(f"     {cmd}")

        # Separate commands for each implementation
        print("\n   📌 Install by implementation:")

        pytubefix_missing = [pkg for pkg in ['pytubefix', 'moviepy'] 
                           if not dependency_results['pytubefix'][pkg]['installed']]
        if pytubefix_missing:
            print(f"     PyTubeFix: pip install {' '.join(pytubefix_missing)}")

        ytdlp_missing = [pkg for pkg in ['yt-dlp'] 
                        if not dependency_results['ytdlp'][pkg]['installed']]
        if ytdlp_missing:
            print(f"     yt-dlp: pip install {' '.join(ytdlp_missing)}")

        optional_missing = [pkg for pkg in ['beautifulsoup4', 'google-api-python-client']
                          if not dependency_results['optional'][pkg]['installed']]
        if optional_missing:
            print(f"     Optional: pip install {' '.join(optional_missing)}")

def create_requirements_files():
    """Create requirements files for easy installation."""
    requirements = {
        'requirements.txt': [
            '# Complete requirements for YouTube Playlist Downloader',
            'requests>=2.25.0',
            'beautifulsoup4>=4.9.0',
            'pytubefix>=6.0.0',
            'moviepy>=1.0.3',
            'yt-dlp>=2023.1.6',
            'google-api-python-client>=2.0.0',
            'pathlib2>=2.3.0; python_version<"3.4"'
        ],
        'requirements_pytubefix.txt': [
            '# Requirements for PyTubeFix implementation',
            'requests>=2.25.0',
            'beautifulsoup4>=4.9.0',
            'pytubefix>=6.0.0',
            'moviepy>=1.0.3',
            'google-api-python-client>=2.0.0'
        ],
        'requirements_ytdlp.txt': [
            '# Requirements for yt-dlp implementation',
            'requests>=2.25.0',
            'yt-dlp>=2023.1.6',
            'google-api-python-client>=2.0.0'
        ]
    }

    print("\n📝 Creating requirements files...")

    for filename, content in requirements.items():
        try:
            with open(filename, 'w') as f:
                f.write('\n'.join(content) + '\n')
            print(f"   ✅ Created {filename}")
        except Exception as e:
            print(f"   ❌ Failed to create {filename}: {e}")

def test_imports():
    """Test if critical modules can be imported."""
    print("\n🧪 Testing imports...")
    print("   " + "=" * 20)

    test_modules = [
        ('requests', 'requests'),
        ('PyTubeFix', 'pytubefix'),
        ('MoviePy', 'moviepy.editor'),
        ('yt-dlp', 'yt_dlp'),
        ('BeautifulSoup', 'bs4'),
        ('Google API Client', 'googleapiclient.discovery')
    ]

    for name, module in test_modules:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")

def run_setup_wizard():
    """Run interactive setup wizard."""
    print("\n🧙 Setup Wizard")
    print("   " + "=" * 15)

    print("\n   This wizard will guide you through the setup process.")

    # Check what user wants to install
    print("\n   Which implementation would you like to set up?")
    print("     1. yt-dlp (Recommended)")
    print("     2. PyTubeFix")
    print("     3. Both")

    choice = input("\n   Choose (1-3): ").strip()

    packages_to_install = ['requests']  # Core dependency

    if choice == '1':
        packages_to_install.extend(['yt-dlp'])
        print("\n   📌 Selected: yt-dlp implementation")
    elif choice == '2':
        packages_to_install.extend(['pytubefix', 'moviepy'])
        print("\n   📌 Selected: PyTubeFix implementation")
    elif choice == '3':
        packages_to_install.extend(['yt-dlp', 'pytubefix', 'moviepy'])
        print("\n   📌 Selected: Both implementations")
    else:
        print("\n   ❌ Invalid choice. Exiting wizard.")
        return

    # Optional packages
    install_optional = input("\n   Install optional packages (API client, web scraping)? (y/N): ").strip().lower()
    if install_optional in ['y', 'yes']:
        packages_to_install.extend(['beautifulsoup4', 'google-api-python-client'])

    # Show installation command
    install_cmd = f"pip install {' '.join(packages_to_install)}"
    print(f"\n   💾 Installation command:")
    print(f"      {install_cmd}")

    # Ask if user wants to run it
    auto_install = input("\n   Run installation now? (y/N): ").strip().lower()
    if auto_install in ['y', 'yes']:
        print("\n   🚀 Installing packages...")
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install'] + packages_to_install,
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Installation completed successfully!")
            else:
                print(f"   ❌ Installation failed: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Installation error: {e}")
    else:
        print("\n   📋 Run the installation command manually when ready.")

def main():
    """Main setup function."""
    print_header()

    print("🔍 System Requirements Check")
    print("=" * 40)

    # Check Python version
    python_ok = check_python_version()

    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()

    # Check dependencies
    dependency_results = check_all_dependencies()

    # Print installation guide
    print_installation_guide(dependency_results)

    # Print FFmpeg installation if needed
    if not ffmpeg_ok:
        print_ffmpeg_installation()

    # Create requirements files
    create_requirements_files()

    # Test imports
    test_imports()

    # Offer setup wizard
    if not python_ok:
        print("\n❌ Cannot proceed without compatible Python version.")
        return

    run_wizard = input("\n🧙 Run setup wizard? (y/N): ").strip().lower()
    if run_wizard in ['y', 'yes']:
        run_setup_wizard()

    # Final summary
    print("\n📋 Setup Summary:")
    print("   " + "=" * 20)

    if python_ok:
        print("   ✅ Python version compatible")
    else:
        print("   ❌ Python needs upgrade")

    if ffmpeg_ok:
        print("   ✅ FFmpeg available")
    else:
        print("   ❌ FFmpeg needs installation")

    # Check if any implementation is ready
    ytdlp_ready = dependency_results['ytdlp']['yt-dlp']['installed']
    pytubefix_ready = (dependency_results['pytubefix']['pytubefix']['installed'] and 
                      dependency_results['pytubefix']['moviepy']['installed'])

    if ytdlp_ready or pytubefix_ready:
        print("   ✅ At least one implementation ready")
        print("\n🚀 You can now run: python main_launcher.py")
    else:
        print("   ❌ No implementations ready")
        print("\n💡 Install dependencies first, then run: python main_launcher.py")

    print("\n📚 Project files:")
    project_files = [
        'main_launcher.py',
        'youtube_downloader_pytubefix.py', 
        'youtube_downloader_ytdlp.py',
        'examples.py',
        'requirements.txt'
    ]

    for file in project_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")

if __name__ == "__main__":
    main()
