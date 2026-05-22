from typing import Dict
from script_engine.engine import ScriptScene

class PromptEngine:
    IDENTITY_DESCRIPTION = """
Aiden Vale, male, age 30, mixed European + Middle Eastern features, defined jawline, warm olive skin tone, dark textured hair, subtle designer stubble, deep grey-blue eyes.
Wearing: black premium fitted t-shirt, dark navy overshirt, silver minimal watch.
Environment: moody luxury creator studio, teal edge lighting (#00D4AA), warm key light, deep navy background tones.
Style: cinematic realism, hyper realistic skin texture, Netflix documentary style, luxury commercial quality, shallow depth of field, anamorphic cinematic feeling, subtle film grain.
"""

    def generate_prompts(self, scene: ScriptScene) -> Dict[str, str]:
        first_frame = self._build_image_prompt(scene, "starting")
        last_frame = self._build_image_prompt(scene, "ending")
        video_prompt = self._build_video_prompt(scene)

        return {
            "first_frame": first_frame,
            "last_frame": last_frame,
            "video": video_prompt
        }

    def _build_image_prompt(self, scene: ScriptScene, frame_type: str) -> str:
        prompt = f"9:16 vertical, cinematic realism, {frame_type} frame. {self.IDENTITY_DESCRIPTION} "
        prompt += f"Camera: {scene.camera_style}. Action: {scene.visual_description}. "
        prompt += "NO text overlays, NO captions."
        return prompt

    def _build_video_prompt(self, scene: ScriptScene) -> str:
        prompt = f"Generate a {scene.duration}-second video. {self.IDENTITY_DESCRIPTION} "
        prompt += f"Action: {scene.visual_description}. Emotional delivery: {scene.emotional_intent}. "
        prompt += f"Voiceover: \"{scene.dialogue}\". Deep, calm, authoritative male voice. "
        prompt += "9:16 ratio, cinematic realistic, synchronized spoken dialogue audio, NO text on screen."
        return prompt
