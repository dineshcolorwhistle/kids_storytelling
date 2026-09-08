"""
Generated Audio Repository for SQLite Caching
"""
from typing import Optional, List
from app.database.connection import get_db
from app.database.models import GeneratedAudio

class GeneratedAudioRepository:
    @staticmethod
    def get_by_cache_key(
        story_id: int, 
        voice_profile_id: int, 
        model_name: str, 
        model_version: str = "1.0"
    ) -> Optional[GeneratedAudio]:
        """Find cached audio record matching the exact cache key."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM generated_audio 
                WHERE story_id = ? 
                  AND voice_profile_id = ? 
                  AND model_name = ? 
                  AND model_version = ?
                LIMIT 1
            """, (story_id, voice_profile_id, model_name, model_version))
            row = cursor.fetchone()
            if row:
                return GeneratedAudio(
                    id=row["id"],
                    story_id=row["story_id"],
                    voice_profile_id=row["voice_profile_id"],
                    file_path=row["file_path"],
                    model_name=row["model_name"],
                    model_version=row["model_version"],
                    duration=row["duration"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    @staticmethod
    def save(audio: GeneratedAudio) -> int:
        """Insert or replace a cached audio record."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO generated_audio (
                    story_id, voice_profile_id, file_path, model_name, model_version, duration
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                audio.story_id,
                audio.voice_profile_id,
                audio.file_path,
                audio.model_name,
                audio.model_version,
                audio.duration
            ))
            return cursor.lastrowid

    @staticmethod
    def get_by_story_and_voice(story_id: int, voice_profile_id: int) -> Optional[GeneratedAudio]:
        """Get any cached audio for story and voice."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM generated_audio 
                WHERE story_id = ? AND voice_profile_id = ?
                ORDER BY id DESC LIMIT 1
            """, (story_id, voice_profile_id))
            row = cursor.fetchone()
            if row:
                return GeneratedAudio(
                    id=row["id"],
                    story_id=row["story_id"],
                    voice_profile_id=row["voice_profile_id"],
                    file_path=row["file_path"],
                    model_name=row["model_name"],
                    model_version=row["model_version"],
                    duration=row["duration"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None
