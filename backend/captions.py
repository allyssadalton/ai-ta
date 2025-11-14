from youtube_transcript_api import YouTubeTranscriptApi

def get_captions_with_timestamps(video_id, languages=['en']):
    try:
        # Ensure it's a valid video ID string
        if not isinstance(video_id, str) or len(video_id) > 20:
            raise ValueError(f"Invalid video_id: {video_id}")

        # Fetch transcript
        transcript_data = YouTubeTranscriptApi().fetch(video_id)

        # Handle both new object-based and old dict-based formats
        captions = []
        for entry in transcript_data:
            if hasattr(entry, "text"):  # new style (objects)
                captions.append({
                    "text": entry.text,
                    "start": entry.start,
                    "duration": entry.duration
                })
            elif isinstance(entry, dict):  # old style (dicts)
                captions.append({
                    "text": entry["text"],
                    "start": entry["start"],
                    "duration": entry["duration"]
                })
            else:
                print(f"[captions] unexpected entry type: {type(entry)}")

        return captions

    except Exception as e:
        print(f"[captions] error processing transcript data: {e}")
        return []

