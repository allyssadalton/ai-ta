#qa2.py
import os
import sys
import google.generativeai as genai
#from indexer import load_existing_index
from keys import GOOGLE_API_KEY
from indexer import load_existing_index, FaissStore

# Configure Gemini client
genai.configure(api_key=GOOGLE_API_KEY)

# store = load_existing_index()
'''

def ask_ai_ta(question, course, top_k=5):
    # Retrieve top relevant chunks
    results = store.search(question, top_k=top_k)
    if not results:
        return "I couldn't find relevant information in the lectures."
    context_list = []
    # Combine retrieved context
    for r in results:
        context_list.append(f"{r['start_time']} {r['text']} https://www.youtube.com/watch?v={r['video_id']}")
    
    context = "\n\n".join(context_list)
    # Construct prompt
    prompt = f"""
    You are an AI Teaching Assistant. 
    Use the lecture transcript excerpts below to answer the student's question. 
    Always include the timestamp exactly as it appears at the start of the transcript line if you are citing a video.
    
    If unsure, say you don't know. 
    Context: {context} 
    Question: {question}

    Format your answer like this:
    Your answer text here.

    [(timestamp / 60):(timestamp % 60] Your answer text here.

    Include the video link from which this context was pulled.
    """

    # Send to Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")  # or "gemini-1.5-pro"
    response = model.generate_content(prompt)

    return response.text.strip() if response.text else "No response from model."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python qa2.py <course_num>")
    course = sys.argv[1]
    print("Welcome to your Gemini AI TA! (type 'quit' to exit)\n")
    while True:
        q = input("Ask a question: ")
        if q.lower() in {"quit", "exit"}:
            break
        print("\nAI TA:", ask_ai_ta(q, course))
        print("\n" + "-"*50 + "\n")
'''

def ask_ai_ta(question, course, top_k=5):
    # Retrieve top relevant chunks from both videos and slides
    store = FaissStore(course_id=course[0:7])
    results = store.search(question, top_k=top_k)
    if not results:
        return "I couldn't find relevant information in the lectures or slides."

    context_list = []

    for r in results:
        if r.get("type") == "pdf":
            # Format slide references
            ref = f"(Pages {r.get('page_start', '?')}–{r.get('page_end', '?')}) {r['text']} [Slide Deck: {r.get('pdf_id', '')}]"
        else:
            # Format video references
            start_time = r.get('start_time', 0)
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            video_link = f"https://www.youtube.com/watch?v={r.get('video_id', '')}"
            ref = f"[{minutes:02d}:{seconds:02d}] {r['text']} ({video_link})"
        context_list.append(ref)

    # Combine retrieved context into one block
    context = "\n\n".join(context_list)

    # Build the AI prompt
    prompt = f"""
        You are an AI Teaching Assistant for the course {course}.
        Use the lecture transcript and slide excerpts below to answer the student's question.

        If citing video content, include the timestamp as shown.
        If citing slides, include the name.
        If you’re unsure, say you don’t know.

        Context:
        {context}

        Question: {question}

        Format your answer like this:

        Your answer text here.

        (Video) [mm:ss] Supporting quote...
        Include the video link from which this context was pulled.

        (Slides) Supporting quote...
        Include the slides name from which this context was pulled.
        """

    # Send to Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    response = model.generate_content(prompt)

    return response.text.strip() if response.text else "No response from model."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python qa2.py <course_id>")
        sys.exit(1)

    course = sys.argv[1]
    print(f"Welcome to Ask Allyssa — your AI TA for {course}!\n(Type 'quit' to exit)\n")

    while True:
        q = input("Ask a question: ")
        if q.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        print("\nAI TA:\n")
        print(ask_ai_ta(q, course))
        print("\n" + "-" * 60 + "\n")
