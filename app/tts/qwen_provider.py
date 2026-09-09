"""
Qwen3-TTS Provider Implementation
Supports both Default voices (CustomVoice) and Cloned personal voices (Base).
Uses lazy loading and singleton instance to avoid reloading heavy weights.
"""
import os
from pathlib import Path
from typing import Optional, Any

from app.tts.base import TTSProvider
from app.database.models import VoiceProfile
from app.config.settings import DEFAULT_TTS_MODEL, BASE_CLONE_TTS_MODEL
from app.utils.logger import logger

class QwenTTSProvider(TTSProvider):
    _instance: Optional["QwenTTSProvider"] = None
    _model_cache = {}

    @classmethod
    def get_instance(cls) -> "QwenTTSProvider":
        if cls._instance is None:
            cls._instance = QwenTTSProvider()
        return cls._instance

    def is_available(self) -> bool:
        return True

    def _get_model(self, model_repo: str):
        """Lazy load and cache model instance on CPU."""
        if model_repo in self._model_cache:
            return self._model_cache[model_repo]

        logger.info(f"Lazy-loading TTS model: {model_repo} onto CPU...")
        import importlib
        torch = importlib.import_module("torch")
        qwen_tts_mod = importlib.import_module("qwen_tts")
        Qwen3TTSModel = getattr(qwen_tts_mod, "Qwen3TTSModel")

        model = Qwen3TTSModel.from_pretrained(
            model_repo,
            device_map="cpu",
            torch_dtype=torch.float32,
        )
        self._model_cache[model_repo] = model
        logger.info(f"Model {model_repo} loaded successfully.")
        return model

    def generate(
        self, 
        text: str, 
        voice_profile: VoiceProfile, 
        output_path: str,
        progress_callback=None
    ) -> str:
        """
        Generate audio using Qwen3-TTS.
        For default profiles -> CustomVoice
        For personal profiles with reference audio -> Base voice cloning
        """
        dest_path = os.path.abspath(output_path)
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(10, "Preparing AI voice model...")

        is_cloning = (
            not voice_profile.is_default 
            and voice_profile.reference_audio_path 
            and os.path.exists(voice_profile.reference_audio_path)
        )

        model_repo = BASE_CLONE_TTS_MODEL if is_cloning else DEFAULT_TTS_MODEL

        if progress_callback:
            progress_callback(25, f"Loading model ({'Voice Cloning' if is_cloning else 'Default Narrator'})...")

        model = self._get_model(model_repo)

        if progress_callback:
            progress_callback(50, "Synthesizing speech from story text...")

        logger.info(f"Generating story audio with profile '{voice_profile.name}' (Cloning={is_cloning})...")

        if is_cloning:
            wavs, sr = model.generate_voice_clone(
                text=text,
                language="English",
                ref_audio=voice_profile.reference_audio_path,
                x_vector_only_mode=True,
            )
        else:
            wavs, sr = model.generate_custom_voice(
                text=text,
                language="English",
                speaker="Aiden",
            )

        if progress_callback:
            progress_callback(85, "Encoding audio output...")

        import importlib
        sf = importlib.import_module("soundfile")
        from app.audio.audio_utils import resample_and_format
        
        audio_data = wavs[0] if isinstance(wavs, list) else wavs
        # Resample to 48kHz Stereo for universal speaker and headset playback
        formatted_audio = resample_and_format(audio_data, orig_sr=sr, target_sr=48000)
        sf.write(dest_path, formatted_audio, 48000, subtype="PCM_16")

        if progress_callback:
            progress_callback(100, "Audio ready!")

        logger.info(f"Saved generated audio to {dest_path} (Normalized to 48000 Hz Stereo)")
        return dest_path
