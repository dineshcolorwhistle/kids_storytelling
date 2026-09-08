"""
Background Generation Worker
Runs TTS inference in a secondary QThread to prevent freezing the PySide6 UI.
"""
from PySide6.QtCore import QThread, Signal
from app.database.models import Story, VoiceProfile
from app.tts.qwen_provider import QwenTTSProvider
from app.services.audio_service import AudioService
from app.config.settings import GENERATED_AUDIO_DIR
from app.utils.logger import logger

class GenerationWorker(QThread):
    progress_updated = Signal(int, str)  # percent, status message
    generation_finished = Signal(str)   # output_path
    generation_failed = Signal(str)     # error_message

    def __init__(self, story: Story, voice_profile: VoiceProfile, parent=None):
        super().__init__(parent)
        self.story = story
        self.voice_profile = voice_profile

    def run(self):
        try:
            logger.info(f"Background worker started generation for story: '{self.story.title}', voice: '{self.voice_profile.name}'")
            self.progress_updated.emit(5, "Checking audio cache...")

            # 1. Double check cache
            cached = AudioService.get_cached_audio(self.story.id, self.voice_profile.id)
            if cached:
                logger.info("Found cached audio during worker launch!")
                self.progress_updated.emit(100, "Found in cache!")
                self.generation_finished.emit(cached.file_path)
                return

            # 2. Prepare output path
            if self.voice_profile.is_default:
                output_path = str(GENERATED_AUDIO_DIR / "default" / f"story_{self.story.id}.wav")
            else:
                output_path = str(GENERATED_AUDIO_DIR / f"voice_{self.voice_profile.id:03d}" / f"story_{self.story.id}.wav")

            # 3. Invoke TTS Provider
            provider = QwenTTSProvider.get_instance()

            def on_progress(pct: int, msg: str):
                self.progress_updated.emit(pct, msg)

            final_path = provider.generate(
                text=self.story.content,
                voice_profile=self.voice_profile,
                output_path=output_path,
                progress_callback=on_progress
            )

            # 4. Register in SQLite Cache
            AudioService.register_generated_audio(
                story_id=self.story.id,
                voice_profile_id=self.voice_profile.id,
                file_path=final_path
            )

            logger.info(f"Worker completed synthesis successfully: {final_path}")
            self.progress_updated.emit(100, "Story ready!")
            self.generation_finished.emit(final_path)

        except Exception as e:
            logger.error(f"Generation worker encountered an error: {e}", exc_info=True)
            self.generation_failed.emit(f"Failed to generate story: {e}")
