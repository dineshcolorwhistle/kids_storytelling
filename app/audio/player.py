"""
Qt Audio Player Wrapper
Wraps QMediaPlayer and QAudioOutput for kid-friendly desktop playback.
"""
import os
from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from app.audio.audio_utils import ensure_compatible_audio
from app.utils.logger import logger

class AudioPlayer(QObject):
    position_changed = Signal(int)     # Current position in milliseconds
    duration_changed = Signal(int)     # Total duration in milliseconds
    state_changed = Signal(str)        # "playing", "paused", "stopped"
    playback_completed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        
        # Default volume 80%
        self.audio_output.setVolume(0.8)
        self.current_file = None

        # Connect internal Qt signals
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)

    def set_video_output(self, video_widget):
        """Connect QVideoWidget to the media player."""
        self.player.setVideoOutput(video_widget)

    def load_file(self, file_path: str) -> bool:
        """Load an audio or video file into the player."""
        if not os.path.exists(file_path):
            logger.error(f"Media file does not exist: {file_path}")
            return False
            
        if file_path.lower().endswith(".mp4"):
            self.current_file = os.path.abspath(file_path)
        else:
            # Ensure audio is 48kHz Stereo 16-bit for speaker & headset compatibility
            self.current_file = ensure_compatible_audio(os.path.abspath(file_path))

        url = QUrl.fromLocalFile(self.current_file)
        self.player.setSource(url)
        logger.info(f"Loaded media into player: {self.current_file}")
        return True

    def play(self):
        """Start or resume playback."""
        self.player.play()

    def pause(self):
        """Pause playback."""
        self.player.pause()

    def stop(self):
        """Stop playback and reset position."""
        self.player.stop()

    def replay(self):
        """Restart playback from the beginning."""
        self.seek(0)
        self.play()

    def seek(self, position_ms: int):
        """Seek to position in milliseconds."""
        self.player.setPosition(position_ms)

    def set_volume(self, percent: int):
        """Set volume 0 to 100."""
        clamped = max(0, min(100, percent))
        self.audio_output.setVolume(clamped / 100.0)

    def is_playing(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def is_paused(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState

    def _on_position_changed(self, position_ms: int):
        self.position_changed.emit(position_ms)
        # Check if reached end
        duration = self.player.duration()
        if duration > 0 and position_ms >= duration:
            self.playback_completed.emit()

    def _on_duration_changed(self, duration_ms: int):
        self.duration_changed.emit(duration_ms)

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.state_changed.emit("playing")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.state_changed.emit("paused")
        else:
            self.state_changed.emit("stopped")
