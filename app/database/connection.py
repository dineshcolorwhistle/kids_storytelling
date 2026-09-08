"""
SQLite Database Connection and Migration Manager
"""
import sqlite3
from contextlib import contextmanager
from app.config.settings import DB_PATH
from app.utils.logger import logger

def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    """Context manager for SQLite transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error occurred: {e}")
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database tables according to the project specifications."""
    logger.info(f"Initializing database schema at {DB_PATH}")
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Stories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT NOT NULL,
                thumbnail_path TEXT,
                estimated_duration INTEGER DEFAULT 40,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Voice Profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reference_audio_path TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. Generated Audio table (Cache tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_audio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                voice_profile_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_version TEXT DEFAULT '1.0',
                duration REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                FOREIGN KEY (voice_profile_id) REFERENCES voice_profiles(id) ON DELETE CASCADE,
                UNIQUE(story_id, voice_profile_id, model_name, model_version)
            );
        """)
        
        # Check and insert system default voice if missing
        cursor.execute("SELECT id FROM voice_profiles WHERE is_default = 1")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO voice_profiles (name, reference_audio_path, is_default)
                VALUES (?, ?, 1)
            """, ("Default Narrator (Aiden)", None))
            
    logger.info("Database schema initialized successfully.")
