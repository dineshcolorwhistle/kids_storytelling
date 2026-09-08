"""
Main Application Window
"""
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
from app.config.settings import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from app.ui.styles import MAIN_STYLESHEET
from app.ui.views.story_library_view import StoryLibraryView
from app.ui.views.story_details_view import StoryDetailsView
from app.ui.views.story_player_view import StoryPlayerView
from app.ui.views.voice_enrollment_view import VoiceEnrollmentView
from app.ui.views.generation_view import GenerationView
from app.database.models import Story, VoiceProfile
from app.services.audio_service import AudioService
from app.services.voice_service import VoiceService
from app.utils.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(850, 600)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        self._init_views()
        logger.info("Main application window initialized.")

    def _init_views(self):
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # 1. Story Library View (index 0)
        self.library_view = StoryLibraryView(self)
        self.library_view.story_chosen.connect(self.show_story_details)
        self.stack.addWidget(self.library_view)

        # 2. Story Details View (index 1)
        self.details_view = StoryDetailsView(self)
        self.details_view.back_clicked.connect(self.show_story_library)
        self.details_view.record_new_voice_clicked.connect(self.show_voice_enrollment)
        self.details_view.play_requested.connect(self.handle_play_request)
        self.stack.addWidget(self.details_view)

        # 3. Story Player View (index 2)
        self.player_view = StoryPlayerView(self)
        self.player_view.back_to_library_clicked.connect(self.show_story_library)
        self.stack.addWidget(self.player_view)

        # 4. Voice Enrollment View (index 3)
        self.enrollment_view = VoiceEnrollmentView(self)
        self.enrollment_view.back_clicked.connect(self.show_story_details_current)
        self.enrollment_view.voice_saved.connect(self.handle_voice_saved)
        self.stack.addWidget(self.enrollment_view)

        # 5. Generation Progress View (index 4)
        self.generation_view = GenerationView(self)
        self.generation_view.generation_succeeded.connect(self.handle_generation_succeeded)
        self.generation_view.generation_aborted.connect(self.show_story_details_current)
        self.stack.addWidget(self.generation_view)

        # Start on Library View
        self.stack.setCurrentWidget(self.library_view)

    def show_story_library(self):
        self.stack.setCurrentWidget(self.library_view)

    def show_story_details(self, story: Story):
        self.current_story = story
        self.details_view.set_story(story)
        self.stack.setCurrentWidget(self.details_view)

    def show_story_details_current(self):
        self.stack.setCurrentWidget(self.details_view)

    def show_voice_enrollment(self):
        self.stack.setCurrentWidget(self.enrollment_view)

    def handle_voice_saved(self, profile: VoiceProfile):
        logger.info(f"New voice profile saved: {profile.name} (ID: {profile.id})")
        self.details_view.refresh_voices(select_profile_id=profile.id)
        self.stack.setCurrentWidget(self.details_view)

    def handle_play_request(self, story: Story, voice_profile_id: int):
        voice_profile = VoiceService.get_voice_by_id(voice_profile_id)
        voice_name = voice_profile.name if voice_profile else "Narrator"
        logger.info(f"Play requested for story: '{story.title}' using voice ID {voice_profile_id} ('{voice_name}')")
        
        cached_audio = AudioService.get_cached_audio(story.id, voice_profile_id)
        
        if cached_audio:
            logger.info(f"Found cached audio: {cached_audio.file_path}. Opening player immediately...")
            self.player_view.play_story(story, cached_audio.file_path, voice_name)
            self.stack.setCurrentWidget(self.player_view)
        else:
            logger.info(f"Audio not cached for story {story.id}, voice {voice_profile_id}. Starting generation screen...")
            self.generation_view.start_generation(story, voice_profile)
            self.stack.setCurrentWidget(self.generation_view)

    def handle_generation_succeeded(self, story: Story, audio_path: str, voice_name: str):
        logger.info(f"Generation finished for story '{story.title}' with audio '{audio_path}'. Transitioning to player...")
        self.player_view.play_story(story, audio_path, voice_name)
        self.stack.setCurrentWidget(self.player_view)
