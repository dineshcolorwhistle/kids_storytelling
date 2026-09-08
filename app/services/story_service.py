"""
Story Service Layer
"""
from typing import List, Optional
from app.database.models import Story
from app.database.repositories.story_repository import StoryRepository

class StoryService:
    @staticmethod
    def get_all_stories() -> List[Story]:
        return StoryRepository.get_all()

    @staticmethod
    def get_story_by_id(story_id: int) -> Optional[Story]:
        return StoryRepository.get_by_id(story_id)

    @staticmethod
    def get_story_count() -> int:
        return StoryRepository.count()
