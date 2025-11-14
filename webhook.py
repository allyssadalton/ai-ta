# webhook.py
from fastapi import FastAPI, Request, Response
import uvicorn
import hmac, hashlib, os

app = Fastapi = FastAPI()

# The hub verification will send a GET with challenge to verify; implement that if using WebSub.
@app.get("/youtube/websub")
async def websub_verify(mode: str = None, topic: str = None, challenge: str = None):
    # Respond with the challenge to verify subscription
    return Response(content=challenge, media_type="text/plain")

@app.post("/youtube/websub")
async def websub_notify(request: Request):
    # YouTube will POST an XML/ATOM feed -- parse and extract video id(s)
    body = await request.body()
    # For brevity: naive parsing. Use xml.etree.ElementTree for real parsing.
    # Extract <yt:videoId> elements. Then call your ingest pipeline for each video_id.
    # e.g. ingest_video(video_id)
    return Response(status_code=204)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
