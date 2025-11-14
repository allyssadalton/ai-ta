import sys
from indexer import FaissStore
from chunker import extract_pdf_text, chunk_pdf_text  # make sure you have pdf_chunker.py from earlier


def ingest_slides(course, slides_path):
    print(f"[ingest] processing slideshow: {slides_path}")

    # Step 1: Extract text from PDF
    pages = extract_pdf_text(slides_path)
    if not pages:
        print("[ingest] no text extracted from PDF")
        return

    # Step 2: Chunk text for embedding
    chunks = chunk_pdf_text(pages, max_chars=800, overlap_chars=200)
    print(f"[ingest] created {len(chunks)} chunks from {len(pages)} pages")

    # Step 3: Store in FAISS
    store = FaissStore(course_id=course)
    pdf_id = f"{course}:{slides_path}"  # unique identifier
    added = store.add_pdf_chunks(pdf_id, chunks)

    print(f"[ingest] indexed {added} chunks for slideshow '{slides_path}' in course '{course}'")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ingest_powerpoint.py <courseid> <slideshow_file_path>")
        sys.exit(1)

    course = sys.argv[1]
    slides_path = sys.argv[2]

    ingest_slides(course, slides_path)
