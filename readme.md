# Allyssa-Dalton-AI-Project-2025

To run
$ pip install -r requirements.txt
$ cd backend
$ python3 server.py
$ cd ../aita-ui
$ npm run dev

To ingest video - cannot be done in codespace
(course name must be in format CSCI### (e.g. CSCI240, CSCI420))
$ python3 ingest_one_video.py <course> <video id> <slides link (optional)>

check to ensure app is working
 
$ curl -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json" -d '{"question":"What is gradient descent?","top_k":3}' 