# indexer.py
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import os
from PyPDF2 import PdfReader

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # dim=384

class FaissStore:
    def __init__(self, course_id, dim=384, base_dir="indexes"):
        self.course_id = course_id
        self.dim = dim
        self.model = SentenceTransformer(EMBED_MODEL_NAME)
        
        # Each course gets its own subfolder
        self.course_dir = os.path.join(base_dir, course_id)
        os.makedirs(self.course_dir, exist_ok=True)
        
        self.index_path = os.path.join(self.course_dir, "faiss_index.bin")
        self.meta_path = os.path.join(self.course_dir, "metadata.pkl")
        
        self._ensure_index()
    def _ensure_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            # load existing
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            print("[indexer] loaded existing index with", len(self.metadata), "entries")
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            self.metadata = []
            print("[indexer] created new index")

    def add_chunks(self, video_id, chunks):
        """
        chunks: list of {'text','start_time','end_time'}
        """
        texts = [c['text'] for c in chunks]
        if not texts:
            return 0
        embeddings = self.model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        self.index.add(embeddings)
        for c in chunks:
            self.metadata.append({
                'video_id': video_id,
                'text': c['text'],
                'start_time': c['start_time'],
                'end_time': c['end_time']
            })
        self.save()
        return len(chunks)

    def add_pdf_chunks(self, pdf_id, chunks):
        """
        chunks: list of {'text','page_start','page_end'}
        """
        texts = [c["text"] for c in chunks]
        if not texts:
            return 0

        embeddings = self.model.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)

        for c in chunks:
            self.metadata.append({
                "pdf_id": pdf_id,
                "text": c["text"],
                "page_start": c["page_start"],
                "page_end": c["page_end"],
                "type": "pdf"
            })

        self.save()
        return len(chunks)

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    '''def search(self, query, top_k=5):
        q_emb = self.model.encode([query]).astype('float32')
        D, I = self.index.search(q_emb, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            results.append({
                'score': float(dist),
                'video_id': meta['video_id'],
                'text': meta['text'],
                'start_time': meta['start_time'],
                'end_time': meta['end_time']
            })
        return results '''
    def search(self, query, top_k=5):
        q_emb = self.model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            result = {
                "score": float(dist),
                "text": meta["text"],
                "type": meta.get("type", "video")
            }
            # attach extra fields based on type
            if meta.get("type") == "pdf":
                result.update({
                    "pdf_id": meta.get("pdf_id"),
                    "page_start": meta.get("page_start"),
                    "page_end": meta.get("page_end"),
                })
            else:
                result.update({
                    "video_id": meta.get("video_id"),
                    "start_time": meta.get("start_time"),
                    "end_time": meta.get("end_time"),
                })
            results.append(result)
        return results

def load_existing_index(course_id):
        store = FaissStore(course_id=course_id)
        print(f"[indexer] loaded {len(store.metadata)} entries for {course_id}")
        return store
