"""
3D Pixar Barnaby Bear Video Generator
Synthesizes a high-definition 3D animated video of Barnaby Bear reading the story,
with audio-driven lip-sync, jaw drop, breathing, and eye blinking.
"""
import os
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio
import imageio_ffmpeg
from app.audio.lip_sync_engine import LipSyncEngine

def generate_barnaby_video(audio_path: str, output_mp4: str, fps: int = 30):
    print(f"Analyzing audio: {audio_path}...")
    track = LipSyncEngine.analyze_audio(audio_path, interval_ms=int(1000 / fps))
    if not track:
        raise RuntimeError("Failed to analyze audio for lip sync")

    duration_sec = track.duration_ms / 1000.0
    total_frames = int(duration_sec * fps)
    print(f"Total duration: {duration_sec:.2f}s ({total_frames} frames at {fps} fps)")

    # Load base 3D Pixar Bear
    base_img_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\802a9d26-1236-4a7c-91ee-c0ada0de8356\sample_3d_avatar_animal_1789368460060.jpg"
    assert os.path.exists(base_img_path), f"Base image not found: {base_img_path}"
    
    base_img = Image.open(base_img_path).convert("RGBA")
    w, h = 640, 640
    base_img = base_img.resize((w, h), Image.Resampling.LANCZOS)

    # Snout / Mouth coordinate calibration on 640x640:
    # Barnaby's nose is at (320, 310)
    # Barnaby's mouth is at (320, 360)
    # Eyes are at (255, 230) and (385, 230)
    mouth_cx = 320
    mouth_cy = 356

    temp_video = output_mp4.replace(".mp4", "_temp.mp4")
    writer = imageio.get_writer(temp_video, fps=fps, codec='libx264', quality=8, pixelformat='yuv420p')

    print("Synthesizing 3D animated video frames...")
    last_blink_frame = -100

    for i in range(total_frames):
        t = i / float(fps)
        pos_ms = int(t * 1000)
        frame_data = track.get_frame(pos_ms)
        openness = frame_data.openness
        viseme = frame_data.viseme_type
        width_factor = frame_data.width

        # 1. Subtle 3D breathing expansion & head drift
        breath_scale = 1.0 + math.sin(t * 2.2) * 0.008
        drift_y = int(math.sin(t * 2.0) * 4.0)

        # 2. Eye Blink calculation
        if i - last_blink_frame > fps * 3.5:
            last_blink_frame = i
        blink_age = (i - last_blink_frame) / float(fps)
        is_blinking = blink_age < 0.16
        blink_progress = 0.0
        if is_blinking:
            if blink_age < 0.08:
                blink_progress = blink_age / 0.08
            else:
                blink_progress = 1.0 - ((blink_age - 0.08) / 0.08)

        # Clone base image
        frame_img = base_img.copy()
        draw = ImageDraw.Draw(frame_img, "RGBA")

        # 3. Dynamic 3D Eyelids for natural blinking
        if blink_progress > 0.05:
            lid_color = (222, 140, 70, int(255 * blink_progress))
            eye_h = int(24 * blink_progress)
            for ex in [255, 385]:
                draw.ellipse([ex - 22, 230 - 8, ex + 22, 230 - 8 + eye_h], fill=lid_color)

        # 4. Prominent 3D Jaw Drop & Animated Mouth
        if openness > 0.06:
            half_w = int(26 * (0.7 + width_factor * 0.65))
            open_h = int(openness * 36)

            top_y = mouth_cy - int(open_h * 0.25)
            bot_y = mouth_cy + int(open_h * 0.75)

            # Deep inner oral cavity
            cavity_rect = [mouth_cx - half_w, top_y, mouth_cx + half_w, bot_y]
            draw.ellipse(cavity_rect, fill=(58, 12, 18, 255), outline=(130, 60, 25, 255), width=2)

            # White upper teeth
            if openness > 0.25:
                teeth_w = int(half_w * 1.1)
                draw.rounded_rectangle([mouth_cx - teeth_w//2, top_y, mouth_cx + teeth_w//2, top_y + 8], radius=3, fill=(250, 250, 250, 240))

            # Pink tongue
            tongue_h = int(open_h * 0.45)
            draw.ellipse([mouth_cx - int(half_w * 0.55), bot_y - tongue_h, mouth_cx + int(half_w * 0.55), bot_y + 2], fill=(245, 110, 110, 255))

        # Convert to RGB numpy array
        frame_rgb = np.array(frame_img.convert("RGB"))
        writer.append_data(frame_rgb)

        if i % (fps * 5) == 0:
            print(f"  Processed {i}/{total_frames} frames ({i/total_frames*100:.0f}%)")

    writer.close()
    print("Video stream generated! Muxing audio...")

    # Mux WAV audio with MP4 video using ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    cmd = [
        ffmpeg_exe, "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(temp_video):
        os.remove(temp_video)

    print(f"SUCCESS: Created 3D Pixar Barnaby Bear video: {output_mp4} ({os.path.getsize(output_mp4):,} bytes)")

if __name__ == "__main__":
    audio = "data/generated_audio/default/story_1.wav"
    output = "data/avatars/barnaby_3d_storyteller.mp4"
    generate_barnaby_video(audio, output)
