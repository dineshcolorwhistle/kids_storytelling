"""
Abstract Base Class for Text-to-Speech Providers
Ensures the UI and services are strictly decoupled from model implementations.
"""
from abc import ABC, abstractmethod
from app.database.models import VoiceProfile

class TTSProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the TTS model/service is initialized or available."""
        pass

    @abstractmethod
    def generate(
        self, 
        text: str, 
        voice_profile: VoiceProfile, 
        output_path: str,
        progress_callback=None
    ) -> str:
        """
        Generate audio from text using the given VoiceProfile and save to output_path.
        Returns the absolute path to the generated WAV file.
        """
        pass
