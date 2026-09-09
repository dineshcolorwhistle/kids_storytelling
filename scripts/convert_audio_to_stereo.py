"""
Convert all existing generated and reference audio files to 48kHz Stereo 16-bit PCM.
Ensures immediate compatibility with laptop speakers (Realtek) and headsets.
"""
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import soundfile as sf
from app.audio.audio_utils import ensure_compatible_audio
from app.utils.logger import logger

def convert_all():
    data_dir = BASE_DIR / "data"
    audio_dirs = [data_dir / "generated_audio", data_dir / "voices"]

    count = 0
    for adir in audio_dirs:
        if not adir.exists():
            continue
        for root, _, files in os.walk(adir):
            for file in files:
                if file.lower().endswith(".wav"):
                    file_path = os.path.join(root, file)
                    try:
                        info = sf.info(file_path)
                        if info.samplerate != 48000 or info.channels != 2:
                            logger.info(f"Converting: {file_path} (from {info.samplerate}Hz {info.channels}ch to 48000Hz 2ch)")
                            ensure_compatible_audio(file_path)
                            count += 1
                        else:
                            logger.info(f"Already 48kHz Stereo: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to process {file_path}: {e}")

    logger.info(f"[DONE] Converted {count} audio files to 48kHz Stereo.")

if __name__ == "__main__":
    convert_all()
