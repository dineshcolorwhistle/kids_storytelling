"""
Application Configuration and Settings
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"

# Data subdirectories
DATABASE_DIR = DATA_DIR / "database"
STORIES_DIR = DATA_DIR / "stories"
VOICES_DIR = DATA_DIR / "voices"
GENERATED_AUDIO_DIR = DATA_DIR / "generated_audio"
LOG_DIR = DATA_DIR / "logs"

# Ensure runtime directories exist
for path in [DATABASE_DIR, STORIES_DIR, VOICES_DIR, GENERATED_AUDIO_DIR, LOG_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATABASE_DIR / "app.db"

# App Metadata
APP_NAME = "MyStory — Kids AI Storytelling"
APP_VERSION = "0.1.0"
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700

# Audio / TTS Settings
AUDIO_SAMPLE_RATE = 24000
DEFAULT_TTS_MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
BASE_CLONE_TTS_MODEL = "Qwen/Qwen3-TTS-12Hz-0.6B-Base"

# TTS Mode: "local" or "remote"
TTS_MODE = os.getenv("TTS_MODE", "local")
REMOTE_TTS_URL = os.getenv("REMOTE_TTS_URL", "http://localhost:8000")
