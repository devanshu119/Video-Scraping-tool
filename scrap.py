import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from moviepy.editor import VideoFileClip

# Function to scrape songs from a playlist URL using BeautifulSoup
def scrape_playlist(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    songs = []
    for item in soup.find_all('a', {'dir': 'auto'}):
        song_name = item.get_text().strip()
        if song_name:  # Skipping empty entries
            songs.append(song_name)
    return songs

# Function to search for a song on YouTube using its title and return the video ID
def search_youtube(query):
    # Use YouTube Data API to search for the query
    # Insert your YouTube Data API key below
    api_key = "YOUR_YOUTUBE_API_KEY"
    search_url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&q={query}&part=snippet&type=video"
    response = requests.get(search_url)
    json_data = response.json()
    video_id = json_data['items'][0]['id']['videoId']
    return video_id

# Function to download audio from a YouTube video using its video ID
def download_audio(video_id):
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(filename='temp')

# Function to separate audio from an MP4 file and delete the MP4
def separate_audio(mp4_file):
    video = VideoFileClip(mp4_file)
    audio_file = mp4_file.replace('.mp4', '.mp3')
    video.audio.write_audiofile(audio_file)
    video.close()  # Close the video file
    # Delete the MP4 file
    import os
    os.remove(mp4_file)

# Main function
def main():
    playlist_url = "YOUR_PLAYLIST_URL_HERE"
    songs = scrape_playlist(playlist_url)

    for song in songs:
        print(f"Searching for '{song}' on YouTube...")
        video_id = search_youtube(song)
        print(f"Downloading audio for '{song}'...")
        download_audio(video_id)
        mp4_file = 'temp.mp4'
        print(f"Separating audio from '{song}'...")
        separate_audio(mp4_file)
        print(f"Audio for '{song}' has been downloaded and separated successfully!")

if __name__ == "__main__":
    main()
