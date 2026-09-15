"""
Lip-Sync Engine
Analyzes audio files into synchronized time-indexed viseme frames for avatar animation.
"""
import os
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
import soundfile as sf
import numpy as np
from app.utils.logger import logger

@dataclass
class VisemeFrame:
    time_ms: int
    openness: float    # 0.0 (closed) to 1.0 (wide open)
    width: float       # 0.0 (narrow/pucker) to 1.0 (wide grin)
    viseme_type: str   # 'REST', 'AA', 'OO', 'EE', 'MBP'

class LipSyncTrack:
    """
    Holds pre-computed viseme frames for an audio track and provides
    fast O(1) query with temporal smoothing.
    """
    def __init__(self, frames: List[VisemeFrame], interval_ms: int = 25, duration_ms: int = 0):
        self.frames = frames
        self.interval_ms = interval_ms
        self.duration_ms = duration_ms
        self._current_openness = 0.0
        self._current_width = 0.5
        self._smoothing_factor = 0.65  # Snappy, natural syllable response

    def get_frame(self, position_ms: int) -> VisemeFrame:
        """Get the smoothed viseme frame for a given playback timestamp in milliseconds."""
        if not self.frames:
            return VisemeFrame(position_ms, 0.0, 0.5, "REST")

        idx = int(position_ms / self.interval_ms)
        if idx < 0:
            target = self.frames[0]
        elif idx >= len(self.frames):
            target = VisemeFrame(position_ms, 0.0, 0.5, "REST")
        else:
            target = self.frames[idx]

        # Apply exponential smoothing for natural lip movement
        self._current_openness += (target.openness - self._current_openness) * self._smoothing_factor
        self._current_width += (target.width - self._current_width) * self._smoothing_factor

        return VisemeFrame(
            time_ms=position_ms,
            openness=round(self._current_openness, 3),
            width=round(self._current_width, 3),
            viseme_type=target.viseme_type
        )

    def reset_smoothing(self):
        """Reset internal smoothed values (e.g. on seek or stop)."""
        self._current_openness = 0.0
        self._current_width = 0.5


class LipSyncEngine:
    """
    Extracts speech envelope, RMS energy, and frequency characteristics from
    audio files to generate synchronized viseme animation tracks.
    """
    @staticmethod
    def analyze_audio(file_path: str, interval_ms: int = 25) -> Optional[LipSyncTrack]:
        """
        Analyze a WAV audio file and return a LipSyncTrack.
        """
        if not os.path.exists(file_path):
            logger.error(f"Cannot analyze lip-sync: file does not exist: {file_path}")
            return None

        try:
            data, sample_rate = sf.read(file_path)
            
            # Convert multi-channel to mono
            if data.ndim > 1:
                data = np.mean(data, axis=1)

            total_samples = len(data)
            duration_ms = int((total_samples / sample_rate) * 1000)
            samples_per_frame = int(sample_rate * (interval_ms / 1000.0))

            if samples_per_frame <= 0 or total_samples == 0:
                logger.warning(f"Audio file {file_path} is too short or empty for lip-sync analysis.")
                return LipSyncTrack([], interval_ms, duration_ms)

            # Compute global peak for normalization
            peak = np.max(np.abs(data))
            if peak > 1e-5:
                normalized_data = data / peak
            else:
                normalized_data = data

            # Responsive noise floor gate for clean speech
            noise_gate = 0.018

            frames: List[VisemeFrame] = []
            num_frames = int(math.ceil(total_samples / samples_per_frame))

            for i in range(num_frames):
                start = i * samples_per_frame
                end = min(start + samples_per_frame, total_samples)
                chunk = normalized_data[start:end]

                if len(chunk) == 0:
                    break

                # 1. Root Mean Square (RMS) energy
                rms = float(np.sqrt(np.mean(chunk ** 2)))

                # 2. Zero-crossing rate (high-frequency consonants / sibilants)
                zero_crossings = np.sum(np.abs(np.diff(np.sign(chunk)))) / (2 * len(chunk))
                time_ms = i * interval_ms

                if rms < noise_gate:
                    # Silence / rest pose
                    frames.append(VisemeFrame(time_ms, 0.0, 0.5, "REST"))
                else:
                    # Speech detected - high-gain non-linear syllable curve
                    scaled_rms = max(0.0, (rms - noise_gate) / 0.20)
                    openness = float(np.clip(math.pow(scaled_rms, 0.60), 0.0, 1.0))

                    # Classify viseme type based on spectral characteristics
                    if zero_crossings > 0.16:
                        # Teeth/wide grin: "ee", "s", "t"
                        viseme_type = "EE"
                        width = float(np.clip(0.65 + openness * 0.35, 0.6, 1.0))
                    elif openness > 0.55 and zero_crossings < 0.08:
                        # Deep rounded vowel: "oo", "oh", "u"
                        viseme_type = "OO"
                        width = float(np.clip(0.30 - (openness * 0.15), 0.1, 0.35))
                    elif openness > 0.30:
                        # Open vowel: "aa", "ah", "father"
                        viseme_type = "AA"
                        width = 0.55
                    elif openness < 0.15:
                        # Bilabial: "m", "b", "p"
                        viseme_type = "MBP"
                        width = 0.50
                    else:
                        viseme_type = "REST"
                        width = 0.50

                    frames.append(VisemeFrame(time_ms, openness, width, viseme_type))

            logger.info(f"LipSyncEngine: Processed {len(frames)} frames for {file_path} ({duration_ms}ms)")
            return LipSyncTrack(frames, interval_ms, duration_ms)

        except Exception as e:
            logger.error(f"Error extracting lip-sync frames from {file_path}: {e}", exc_info=True)
            return None
