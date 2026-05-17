import os
import json
import time
from google import genai
from google.genai import types
from moviepy.editor import VideoFileClip, concatenate_videoclips
from instagrapi import Client as InstaClient

def generate_reel(reel_id, google_api_key):
    client = genai.Client(api_key=google_api_key)

    with open('reels_data.json', 'r') as f:
        reels = json.load(f)

    reel = next((r for r in reels if r['reel_id'] == reel_id), None)
    if not reel:
        print(f"Reel {reel_id} not found.")
        return None

    video_clips = []

    for scene in reel['scenes']:
        print(f"Generating Scene {scene['id']} for Reel {reel_id}...")

        # 1. Generate Video with Veo 3.1
        # In a real API call, we'd pass first_frame_prompt and last_frame_prompt as guidance
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=f"{scene['video_prompt']} | Guidance: First Frame: {scene['first_frame_prompt']}, Last Frame: {scene['last_frame_prompt']}",
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16"
            )
        )

        while not operation.done:
            print("Waiting for video generation...")
            time.sleep(30)

        video_path = f"scene_{scene['id']}.mp4"
        operation.result.save(video_path)
        video_clips.append(VideoFileClip(video_path))

    # 2. Concatenate Clips
    final_clip = concatenate_videoclips(video_clips)
    final_output = f"reel_{reel_id}_final.mp4"
    final_clip.write_videofile(final_output, fps=24)

    print(f"Reel {reel_id} generated successfully: {final_output}")
    return final_output, reel['caption']

def post_to_instagram(video_path, caption, username, password):
    cl = InstaClient()
    cl.login(username, password)
    reel = cl.clip_upload(video_path, caption)
    print(f"Reel posted successfully: {reel.pk}")

def run_automation():
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    INSTA_USERNAME = os.getenv("INSTA_USERNAME")
    INSTA_PASSWORD = os.getenv("INSTA_PASSWORD")

    # Determine which reel to post based on current day and time
    # This is a simplified logic for 30 days, 2 posts per day
    import datetime
    now = datetime.datetime.now()
    # Assume we started on some date, calculate the reel index
    # For demonstration, we'll use a fixed index or pass it via env
    reel_id = int(os.getenv("REEL_ID", 1))

    video_path, caption = generate_reel(reel_id, GOOGLE_API_KEY)
    if video_path:
        post_to_instagram(video_path, caption, INSTA_USERNAME, INSTA_PASSWORD)

if __name__ == "__main__":
    run_automation()
