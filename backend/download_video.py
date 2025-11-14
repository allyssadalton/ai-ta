"""
import os
import subprocess

def download_YT_Video(course, videoURL):
    video_info = json.loads(result.stdout)
    title = video_info.get("title")
    output_path = os.path.join(course, "video.mp4")

subprocess.run([
    "yt-dlp",
    "--cookies", "cookies.txt",
    #"--cookies-from-browser", "chrome",  for ui maybe?
    video_url,
    "-o", output_path
], check=True)

# Verify download
if os.path.exists(output_path):
    file_size_mb = os.path.getsize(output_path) / (1024*1024)
    print(f"Download successful: {output_path} ({file_size_mb:.2f} MB)")
else:
    print("Download failed.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_video.py <courseid> <youtube_video_url> <slides_link (optional)>")
        sys.exit(1)
    vid = sys.argv[2]
    course = sys.argv[1]
    ingest_video(course, vid) 
"""
import os
import subprocess
import json
import re
import sys

def download_YT_Video(course, video_url, cookies_file="cookies.txt"):
    # Make sure course folder exists
    os.makedirs(course, exist_ok=True)

    # Step 1: Get video metadata
    result = subprocess.run(
        [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "--skip-download",
            "-J",
            video_url
        ],
        capture_output=True,
        text=True,
        check=True
    )

    video_info = json.loads(result.stdout)
    title = video_info.get("title", "Unknown_Title")

    # Step 2: Make title safe for filesystem
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)

    # Step 3: Build output path
    output_path = os.path.join(course, f"{safe_title}.mp4")

    # Step 4: Download video
    subprocess.run(
        [
            "yt-dlp",
            "--cookies", cookies_file,
            video_url,
            "-o", output_path
        ],
        check=True
    )

    # Step 5: Verify download
    if os.path.exists(output_path):
        file_size_mb = os.path.getsize(output_path) / (1024*1024)
        print(f"Download successful: {output_path} ({file_size_mb:.2f} MB)")
    else:
        print("Download failed.")

# --------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_video.py <course_folder> <youtube_video_url>")
        sys.exit(1)

    course = sys.argv[1]
    vid_url = sys.argv[2]

    download_YT_Video(course, vid_url)