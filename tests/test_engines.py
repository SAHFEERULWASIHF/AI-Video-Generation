import pytest
from script_engine.engine import ScriptEngine
from prompt_engine.engine import PromptEngine

@pytest.mark.asyncio
async def test_script_generation():
    engine = ScriptEngine()
    topic = "The Future of AI Agents"
    script = await engine.generate_script(topic)

    assert script.topic == topic
    assert len(script.scenes) == 4
    assert script.scenes[0].duration == 4
    assert "dead" in script.scenes[0].dialogue

def test_prompt_generation():
    prompt_engine = PromptEngine()
    from script_engine.engine import ScriptScene
    scene = ScriptScene(
        scene_number=1,
        duration=4,
        dialogue="Hello world",
        emotional_intent="Intense",
        camera_style="Close-up",
        visual_description="Aiden looking at camera"
    )

    prompts = prompt_engine.generate_prompts(scene)
    assert "9:16 vertical" in prompts['first_frame']
    assert "Aiden Vale" in prompts['first_frame']
    assert "synchronized spoken dialogue audio" in prompts['video']
