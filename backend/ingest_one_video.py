import sys
from fileMaker import fileCreation
from captions import get_captions_with_timestamps
from chunker import chunk_transcript
from indexer import FaissStore
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled  # <-- import the exception

def ingest_video(course, video_id):
    #Try to get the transcript directly (English or auto-generated English)
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
    captions_with_timestamps = get_captions_with_timestamps(video_id, transcript_data)
    
    # Creates file of the transcript with the video id as the name
    fileCreation(course, video_id, captions_with_timestamps)
    # Chunk the transcript
    chunks = chunk_transcript(captions_with_timestamps, max_chars=800, overlap_chars=200)
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