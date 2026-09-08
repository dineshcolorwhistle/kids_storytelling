"""
Audio Service and Caching Engine
"""
import os
from pathlib import Path
from typing import Optional
import soundfile as sf

from app.config.settings import GENERATED_AUDIO_DIR, DEFAULT_TTS_MODEL
from app.database.models import GeneratedAudio
from app.database.repositories.generated_audio_repository import GeneratedAudioRepository
from app.utils.logger import logger

class AudioService:
    DEFAULT_DIR = GENERATED_AUDIO_DIR / "default"

    @classmethod
    def get_cached_audio(
        cls, 
        story_id: int, 
        voice_profile_id: int, 
        model_name: str = DEFAULT_TTS_MODEL, 
        model_version: str = "1.0"
    ) -> Optional[GeneratedAudio]:
        """
        Check if audio exists both in SQLite and physically on disk.
        Returns GeneratedAudio if valid cache hit, else None.
        """
        record = GeneratedAudioRepository.get_by_cache_key(
            story_id, voice_profile_id, model_name, model_version
        )
        if record:
            if os.path.exists(record.file_path):
                logger.info(f"[CACHE HIT] Audio found for story {story_id}, voice {voice_profile_id}: {record.file_path}")
                return record
            else:
                logger.warning(f"[CACHE MISS] Record existed in DB but file missing on disk: {record.file_path}")
                
        # Also check fallback on disk for default voice
        if voice_profile_id == 1:
            disk_path = cls.DEFAULT_DIR / f"story_{story_id}.wav"
            if disk_path.exists():
                logger.info(f"[CACHE RECOVERY] Discovered unindexed default audio at {disk_path}")
                try:
                    info = sf.info(str(disk_path))
                    duration = info.duration
                except Exception:
                    duration = 30.0
                
                new_record = GeneratedAudio(
                    id=None,
                    story_id=story_id,
                    voice_profile_id=1,
                    file_path=str(disk_path),
                    model_name=model_name,
                    model_version=model_version,
                    duration=duration
                )
                GeneratedAudioRepository.save(new_record)
                return new_record

        logger.info(f"[CACHE MISS] No cached audio found for story {story_id}, voice {voice_profile_id}")
        return None

    @classmethod
    def register_generated_audio(
        cls,
        story_id: int,
        voice_profile_id: int,
        file_path: str,
        model_name: str = DEFAULT_TTS_MODEL,
        model_version: str = "1.0"
    ) -> GeneratedAudio:
        """Register newly generated audio file into cache."""
        try:
            info = sf.info(file_path)
            duration = info.duration
        except Exception:
            duration = 30.0

        audio = GeneratedAudio(
            id=None,
            story_id=story_id,
            voice_profile_id=voice_profile_id,
            file_path=os.path.abspath(file_path),
            model_name=model_name,
            model_version=model_version,
            duration=duration
        )
        audio_id = GeneratedAudioRepository.save(audio)
        audio.id = audio_id
        logger.info(f"Registered audio cache id {audio_id} for story {story_id}, duration {duration:.2f}s")
        return audio
