from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Query
import random

import uuid
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

sessions = {}
QUIZ_FILE_PATH = "sample_quiz.txt"
HTML_FILE_PATH = "static/index.html"

app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root path
@app.get("/")
async def serve_frontend():
    return FileResponse(HTML_FILE_PATH)

@app.get("/cat.png")
async def get_cat_image():
    return FileResponse("cat.png")

@app.get("/autoload")
async def autoload_quiz():
    session_id = str(uuid.uuid4())
    with open(QUIZ_FILE_PATH, "r", encoding="utf-8") as f:
        quiz_data = json.load(f)
    sessions[session_id] = {
        "questions": quiz_data,
        "current": 0,
        "score": 0
    }
    return {"session_id": session_id}


@app.get("/question")
async def get_question(session_id: str = Query(...)):
    session = sessions.get(session_id)
    if not session or session["current"] >= len(session["questions"]):
        return {"done": True, "score": session["score"], "total": len(session["questions"])}

    q = session["questions"][session["current"]]
    options = q["options"].copy()
    random.shuffle(options)  

    return {
        "question": q["question"],
        "options": options,
        "done": False
    }


@app.post("/answer")
async def answer_question(session_id: str = Form(...), answer: str = Form(...)):
    session = sessions.get(session_id)
    if session is None:
        return JSONResponse(content={"error": "Invalid session"}, status_code=400)

    current = session["current"]
    if current >= len(session["questions"]):
        return {"feedback": "Quiz already finished."}

    correct = session["questions"][current]["answer"]
    feedback = "Correct!" if answer == correct else f"Wrong! Correct answer: {correct}"
    if answer == correct:
        session["score"] += 1
    session["current"] += 1
    return {"feedback": feedback}
