"""
Audio Utilities for Hardware Compatibility
Ensures all audio files are 48kHz Stereo 16-bit PCM for universal compatibility
with built-in laptop speakers (Realtek, etc.) and all headsets/headphones.
"""
import os
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from app.utils.logger import logger

TARGET_SAMPLE_RATE = 48000
TARGET_CHANNELS = 2

def resample_and_format(data: np.ndarray, orig_sr: int, target_sr: int = TARGET_SAMPLE_RATE) -> np.ndarray:
    """
    Resample audio array to target sample rate and ensure dual-channel stereo format.
    """
    # 1. Convert to 1D mono first if needed
    if data.ndim == 1:
        mono = data
    elif data.ndim == 2:
        if data.shape[1] == 1:
            mono = data[:, 0]
        elif data.shape[0] == 1:
            mono = data[0, :]
        else:
            mono = data.mean(axis=1)
    else:
        mono = data.flatten()

    # 2. Resample if necessary
    if orig_sr != target_sr:
        target_length = round(len(mono) * target_sr / orig_sr)
        if target_length > 0:
            x_old = np.linspace(0, 1, len(mono), endpoint=False)
            x_new = np.linspace(0, 1, target_length, endpoint=False)
            resampled = np.interp(x_new, x_old, mono).astype(np.float32)
        else:
            resampled = np.zeros((0,), dtype=np.float32)
    else:
        resampled = mono.astype(np.float32)

    # 3. Peak-normalize slightly to prevent any digital clipping
    max_val = float(np.max(np.abs(resampled))) if resampled.size > 0 else 0.0
    if max_val > 0.98:
        resampled = resampled * (0.95 / max_val)

    # 4. Convert mono to 2-channel stereo (duplicate channels)
    stereo = np.column_stack([resampled, resampled]).astype(np.float32)
    return stereo

def ensure_compatible_audio(file_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> str:
    """
    Ensures the audio file is 48kHz Stereo 16-bit PCM.
    If it is already compatible, returns file_path directly.
    If not, converts the file in-place (or writes a normalized replacement).
    """
    if not file_path or not os.path.exists(file_path):
        return file_path

    try:
        info = sf.info(file_path)
        # Check if already 48kHz Stereo PCM
        if info.samplerate == target_sr and info.channels == TARGET_CHANNELS:
            return file_path

        logger.info(f"Normalizing audio for speaker/headset compatibility: {file_path} (was {info.samplerate}Hz, {info.channels}ch)")

        data, sr = sf.read(file_path)
        stereo = resample_and_format(data, orig_sr=sr, target_sr=target_sr)

        # Write to temporary file first then replace
        temp_dir = os.path.dirname(file_path)
        temp_out = os.path.join(temp_dir, f"tmp_norm_{os.path.basename(file_path)}")
        sf.write(temp_out, stereo, target_sr, subtype="PCM_16")

        # Atomic replace
        if os.path.exists(temp_out):
            os.replace(temp_out, file_path)
            logger.info(f"Successfully converted audio to {target_sr}Hz Stereo: {file_path}")

        return file_path

    except Exception as e:
        logger.error(f"Error ensuring compatible audio for {file_path}: {e}")
        return file_path
