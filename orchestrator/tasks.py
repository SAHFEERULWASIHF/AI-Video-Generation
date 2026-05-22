from celery import Celery
import os
import asyncio
from sqlalchemy.orm import Session
from database.db import SessionLocal
from models.models import Reel, ReelStatus, Scene, AccountType
from script_engine.engine import ScriptEngine
from prompt_engine.engine import PromptEngine
from veo_pipeline.automation import GoogleAutomation, AccountManager
from editing_engine.engine import EditingEngine
from subtitle_engine.engine import SubtitleEngine
from account_rotation.manager import RotationSystem
import logging

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

async def _process_reel_generation(reel_id: int):
    db = SessionLocal()
    try:
        reel = db.query(Reel).filter(Reel.id == reel_id).first()
        if not reel: return

        reel.status = ReelStatus.GENERATING
        db.commit()

        # 1. Generate Script
        script_engine = ScriptEngine()
        script = await script_engine.generate_script(reel.topic)
        reel.script = script.model_dump_json()
        reel.instagram_caption = script.instagram_caption

        # 2. Setup Tools
        prompt_engine = PromptEngine()
        rotation_system = RotationSystem(db)
        # Assuming accounts are already in DB or loaded from env
        account_manager = AccountManager(os.getenv("GOOGLE_ACCOUNTS_JSON", "[]"))
        google_auto = GoogleAutomation(account_manager, os.getenv("STORAGE_PATH", "./storage"))

        scene_video_paths = []

        # 3. Process Scenes
        for s_data in script.scenes:
            scene = Scene(
                reel_id=reel.id,
                scene_number=s_data.scene_number,
                duration=s_data.duration,
                dialogue=s_data.dialogue,
                visual_prompt=s_data.visual_description
            )
            db.add(scene)
            db.commit()

            prompts = prompt_engine.generate_prompts(s_data)
            scene.first_frame_prompt = prompts['first_frame']
            scene.last_frame_prompt = prompts['last_frame']
            scene.video_generation_prompt = prompts['video']

            # Generate Images
            first_frame_path = await google_auto.generate_image(scene.first_frame_prompt, scene.id)
            last_frame_path = await google_auto.generate_image(scene.last_frame_prompt, scene.id)
            scene.image_path = first_frame_path

            # Generate Video
            video_path = await google_auto.generate_video(
                scene.video_generation_prompt, first_frame_path, last_frame_path, scene.id
            )
            scene.video_path = video_path
            scene.status = "completed"
            scene_video_paths.append(video_path)
            db.commit()

        # 4. Editing
        reel.status = ReelStatus.EDITING
        db.commit()

        editing_engine = EditingEngine(os.getenv("STORAGE_PATH", "./storage"))
        raw_video_path = os.path.join(editing_engine.storage_base, f"reel_{reel.id}_raw.mp4")
        editing_engine.stitch_scenes(scene_video_paths, raw_video_path)

        # Subtitles (Mocked logic for burning)
        final_video_path = os.path.join(editing_engine.storage_base, f"reel_{reel.id}_final.mp4")
        editing_engine.add_subtitles(raw_video_path, [], final_video_path)

        reel.video_path = final_video_path
        reel.status = ReelStatus.COMPLETED
        db.commit()

        # 5. Notify Bot (In a real app, you'd send a webhook or message)
        logging.info(f"Reel {reel.id} generation completed.")

    except Exception as e:
        logging.error(f"Error generating reel {reel_id}: {e}")
        reel.status = ReelStatus.FAILED
        db.commit()
    finally:
        db.close()

@celery_app.task
def process_reel_generation(reel_id: int):
    asyncio.run(_process_reel_generation(reel_id))
