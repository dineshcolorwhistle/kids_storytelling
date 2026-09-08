"""
Story Player View
Full-screen, kid-friendly audio player with large controls, progress scrubber, and volume slider.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QFrame
)
from PySide6.QtCore import Signal, Qt
from app.audio.player import AudioPlayer
from app.database.models import Story
from app.utils.logger import logger

def format_time(ms: int) -> str:
    """Format milliseconds as MM:SS."""
    seconds = max(0, ms // 1000)
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

class StoryPlayerView(QWidget):
    back_to_library_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = AudioPlayer(self)
        self.story = None
        self.is_slider_down = False
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 24)
        layout.setSpacing(18)

        # Top Bar: Back Button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Stories")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: #EDF2F7;
                color: #4A5568;
                font-weight: 700;
                font-size: 14px;
                border-radius: 10px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        self.back_btn.clicked.connect(self._on_back_clicked)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Player Container Card
        card = QFrame()
        card.setObjectName("playerCard")
        card.setStyleSheet("""
            QFrame#playerCard {
                background: #FFFFFF;
                border-radius: 24px;
                border: 2px solid #E2E8F0;
                padding: 24px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        # Hero Character Art / Icon
        self.hero_icon = QLabel("🎧")
        self.hero_icon.setStyleSheet("font-size: 72px; margin-top: 10px;")
        self.hero_icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.hero_icon)

        # Story Title
        self.title_label = QLabel("Story Title")
        self.title_label.setObjectName("appTitle")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: 800; color: #2D3748; padding: 0;")
        self.title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.title_label)

        # Narrator Badge
        self.narrator_label = QLabel("Narrator: Default Voice")
        self.narrator_label.setStyleSheet("""
            background-color: #EBF8FF;
            color: #2B6CB0;
            font-size: 14px;
            font-weight: 700;
            border-radius: 12px;
            padding: 6px 16px;
        """)
        self.narrator_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.narrator_label)

        card_layout.addSpacing(10)

        # Scrubber Section (Time & Slider)
        scrubber_layout = QVBoxLayout()
        scrubber_layout.setSpacing(6)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setCursor(Qt.PointingHandCursor)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px;
                background: #EDF2F7;
                border-radius: 5px;
            }
            QSlider::sub-page:horizontal {
                background: #48BB78;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #38A169;
                border: 2px solid #FFFFFF;
                width: 22px;
                height: 22px;
                margin: -6px 0;
                border-radius: 11px;
            }
            QSlider::handle:horizontal:hover {
                background: #2F855A;
            }
        """)
        scrubber_layout.addWidget(self.progress_slider)

        # Time Labels
        time_layout = QHBoxLayout()
        self.elapsed_time_label = QLabel("00:00")
        self.elapsed_time_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #718096;")
        time_layout.addWidget(self.elapsed_time_label)
        time_layout.addStretch()

        self.total_time_label = QLabel("00:00")
        self.total_time_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #718096;")
        time_layout.addWidget(self.total_time_label)

        scrubber_layout.addLayout(time_layout)
        card_layout.addLayout(scrubber_layout)

        card_layout.addSpacing(10)

        # Main Playback Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        controls_layout.setAlignment(Qt.AlignCenter)

        # Replay Button
        self.replay_btn = QPushButton("↺ Replay")
        self.replay_btn.setCursor(Qt.PointingHandCursor)
        self.replay_btn.setStyleSheet("""
            QPushButton {
                background: #EDF2F7;
                color: #2D3748;
                font-size: 16px;
                font-weight: 700;
                border-radius: 14px;
                padding: 12px 20px;
                border: none;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        self.replay_btn.clicked.connect(self.player.replay)
        controls_layout.addWidget(self.replay_btn)

        # Play / Pause Primary Button
        self.play_pause_btn = QPushButton("⏸ Pause")
        self.play_pause_btn.setCursor(Qt.PointingHandCursor)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: #FFFFFF;
                font-size: 20px;
                font-weight: 800;
                border-radius: 18px;
                padding: 14px 36px;
                border: none;
            }
            QPushButton:hover { background-color: #38A169; }
            QPushButton:pressed { background-color: #2F855A; }
        """)
        self.play_pause_btn.clicked.connect(self._toggle_play_pause)
        controls_layout.addWidget(self.play_pause_btn)

        # Stop Button
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #FED7D7;
                color: #C53030;
                font-size: 16px;
                font-weight: 700;
                border-radius: 14px;
                padding: 12px 20px;
                border: none;
            }
            QPushButton:hover { background: #FEB2B2; }
        """)
        self.stop_btn.clicked.connect(self.player.stop)
        controls_layout.addWidget(self.stop_btn)

        card_layout.addLayout(controls_layout)

        card_layout.addSpacing(10)

        # Volume Row
        volume_layout = QHBoxLayout()
        volume_layout.setAlignment(Qt.AlignCenter)
        volume_layout.setSpacing(12)

        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("font-size: 18px;")
        volume_layout.addWidget(vol_icon)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(140)
        self.volume_slider.valueChanged.connect(self.player.set_volume)
        volume_layout.addWidget(self.volume_slider)

        card_layout.addLayout(volume_layout)
        layout.addWidget(card)

    def _connect_signals(self):
        # Player signals
        self.player.position_changed.connect(self._on_player_position_changed)
        self.player.duration_changed.connect(self._on_player_duration_changed)
        self.player.state_changed.connect(self._on_player_state_changed)
        self.player.playback_completed.connect(self._on_playback_completed)

        # Slider interaction
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)

    def play_story(self, story: Story, audio_path: str, voice_name: str = "Default AI Voice"):
        """Load and start playing the story."""
        self.story = story
        self.title_label.setText(story.title)
        self.narrator_label.setText(f"Narrator: {voice_name}")
        
        # Load audio into backend
        if self.player.load_file(audio_path):
            self.player.play()
        else:
            logger.error(f"Failed to play audio from {audio_path}")

    def _toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def _on_player_position_changed(self, pos_ms: int):
        if not self.is_slider_down:
            self.progress_slider.setValue(pos_ms)
        self.elapsed_time_label.setText(format_time(pos_ms))

    def _on_player_duration_changed(self, duration_ms: int):
        self.progress_slider.setRange(0, duration_ms)
        self.total_time_label.setText(format_time(duration_ms))

    def _on_player_state_changed(self, state: str):
        if state == "playing":
            self.play_pause_btn.setText("⏸ Pause")
            self.play_pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ED8936;
                    color: #FFFFFF;
                    font-size: 20px;
                    font-weight: 800;
                    border-radius: 18px;
                    padding: 14px 36px;
                    border: none;
                }
                QPushButton:hover { background-color: #DD6B20; }
            """)
        else:
            self.play_pause_btn.setText("▶ Play")
            self.play_pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #48BB78;
                    color: #FFFFFF;
                    font-size: 20px;
                    font-weight: 800;
                    border-radius: 18px;
                    padding: 14px 36px;
                    border: none;
                }
                QPushButton:hover { background-color: #38A169; }
            """)

    def _on_playback_completed(self):
        self.play_pause_btn.setText("▶ Play Again")

    def _on_slider_pressed(self):
        self.is_slider_down = True

    def _on_slider_released(self):
        self.is_slider_down = False
        self.player.seek(self.progress_slider.value())

    def _on_back_clicked(self):
        self.player.stop()
        self.back_to_library_clicked.emit()
