"""
Story Repository for Database Access
"""
from typing import List, Optional
from app.database.connection import get_db
from app.database.models import Story

class StoryRepository:
    @staticmethod
    def get_all() -> List[Story]:
        """Fetch all stories ordered by title."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stories ORDER BY id ASC")
            rows = cursor.fetchall()
            return [
                Story(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    content=row["content"],
                    thumbnail_path=row["thumbnail_path"],
                    estimated_duration=row["estimated_duration"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

    @staticmethod
    def get_by_id(story_id: int) -> Optional[Story]:
        """Fetch a single story by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
            row = cursor.fetchone()
            if row:
                return Story(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    content=row["content"],
                    thumbnail_path=row["thumbnail_path"],
                    estimated_duration=row["estimated_duration"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    @staticmethod
    def count() -> int:
        """Count total stories."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM stories")
            return cursor.fetchone()["count"]

    @staticmethod
    def create(story: Story) -> int:
        """Insert a new story and return its ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stories (title, description, content, thumbnail_path, estimated_duration)
                VALUES (?, ?, ?, ?, ?)
            """, (story.title, story.description, story.content, story.thumbnail_path, story.estimated_duration))
            return cursor.lastrowid
