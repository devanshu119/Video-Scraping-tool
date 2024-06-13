# Video-Scraping-tool
This code is a Python script that automates the process of downloading audio files from YouTube videos in a playlist.
import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os


def scrape_playlist(url):
    try:
        response = requests.get(url, verify=True)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching playlist URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    songs = []
    for item in soup.find_all('a', {'dir': 'auto'}):
        song_name = item.get_text().strip()
        if song_name:  # Skipping empty entries
            songs.append(song_name)
    return songs


def search_youtube(query, api_key):
    try:
        search_url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&q={query}&part=snippet&type=video"
        response = requests.get(search_url, verify=True)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error searching for '{query}' on YouTube: {e}")
        return None

    json_data = response.json()
    if 'items' in json_data and len(json_data['items']) > 0:
        video_id = json_data['items'][0]['id']['videoId']
        return video_id
    else:
        print(f"No results found for '{query}' on YouTube")
        return None


def download_audio(video_id, output_file):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream:
            audio_stream.download(output_file=output_file)
        else:
            print(f"No audio stream found for video ID {video_id}")
    except Exception as e:
        print(f"Error downloading audio for video ID {video_id}: {e}")


def separate_audio(mp4_file, mp3_file):
    try:
        video = VideoFileClip(mp4_file)
        video.audio.write_audiofile(mp3_file)
        video.close()  # Close the video file
        os.remove(mp4_file)  # Delete the MP4 file
    except Exception as e:
        print(f"Error separating audio from {mp4_file}: {e}")


def main():
    playlist_url = "YOUR_PLAYLIST_URL_HERE"
    api_key = "YOUR_YOUTUBE_API_KEY_HERE"

    songs = scrape_playlist(playlist_url)

    for song in songs:
        print(f"Searching for '{song}' on YouTube...")
        video_id = search_youtube(song, api_key)
        if video_id:
            print(f"Downloading audio for '{song}'...")
            mp4_file = f"temp_{song}.mp4"
            download_audio(video_id, mp4_file)
            mp3_file = f"{song}.mp3"
            print(f"Separating audio from '{song}'...")
            separate_audio(mp4_file, mp3_file)
            print(f"Audio for '{song}' has been downloaded and separated successfully!")

if __name__ == "__main__":
    main()
