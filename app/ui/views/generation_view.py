"""
Generation View (Screen 6)
Kid-friendly animated progress screen displayed while AI synthesizes audio in the background.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QFrame, QPushButton
)
from PySide6.QtCore import Signal, Qt, QTimer
from app.database.models import Story, VoiceProfile
from app.services.generation_worker import GenerationWorker
from app.utils.logger import logger

class GenerationView(QWidget):
    generation_succeeded = Signal(object, str, str)  # story, audio_path, voice_name
    generation_aborted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.story = None
        self.voice_profile = None
        self.elapsed_seconds = 0

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("generationCard")
        card.setStyleSheet("""
            QFrame#generationCard {
                background: #FFFFFF;
                border-radius: 28px;
                border: 2px solid #E2E8F0;
                padding: 40px;
                max-width: 600px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)

        # Magic Storytelling Graphic
        self.magic_icon = QLabel("🪄")
        self.magic_icon.setStyleSheet("font-size: 80px; margin-bottom: 10px;")
        self.magic_icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.magic_icon)

        # Main Title
        self.title_label = QLabel("Creating your story...")
        self.title_label.setObjectName("appTitle")
        self.title_label.setStyleSheet("font-size: 28px; font-weight: 800; color: #4C51BF;")
        self.title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.title_label)

        # Subtitle with Voice Name
        self.voice_label = QLabel("Using Dad's Voice")
        self.voice_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #2B6CB0;")
        self.voice_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.voice_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(10)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(22)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 11px;
                background-color: #EDF2F7;
                text-align: center;
                font-weight: 700;
                color: #2D3748;
            }
            QProgressBar::chunk {
                background-color: #48BB78;
                border-radius: 11px;
            }
        """)
        card_layout.addWidget(self.progress_bar)

        # Status and Timer Row
        status_row = QHBoxLayout()
        self.status_text = QLabel("Starting AI narrator...")
        self.status_text.setStyleSheet("font-size: 14px; font-weight: 600; color: #718096;")
        status_row.addWidget(self.status_text)
        status_row.addStretch()

        self.timer_label = QLabel("⏱️ 00:00")
        self.timer_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #4A5568;")
        status_row.addWidget(self.timer_label)

        card_layout.addLayout(status_row)

        # Friendly Notice
        tip_label = QLabel("💡 Tip: AI voice cloning runs directly on your PC. Once finished, this story will replay instantly!")
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet("font-size: 13px; color: #A0AEC0; margin-top: 10px; text-align: center;")
        tip_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(tip_label)

        layout.addWidget(card)

    def start_generation(self, story: Story, voice_profile: VoiceProfile):
        """Start the background generation thread."""
        self.story = story
        self.voice_profile = voice_profile
        self.voice_label.setText(f"Using {voice_profile.name}")
        self.progress_bar.setValue(5)
        self.status_text.setText("Starting speech generation...")
        
        self.elapsed_seconds = 0
        self.timer_label.setText("⏱️ 00:00")
        self.timer.start()

        self.worker = GenerationWorker(story, voice_profile, self)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.generation_finished.connect(self._on_finished)
        self.worker.generation_failed.connect(self._on_failed)
        self.worker.start()

    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.status_text.setText(message)

    def _on_tick(self):
        self.elapsed_seconds += 1
        mins = self.elapsed_seconds // 60
        secs = self.elapsed_seconds % 60
        self.timer_label.setText(f"⏱️ {mins:02d}:{secs:02d}")

    def _on_finished(self, audio_path: str):
        self.timer.stop()
        logger.info(f"Generation view received finished signal with {audio_path}")
        self.generation_succeeded.emit(self.story, audio_path, self.voice_profile.name)

    def _on_failed(self, error_message: str):
        self.timer.stop()
        self.status_text.setText(f"Error: {error_message}")
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Generation Failed", error_message)
        self.generation_aborted.emit()
