"""
Voice Profile Repository for Database Access
"""
from typing import List, Optional
from app.database.connection import get_db
from app.database.models import VoiceProfile

class VoiceProfileRepository:
    @staticmethod
    def get_all() -> List[VoiceProfile]:
        """Fetch all voice profiles ordered with default first, then newest."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM voice_profiles ORDER BY is_default DESC, id ASC")
            rows = cursor.fetchall()
            return [
                VoiceProfile(
                    id=row["id"],
                    name=row["name"],
                    reference_audio_path=row["reference_audio_path"],
                    is_default=bool(row["is_default"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(profile_id: int) -> Optional[VoiceProfile]:
        """Fetch a single voice profile by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM voice_profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            if row:
                return VoiceProfile(
                    id=row["id"],
                    name=row["name"],
                    reference_audio_path=row["reference_audio_path"],
                    is_default=bool(row["is_default"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    @staticmethod
    def create(name: str, reference_audio_path: Optional[str] = None, is_default: bool = False) -> int:
        """Create a new voice profile and return its ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO voice_profiles (name, reference_audio_path, is_default)
                VALUES (?, ?, ?)
            """, (name, reference_audio_path, 1 if is_default else 0))
            return cursor.lastrowid

    @staticmethod
    def delete(profile_id: int) -> bool:
        """Delete a voice profile by ID (cannot delete default)."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voice_profiles WHERE id = ? AND is_default = 0", (profile_id,))
            return cursor.rowcount > 0
