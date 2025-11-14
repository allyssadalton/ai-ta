from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI()

class AskRequest(BaseModel):
    question: str
    top_k: int = 4

@app.get("/")
def root():
    return {"message": "AI TA is running!"}

# Temporary /ask endpoint
@app.post("/ask")
def ask(req: AskRequest):
    question = req.question
    top_k = req.top_k
    # Dummy answer for now
    return {
        "question": question,
        "answer": f"This is a placeholder answer for '{question}'",
        "sources": []
    }
