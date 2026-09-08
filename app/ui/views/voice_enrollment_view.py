"""
Voice Enrollment View
Allows an adult to record a 20-30s voice reference sample, preview it, and save a VoiceProfile.
"""
import os
import tempfile
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTextEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from app.audio.recorder import AudioRecorder
from app.audio.player import AudioPlayer
from app.services.voice_service import VoiceService, MIN_RECORDING_DURATION_SEC
from app.utils.logger import logger

READING_PROMPT = (
    "Hello! I am going to tell you a wonderful story. "
    "Once upon a time, there was a little rabbit. "
    "The rabbit loved exploring the beautiful forest, "
    "sniffing fresh flowers and watching butterflies dance in the warm sunshine. "
    "Every day was a brand new adventure filled with laughter, wonder, and joy."
)

class VoiceEnrollmentView(QWidget):
    voice_saved = Signal(object)      # Emits newly created VoiceProfile
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recorder = AudioRecorder(self)
        self.player = AudioPlayer(self)
        self.temp_audio_path = os.path.join(tempfile.gettempdir(), "temp_voice_sample.wav")
        self.has_recorded = False

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 24)
        layout.setSpacing(16)

        # Top Bar: Back / Cancel
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Cancel")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: #EDF2F7;
                color: #4A5568;
                font-weight: 700;
                border-radius: 10px;
                padding: 6px 14px;
                border: none;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        self.back_btn.clicked.connect(self._on_cancel)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Header Title
        title = QLabel("🎙️ Create My Voice")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        subtitle = QLabel("Record your voice once so the app can narrate stories in your voice!")
        subtitle.setObjectName("appSubtitle")
        layout.addWidget(subtitle)

        # Reading Prompt Card
        card = QFrame()
        card.setObjectName("promptCard")
        card.setStyleSheet("""
            QFrame#promptCard {
                background: #FFFFFF;
                border-radius: 16px;
                border: 2px solid #CBD5E0;
                padding: 16px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        card_title = QLabel("Please read the following aloud in a clear, natural voice:")
        card_title.setStyleSheet("font-weight: 700; color: #4C51BF; font-size: 14px;")
        card_layout.addWidget(card_title)

        prompt_box = QTextEdit()
        prompt_box.setReadOnly(True)
        prompt_box.setText(READING_PROMPT)
        prompt_box.setStyleSheet("""
            QTextEdit {
                background: #F7FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
                line-height: 1.6;
                color: #2D3748;
            }
        """)
        card_layout.addWidget(prompt_box)
        layout.addWidget(card)

        # Timer and Status Display
        status_box = QHBoxLayout()
        self.status_label = QLabel("Ready to record (Target: 20–30 seconds)")
        self.status_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #718096;")
        status_box.addWidget(self.status_label)

        status_box.addStretch()

        self.timer_label = QLabel("⏱️ 00:00")
        self.timer_label.setStyleSheet("""
            background: #EDF2F7;
            color: #2D3748;
            font-size: 16px;
            font-weight: 800;
            border-radius: 12px;
            padding: 6px 16px;
        """)
        status_box.addWidget(self.timer_label)
        layout.addLayout(status_box)

        # Action Buttons (Start / Stop / Play Preview / Record Again)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.record_btn = QPushButton("🎙️ Start Recording")
        self.record_btn.setCursor(Qt.PointingHandCursor)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 800;
                border-radius: 14px;
                padding: 12px 24px;
                border: none;
            }
            QPushButton:hover { background-color: #C53030; }
        """)
        self.record_btn.clicked.connect(self._on_record_clicked)
        btn_layout.addWidget(self.record_btn)

        self.preview_btn = QPushButton("▶ Play Recording")
        self.preview_btn.setEnabled(False)
        self.preview_btn.setCursor(Qt.PointingHandCursor)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: 700;
                border-radius: 14px;
                padding: 12px 20px;
                border: none;
            }
            QPushButton:hover { background-color: #3182CE; }
            QPushButton:disabled { background-color: #CBD5E0; color: #A0AEC0; }
        """)
        self.preview_btn.clicked.connect(self._on_preview_clicked)
        btn_layout.addWidget(self.preview_btn)

        self.rerecord_btn = QPushButton("↺ Record Again")
        self.rerecord_btn.setEnabled(False)
        self.rerecord_btn.setCursor(Qt.PointingHandCursor)
        self.rerecord_btn.setStyleSheet("""
            QPushButton {
                background: #EDF2F7;
                color: #4A5568;
                font-size: 15px;
                font-weight: 700;
                border-radius: 14px;
                padding: 12px 20px;
                border: none;
            }
            QPushButton:hover { background: #E2E8F0; }
            QPushButton:disabled { background: #F7FAFC; color: #CBD5E0; }
        """)
        self.rerecord_btn.clicked.connect(self._on_rerecord_clicked)
        btn_layout.addWidget(self.rerecord_btn)

        layout.addLayout(btn_layout)

        # Profile Name Input Box & Save Button
        save_card = QFrame()
        save_card.setObjectName("saveCard")
        save_card.setStyleSheet("""
            QFrame#saveCard {
                background: #FFFFFF;
                border-radius: 16px;
                border: 2px solid #E2E8F0;
                padding: 16px;
            }
        """)
        save_layout = QHBoxLayout(save_card)
        save_layout.setSpacing(14)

        name_label = QLabel("Voice Name:")
        name_label.setStyleSheet("font-weight: 700; font-size: 15px; color: #2D3748;")
        save_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Dad's Voice, Mom, Grandpa")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 15px;
                color: #2D3748;
            }
            QLineEdit:focus { border: 2px solid #667EEA; }
        """)
        save_layout.addWidget(self.name_input, stretch=1)

        self.save_btn = QPushButton("💾 Save Voice")
        self.save_btn.setEnabled(False)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 800;
                border-radius: 12px;
                padding: 10px 24px;
                border: none;
            }
            QPushButton:hover { background-color: #38A169; }
            QPushButton:disabled { background-color: #CBD5E0; color: #A0AEC0; }
        """)
        self.save_btn.clicked.connect(self._on_save_clicked)
        save_layout.addWidget(self.save_btn)

        layout.addWidget(save_card)

    def _connect_signals(self):
        self.recorder.recording_tick.connect(self._on_tick)
        self.recorder.error_occurred.connect(self._on_recorder_error)

    def _on_record_clicked(self):
        if not self.recorder.is_recording():
            success = self.recorder.start_recording(self.temp_audio_path)
            if success:
                self.record_btn.setText("⏹️ Stop Recording")
                self.record_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #C53030;
                        color: #FFFFFF;
                        font-size: 16px;
                        font-weight: 800;
                        border-radius: 14px;
                        padding: 12px 24px;
                        border: none;
                    }
                """)
                self.status_label.setText("Recording in progress... Speak clearly.")
                self.status_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #E53E3E;")
                self.preview_btn.setEnabled(False)
                self.rerecord_btn.setEnabled(False)
                self.save_btn.setEnabled(False)
        else:
            self.recorder.stop_recording()
            self.record_btn.setText("🎙️ Start Recording")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E53E3E;
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 800;
                    border-radius: 14px;
                    padding: 12px 24px;
                    border: none;
                }
            """)
            self.has_recorded = True
            self.preview_btn.setEnabled(True)
            self.rerecord_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            elapsed = self.recorder.elapsed_seconds
            if elapsed >= MIN_RECORDING_DURATION_SEC:
                self.status_label.setText(f"Great recording! Duration: {elapsed} seconds.")
                self.status_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #38A169;")
            else:
                self.status_label.setText(f"Recording is short ({elapsed}s). Recommended: 20-30s.")
                self.status_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #D69E2E;")

    def _on_tick(self, seconds: int):
        mins = seconds // 60
        secs = seconds % 60
        self.timer_label.setText(f"⏱️ {mins:02d}:{secs:02d}")
        if seconds >= 20:
            self.timer_label.setStyleSheet("""
                background: #C6F6D5;
                color: #22543D;
                font-size: 16px;
                font-weight: 800;
                border-radius: 12px;
                padding: 6px 16px;
            """)

    def _on_preview_clicked(self):
        if self.player.is_playing():
            self.player.stop()
            self.preview_btn.setText("▶ Play Recording")
        else:
            if self.player.load_file(self.temp_audio_path):
                self.player.play()
                self.preview_btn.setText("⏹️ Stop Preview")
                self.player.playback_completed.connect(lambda: self.preview_btn.setText("▶ Play Recording"))

    def _on_rerecord_clicked(self):
        if self.player.is_playing():
            self.player.stop()
        self.timer_label.setText("⏱️ 00:00")
        self.timer_label.setStyleSheet("""
            background: #EDF2F7;
            color: #2D3748;
            font-size: 16px;
            font-weight: 800;
            border-radius: 12px;
            padding: 6px 16px;
        """)
        self.status_label.setText("Ready to re-record (Target: 20–30 seconds)")
        self.status_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #718096;")
        self.has_recorded = False
        self.preview_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.rerecord_btn.setEnabled(False)

    def _on_save_clicked(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a name for this voice profile (e.g. 'Dad's Voice').")
            return

        success, msg, profile = VoiceService.create_voice_profile(name, self.temp_audio_path)
        if success:
            QMessageBox.information(self, "Voice Saved", f"'{name}' has been saved successfully!")
            self.name_input.clear()
            self._on_rerecord_clicked()
            self.voice_saved.emit(profile)
        else:
            QMessageBox.warning(self, "Save Failed", msg)

    def _on_recorder_error(self, message: str):
        QMessageBox.critical(self, "Microphone Error", message)

    def _on_cancel(self):
        if self.recorder.is_recording():
            self.recorder.stop_recording()
        if self.player.is_playing():
            self.player.stop()
        self.back_clicked.emit()
