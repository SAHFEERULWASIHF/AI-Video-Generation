from pydantic import BaseModel
from typing import List, Optional
import os
import json

class ScriptScene(BaseModel):
    scene_number: int
    duration: int
    dialogue: str
    emotional_intent: str
    camera_style: str
    visual_description: str

class ReelScript(BaseModel):
    topic: str
    hook: str
    tension: str
    escalation: str
    proof: str
    payoff: str
    cta: str
    scenes: List[ScriptScene]
    instagram_caption: str

class ScriptEngine:
    def __init__(self):
        # In production, initialize google-generativeai here
        self.api_key = os.getenv("GEMINI_API_KEY")

    async def generate_script(self, topic: str) -> ReelScript:
        # Template-based generation as a robust fallback/default for high-retention logic
        # This follows the mandatory brand strategy

        script = ReelScript(
            topic=topic,
            hook=f"SEO as you know it... is dead. Especially regarding {topic}.",
            tension=f"Google's 2026 update is a direct attack on how you handle {topic}.",
            escalation="If AI doesn't cite you as an authority, you don't exist in the GEO era.",
            proof=f"We've optimized {topic} across 100+ entities with FSW Creations.",
            payoff="The 1% are using this secret to bypass traditional search and dominate the AI brain.",
            cta=f"Stop guessing with {topic}. Follow FSW for the 2026 roadmap.",
            instagram_caption=f"SEO isn't dying; it's evolving. {topic} is the new frontier. #FSWCreations #SEO2026 #GEO",
            scenes=[]
        )

        script.scenes = self.split_into_scenes(script)
        return script

    def split_into_scenes(self, script: ReelScript) -> List[ScriptScene]:
        scenes = []
        # Hook (4s)
        scenes.append(ScriptScene(
            scene_number=1, duration=4, dialogue=script.hook,
            emotional_intent="Provocative", camera_style="Close-up",
            visual_description="Aiden Vale looking directly into camera with intense gaze, moody studio, teal glow."
        ))
        # Tension & Escalation (8s)
        scenes.append(ScriptScene(
            scene_number=2, duration=8, dialogue=f"{script.tension} {script.escalation}",
            emotional_intent="Authoritative", camera_style="Medium shot",
            visual_description="Aiden gesturing towards floating Electric Teal data visualizations."
        ))
        # Proof & Payoff (8s)
        scenes.append(ScriptScene(
            scene_number=3, duration=8, dialogue=f"{script.proof} {script.payoff}",
            emotional_intent="Visionary", camera_style="Close-up on hands/face",
            visual_description="Aiden interacting with a glass tablet reflecting teal light."
        ))
        # CTA (4s)
        scenes.append(ScriptScene(
            scene_number=4, duration=4, dialogue=script.cta,
            emotional_intent="Confident", camera_style="Medium shot",
            visual_description="Aiden standing confidently, FSW logo glowing in background."
        ))
        return scenes
