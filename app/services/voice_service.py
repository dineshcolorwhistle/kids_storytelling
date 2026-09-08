"""
Voice Service Layer
Handles voice profile creation, reference audio validation, and lifecycle.
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import soundfile as sf

from app.config.settings import VOICES_DIR
from app.database.models import VoiceProfile
from app.database.repositories.voice_profile_repository import VoiceProfileRepository
from app.utils.logger import logger

MIN_RECORDING_DURATION_SEC = 10.0  # Minimum 10 seconds for testing/MVP
RECOMMENDED_DURATION_SEC = 20.0

class VoiceService:
    @staticmethod
    def get_all_voices() -> List[VoiceProfile]:
        return VoiceProfileRepository.get_all()

    @staticmethod
    def get_voice_by_id(profile_id: int) -> Optional[VoiceProfile]:
        return VoiceProfileRepository.get_by_id(profile_id)

    @staticmethod
    def validate_audio_file(audio_path: str) -> Tuple[bool, str, float]:
        """
        Validate audio file exists and check duration.
        Returns (is_valid, message, duration).
        """
        if not os.path.exists(audio_path):
            return False, "Audio file does not exist.", 0.0

        try:
            info = sf.info(audio_path)
            duration = info.duration
            if duration < MIN_RECORDING_DURATION_SEC:
                return False, f"Recording is too short ({duration:.1f}s). Please record at least {int(MIN_RECORDING_DURATION_SEC)} seconds.", duration
            return True, "Audio is valid.", duration
        except Exception as e:
            logger.error(f"Error inspecting audio file {audio_path}: {e}")
            return False, f"Could not read audio file: {e}", 0.0

    @classmethod
    def create_voice_profile(cls, name: str, temp_audio_path: str) -> Tuple[bool, str, Optional[VoiceProfile]]:
        """
        Validate temporary recording, save to permanent location, and register in database.
        """
        clean_name = name.strip()
        if not clean_name:
            return False, "Please enter a name for this voice profile.", None

        is_valid, msg, duration = cls.validate_audio_file(temp_audio_path)
        if not is_valid:
            return False, msg, None

        # 1. Create DB entry to acquire profile ID
        profile_id = VoiceProfileRepository.create(clean_name, None, is_default=False)
        
        # 2. Copy audio to permanent directory: data/voices/voice_{id}/reference.wav
        profile_dir = VOICES_DIR / f"voice_{profile_id:03d}"
        profile_dir.mkdir(parents=True, exist_ok=True)
        dest_path = profile_dir / "reference.wav"

        try:
            shutil.copyfile(temp_audio_path, dest_path)
            # Update DB with final path
            from app.database.connection import get_db
            with get_db() as conn:
                conn.execute(
                    "UPDATE voice_profiles SET reference_audio_path = ? WHERE id = ?",
                    (str(dest_path), profile_id)
                )

            logger.info(f"Successfully created VoiceProfile '{clean_name}' (ID: {profile_id}) at {dest_path}")
            profile = VoiceProfileRepository.get_by_id(profile_id)
            return True, "Voice profile saved successfully!", profile
        except Exception as e:
            logger.error(f"Failed to copy voice reference audio: {e}")
            VoiceProfileRepository.delete(profile_id)
            return False, f"Failed to save audio file: {e}", None

    @staticmethod
    def delete_voice_profile(profile_id: int) -> bool:
        """Delete voice profile and its disk directory."""
        profile = VoiceProfileRepository.get_by_id(profile_id)
        if not profile or profile.is_default:
            logger.warning(f"Cannot delete voice profile id {profile_id} (not found or is default)")
            return False

        # Remove disk directory if exists
        if profile.reference_audio_path:
            parent_dir = Path(profile.reference_audio_path).parent
            if parent_dir.exists() and parent_dir != VOICES_DIR:
                try:
                    shutil.rmtree(parent_dir)
                except Exception as e:
                    logger.error(f"Error removing voice profile dir {parent_dir}: {e}")

        # Also remove cached generated audio directory for this voice profile
        from app.config.settings import GENERATED_AUDIO_DIR
        gen_dir = GENERATED_AUDIO_DIR / f"voice_{profile_id:03d}"
        if gen_dir.exists():
            try:
                shutil.rmtree(gen_dir)
            except Exception as e:
                logger.error(f"Error removing generated audio dir {gen_dir}: {e}")

        success = VoiceProfileRepository.delete(profile_id)
        logger.info(f"Deleted voice profile {profile_id}: {success}")
        return success
