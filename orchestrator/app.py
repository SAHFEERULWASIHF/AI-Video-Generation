from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database.db import get_db, init_db
from models.models import Reel, ReelStatus, Scene
from script_engine.engine import ScriptEngine
from prompt_engine.engine import PromptEngine
import os

app = FastAPI(title="FSW Creations AI Reel Orchestrator")

@app.on_event("startup")
def startup():
    init_db()

@app.post("/reels/generate")
async def trigger_generation(topic: str, db: Session = Depends(get_db)):
    # 1. Create Reel record
    reel = Reel(topic=topic, status=ReelStatus.PENDING)
    db.add(reel)
    db.commit()
    db.refresh(reel)

    # 2. Trigger Celery Task (Mocked here as background task)
    # process_reel_generation.delay(reel.id)

    return {"reel_id": reel.id, "status": reel.status}

@app.get("/reels/{reel_id}")
async def get_reel_status(reel_id: int, db: Session = Depends(get_db)):
    reel = db.query(Reel).filter(Reel.id == reel_id).first()
    return reel

@app.post("/reels/{reel_id}/post")
async def post_reel(reel_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    reel = db.query(Reel).filter(Reel.id == reel_id).first()
    if not reel: return {"error": "Not found"}

    # Trigger Instagram posting task
    # process_instagram_publish.delay(reel_id)
    return {"status": "posting_triggered"}
