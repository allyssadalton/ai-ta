# chunker.py
from PyPDF2 import PdfReader
def chunk_transcript(transcript, max_chars=800, overlap_chars=200):
    """
    transcript: list of {'text','start','duration'}
    returns list of {'text','start_time','end_time'}
    """
    if not transcript:
        return []

    chunks = []
    buffer = ""
    buffer_start = None
    last_seg_end = None

    for seg in transcript:
        text = seg.get('text', '').strip()
        start = seg.get('start', 0.0)
        duration = seg.get('duration', 0.0)
        seg_end = start + duration
        if buffer == "":
            buffer_start = start

        if buffer:
            buffer += " " + text
        else:
            buffer = text

        last_seg_end = seg_end

        if len(buffer) >= max_chars:
            chunks.append({
                'text': buffer.strip(),
                'start_time': buffer_start,
                'end_time': seg_end
            })
            # keep last overlap_chars characters
            if overlap_chars > 0:
                buffer = buffer[-overlap_chars:]
                # estimate new buffer_start roughly from the last words — we'll set it to seg_end - small offset
                buffer_start = seg_end - 1.0
            else:
                buffer = ""
                buffer_start = None

    # leftover
    if buffer:
        # end_time as last segment end timestamp
        if last_seg_end is None and transcript:
            last_seg_end = transcript[-1].get('start', 0.0) + transcript[-1].get('duration', 0.0)
        chunks.append({
            'text': buffer.strip(),
            'start_time': buffer_start if buffer_start is not None else 0.0,
            'end_time': last_seg_end if last_seg_end is not None else buffer_start
        })

    return chunks

def extract_pdf_text(pdf_path):
    """Extract text from each page of a PDF."""
    reader = PdfReader(pdf_path)
    text_pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            text_pages.append({
                "page_num": i + 1,
                "text": text.strip()
            })
    return text_pages


def chunk_pdf_text(text_pages, max_chars=800, overlap_chars=200):
    """
    Chunks text from PDF pages.
    Returns [{'text','page_start','page_end'}]
    """
    chunks = []
    buffer = ""
    buffer_start = None
    last_page = None

    for p in text_pages:
        text = p["text"]
        page_num = p["page_num"]

        if buffer == "":
            buffer_start = page_num

        if buffer:
            buffer += " " + text
        else:
            buffer = text

        last_page = page_num

        if len(buffer) >= max_chars:
            chunks.append({
                "text": buffer.strip(),
                "page_start": buffer_start,
                "page_end": page_num
            })
            # Keep overlap
            buffer = buffer[-overlap_chars:] if overlap_chars > 0 else ""
            buffer_start = page_num

    # Add remaining text
    if buffer.strip():
        chunks.append({
            "text": buffer.strip(),
            "page_start": buffer_start or 1,
            "page_end": last_page or buffer_start or 1
        })

    return chunks