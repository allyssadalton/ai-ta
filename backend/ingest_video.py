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

def ingest_video(course, video_id):
    #Try to get the transcript directly (English or auto-generated English)
    try:
        try:
            api = YouTubeTranscriptApi()
            transcript_data = api.fetch(video_id)
            print(f"Fetched {len(transcript_data)} transcript segments for video {video_id}.")

        except TranscriptsDisabled:
            print(f"Transcripts are disabled for this video ({video_id}).")
            return
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {e}")
            return

        # Optional: Format transcript into timestamped captions
        captions = get_captions_with_timestamps(video_id, transcript_data)

        # Creates file of the transcript with the video id as the name
        fileCreation(course, video_id, captions)
    
    # except incase its an unlisted video
    except:
        ydl_opts = {
            'username': username,
            'password': password,
            'cookiefile': 'cookies.txt',
            'outtmpl': '%(id)s.%(ext)s',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)
            filename = ydl.prepare_filename(info)
        
        # Load video and extract audio
        video = AudioSegment.from_file(filename)
        audio_file = f"{video_id}_audio.wav"
        audio = video.set_channels(1).set_frame_rate(16000)
        audio.export(audio_file, format="wav")

        # Configure Google Gemini client
        genai.configure(api_key=GOOGLE_API_KEY)
        
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Upload and process
        myfile = genai.upload_file(audio_file)
        response = model.generate_content([
                "Return the transcript as a JSON array of objects like "
                "[{\"start\": \"00:00\", \"text\": \"Intro\"}, ...]",
                myfile
            ]
        )
        try: 
            print("trying to create json ")
            captions = json.loads(response.text)
            print("trying to create file with function")
            fileCreation(course, video_id, captions)     
            # transcript_data = captions  
        except Exception as e:
            print("making file manually:", e)
            os.makedirs(course, exist_ok=True)
            file_path = os.path.join(course, f"{video_id}.txt")

            with open(file_path, "x") as file:
                file.write(f"http://youtube.com/watch?v={video_id}\n\n")
                file.write(response.text)

            # fallback — treat entire response as one transcript segment
            captions = [{"start": 0.0, "duration": 0.0, "text": response.text}]
    # Chunk the transcript
    chunks = chunk_transcript(captions, max_chars=800, overlap_chars=200)
    print(f"[ingest] created {len(chunks)} chunks")

    # Store in FAISS
    store = FaissStore(course_id=course)
    added = store.add_chunks(video_id, chunks)
    print(f"[ingest] indexed {added} chunks for video {video_id}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ingest_one_video.py <courseid> <youtube_video_id>")
        sys.exit(1)
    vid = sys.argv[2]
    course = sys.argv[1]
    ingest_video(course, vid) 