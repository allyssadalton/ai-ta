import sys
import os
from fileMaker import fileCreation
from captions import get_captions_with_timestamps
from chunker import chunk_transcript
from indexer import FaissStore
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled  # <-- import the exception
from keys import GOOGLE_API_KEY

import json
import yt_dlp
from pydub import AudioSegment

from keys import username
from keys import password
import google.generativeai as genai

def ingest_priv_video(course, video_id):
    ydl_opts = {
        'username': username,
        'password': password,
        'cookiefile': 'cookies.txt',
        'outtmpl': '%(id)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
    }

    # Download video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)
        filename = ydl.prepare_filename(info)

    # Extract audio
    video = AudioSegment.from_file(filename)
    audio_file = f"{video_id}_audio.wav"
    audio = video.set_channels(1).set_frame_rate(16000)
    audio.export(audio_file, format="wav")

    # Configure Gemini
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    myfile = genai.upload_file(audio_file)

    print("Generating transcript from Gemini...")
    response = model.generate_content([
        "Return the transcript as a JSON array of objects like "
        "[{\"start\": \"00:00\", \"text\": \"Intro\", \"duration\": \"00:00\"}]",
        myfile
    ])

    # Try parsing JSON, fallback if truncated
    captions = None
    try:
        captions = json.loads(response.text)

        # Ensure it's a list of dicts
        if not isinstance(captions, list) or not all(isinstance(seg, dict) for seg in captions):
            raise ValueError("Transcript not in expected JSON format.")

        # Fill in missing duration/start info if necessary
        for i, seg in enumerate(captions):
            # Convert start to seconds
            start_sec = sum(int(x) * 60 ** j for j, x in enumerate(reversed(seg.get("start", "0:00").split(":"))))
            seg["start"] = start_sec

            # Calculate duration
            if i + 1 < len(captions):
                next_start = sum(int(x) * 60 ** j for j, x in enumerate(reversed(captions[i + 1].get("start", "0:00").split(":"))))
                seg["duration"] = next_start - start_sec
            else:
                seg["duration"] = 5.0  # fallback for last segment

        transcript_text = captions

        print("Transcript parsed successfully, creating file...")
        fileCreation(course, video_id, captions)

    except Exception as e:
        print(f"Transcript JSON invalid or truncated ({e}). Falling back to plain text file.")
        os.makedirs(course, exist_ok=True)
        file_path = os.path.join(course, f"{video_id}.txt")
        with open(file_path, "w") as f:
            f.write(f"http://youtube.com/watch?v={video_id}\n\n")
            f.write(response.text)

        # Wrap in minimal structure so chunk_transcript still works
        transcript_text = [{"start": 0, "text": response.text, "duration": 5}]

    # Chunk transcript safely
    chunks = chunk_transcript(transcript_text, max_chars=800, overlap_chars=200)
    print(f"[ingest] created {len(chunks)} chunks")

    # Store in FAISS
    store = FaissStore(course_id=course)
    added = store.add_chunks(video_id, chunks)
    print(f"[ingest] indexed {added} chunks for video {video_id}")

    # Cleanup
    os.remove(audio_file)
    os.remove(file_path)
    os.remove(filename)  # uncomment if you want to delete the video too


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ingest_one_video.py <courseid> <youtube_video_id>")
        sys.exit(1)
    vid = sys.argv[2]
    course = sys.argv[1]
    ingest_priv_video(course, vid) 