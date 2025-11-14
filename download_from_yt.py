"""
import ssl
import pytube
ssl._create_default_https_context = ssl._create_unverified_context


from pytube import YouTube
import os

video_url = "https://www.youtube.com/watch?v=twJ7Y5ctLMQ"
yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

# Choose the highest resolution progressive stream (video + audio)
stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()

os.makedirs("video_download", exist_ok=True)
video_path = os.path.join("video_download", "video.mp4")
stream.download(output_path="video_download", filename="video.mp4")

if os.path.exists(video_path):
    print(f"Download successful! File saved at: {video_path}")
"""
import os
import ssl
import certifi
from pytube import YouTube

# ---------- SSL fix for macOS/Homebrew Python ----------
#ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# ---------- YouTube video URL ----------
video_url = "https://www.youtube.com/watch?v=twJ7Y5ctLMQ"

try:
    yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)
except Exception as e:
    print("Error initializing YouTube object:", e)
    exit()

# ---------- Print video metadata ----------
print("Title:", yt.title)
print("Author:", yt.author)
print("Length (seconds):", yt.length)
print("Views:", yt.views)

# ---------- Choose highest resolution progressive stream ----------
try:
    stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
except Exception as e:
    print("Error getting stream:", e)
    exit()

# ---------- Download ----------
os.makedirs("video_download", exist_ok=True)
video_path = os.path.join("video_download", "video.mp4")

try:
    print("Downloading video...")
    stream.download(output_path="video_download", filename="video.mp4")
except Exception as e:
    print("Download failed:", e)
    exit()

# ---------- Verify download ----------
if os.path.exists(video_path):
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"Download successful! File saved at: {video_path}")
    print(f"File size: {file_size_mb:.2f} MB")
else:
    print("Download failed: file does not exist.")
