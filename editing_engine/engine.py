import ffmpeg
import os
from typing import List

class EditingEngine:
    def __init__(self, storage_base: str):
        self.storage_base = storage_base

    def stitch_scenes(self, scene_paths: List[str], output_path: str):
        if not scene_paths:
            return

        # Create concat file for ffmpeg
        concat_file = os.path.join(self.storage_base, "concat_list.txt")
        with open(concat_file, "w") as f:
            for path in scene_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")

        try:
            (
                ffmpeg
                .input(concat_file, format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(quiet=True)
            )
        finally:
            if os.path.exists(concat_file):
                os.remove(concat_file)

    def add_subtitles(self, video_path: str, srt_path: str, output_path: str):
        # Burn subtitles into video using FFmpeg
        try:
            (
                ffmpeg
                .input(video_path)
                .filter('subtitles', srt_path, force_style='Fontname=Arial,Fontsize=24,PrimaryColour=&H00D4AA,OutlineColour=&H000000,BorderStyle=1,Outline=2')
                .output(output_path)
                .overwrite_output()
                .run(quiet=True)
            )
        except Exception as e:
            print(f"Subtitle burning error: {e}")
            import shutil
            shutil.copy(video_path, output_path)

    def add_background_music(self, video_path: str, music_path: str, output_path: str, volume: float = 0.1):
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(music_path).filter('volume', volume)

        (
            ffmpeg
            .output(video.video, video.audio, audio, output_path, vcodec='copy', acodec='aac', shortest=None)
            .overwrite_output()
            .run(quiet=True)
        )
