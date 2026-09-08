"""
Audio Recorder using PySide6.QtMultimedia
Records microphone input to standard WAV files with live timer feedback.
"""
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QTimer, QUrl
from PySide6.QtMultimedia import (
    QMediaCaptureSession, QAudioInput, QMediaRecorder, QMediaFormat, QMediaDevices
)
from app.utils.logger import logger

class AudioRecorder(QObject):
    recording_started = Signal()
    recording_stopped = Signal(str)  # Emits final audio file path
    recording_tick = Signal(int)     # Emits elapsed seconds
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = QMediaCaptureSession(self)
        self.audio_input = QAudioInput(self)
        self.recorder = QMediaRecorder(self)
        
        self.session.setAudioInput(self.audio_input)
        self.session.setRecorder(self.recorder)

        # Configure uncompressed WAV output
        media_format = QMediaFormat()
        media_format.setFileFormat(QMediaFormat.FileFormat.Wave)
        media_format.setAudioCodec(QMediaFormat.AudioCodec.Wave)
        self.recorder.setMediaFormat(media_format)
        self.recorder.setQuality(QMediaRecorder.Quality.HighQuality)

        # Elapsed Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)
        self.elapsed_seconds = 0
        self.current_output_path = None

        # Recorder Signals
        self.recorder.errorOccurred.connect(self._on_recorder_error)

    def is_microphone_available(self) -> bool:
        """Check if at least one audio input device exists."""
        devices = QMediaDevices.audioInputs()
        return len(devices) > 0

    def start_recording(self, output_path: str) -> bool:
        """Start microphone capture to destination file."""
        if not self.is_microphone_available():
            err_msg = "No microphone detected on your system. Please plug in a microphone and check Windows settings."
            logger.error(err_msg)
            self.error_occurred.emit(err_msg)
            return False

        try:
            self.current_output_path = os.path.abspath(output_path)
            Path(self.current_output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Remove old file if exists
            if os.path.exists(self.current_output_path):
                os.remove(self.current_output_path)

            self.recorder.setOutputLocation(QUrl.fromLocalFile(self.current_output_path))
            self.recorder.record()
            
            self.elapsed_seconds = 0
            self.timer.start()
            self.recording_started.emit()
            logger.info(f"Started audio recording to: {self.current_output_path}")
            return True
        except Exception as e:
            err_msg = f"Failed to start recording: {e}"
            logger.error(err_msg)
            self.error_occurred.emit(err_msg)
            return False

    def stop_recording(self) -> str:
        """Stop recording and return finalized file path."""
        self.timer.stop()
        self.recorder.stop()
        logger.info(f"Stopped recording. Total duration: {self.elapsed_seconds}s. File: {self.current_output_path}")
        self.recording_stopped.emit(self.current_output_path)
        return self.current_output_path

    def is_recording(self) -> bool:
        return self.recorder.recorderState() == QMediaRecorder.RecorderState.RecordingState

    def _on_tick(self):
        self.elapsed_seconds += 1
        self.recording_tick.emit(self.elapsed_seconds)

    def _on_recorder_error(self, error, error_string):
        logger.error(f"QMediaRecorder error ({error}): {error_string}")
        self.error_occurred.emit(f"Microphone recording error: {error_string}")
