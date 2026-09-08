"""
Data Models and Dataclasses for SQLite
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Story:
    id: Optional[int]
    title: str
    description: str
    content: str
    thumbnail_path: Optional[str] = None
    estimated_duration: int = 40  # in seconds
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class VoiceProfile:
    id: Optional[int]
    name: str
    reference_audio_path: Optional[str] = None
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class GeneratedAudio:
    id: Optional[int]
    story_id: int
    voice_profile_id: int
    file_path: str
    model_name: str
    model_version: Optional[str] = "1.0"
    duration: float = 0.0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
