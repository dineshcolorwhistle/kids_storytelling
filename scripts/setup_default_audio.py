"""
Setup and Register Pre-Generated Default Story Audio
"""
import os
import sys
import shutil
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import soundfile as sf
from app.config.settings import GENERATED_AUDIO_DIR, DEFAULT_TTS_MODEL
from app.services.audio_service import AudioService
from app.services.story_service import StoryService
from app.utils.logger import logger

def setup_default_audio():
    default_dir = GENERATED_AUDIO_DIR / "default"
    default_dir.mkdir(parents=True, exist_ok=True)

    poc_audio = GENERATED_AUDIO_DIR / "poc_output.wav"
    if not poc_audio.exists():
        logger.error(f"Base POC audio not found at {poc_audio}")
        return

    stories = StoryService.get_all_stories()
    logger.info(f"Setting up default audio for {len(stories)} stories...")

    for story in stories:
        target_path = default_dir / f"story_{story.id}.wav"
        if not target_path.exists():
            # Seed with the validated high quality audio
            shutil.copyfile(poc_audio, target_path)
            logger.info(f"Created default audio for story {story.id} ({story.title})")

        # Register in SQLite cache
        AudioService.register_generated_audio(
            story_id=story.id,
            voice_profile_id=1,  # Default Narrator ID
            file_path=str(target_path),
            model_name=DEFAULT_TTS_MODEL,
            model_version="1.0"
        )

    logger.info("[SUCCESS] All default stories indexed in SQLite cache.")

if __name__ == "__main__":
    setup_default_audio()
