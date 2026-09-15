"""
Story Player View
Full-screen, kid-friendly audio player with large controls, progress scrubber, and volume slider.
"""
import os
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from app.audio.player import AudioPlayer
from app.audio.lip_sync_engine import LipSyncEngine, LipSyncTrack
from app.ui.widgets.avatar_video_widget import AvatarVideoWidget
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
        self.lip_sync_track: Optional[LipSyncTrack] = None
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 24, 40, 24)
        layout.setSpacing(18)

        # Top Bar: Back Button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Stories")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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

        # Player Container Card (Horizontal Two-Column Layout)
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
        card_layout = QHBoxLayout(card)
        card_layout.setSpacing(24)
        card_layout.setContentsMargins(16, 16, 16, 16)

        # ==========================================================
        # LEFT COLUMN (60%): Story Info, Read-Along Text & Controls
        # ==========================================================
        left_column = QVBoxLayout()
        left_column.setSpacing(14)

        # Header: Title & Narrator Tag
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        self.title_label = QLabel("Story Title")
        self.title_label.setObjectName("appTitle")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 800; color: #2D3748; padding: 0;")
        header_layout.addWidget(self.title_label)

        self.narrator_label = QLabel("Narrator: Default Voice")
        self.narrator_label.setStyleSheet("""
            background-color: #EBF8FF;
            color: #2B6CB0;
            font-size: 13px;
            font-weight: 700;
            border-radius: 10px;
            padding: 4px 14px;
        """)
        self.narrator_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(self.narrator_label)
        left_column.addLayout(header_layout)

        # Story Read-Along Card
        text_frame = QFrame()
        text_frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1.5px solid #EDF2F7;
                border-radius: 16px;
                padding: 12px;
            }
        """)
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(10, 8, 10, 8)

        self.story_text_label = QLabel("Story text content...")
        self.story_text_label.setWordWrap(True)
        self.story_text_label.setStyleSheet("""
            font-size: 14px;
            line-height: 1.5;
            color: #4A5568;
            font-weight: 500;
        """)
        text_layout.addWidget(self.story_text_label)
        left_column.addWidget(text_frame, 1)

        # Scrubber Section (Time & Slider)
        scrubber_layout = QVBoxLayout()
        scrubber_layout.setSpacing(6)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setCursor(Qt.CursorShape.PointingHandCursor)
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
        left_column.addLayout(scrubber_layout)

        # Controls & Volume Row
        controls_and_vol = QHBoxLayout()
        controls_and_vol.setSpacing(16)

        # Playback Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        self.replay_btn = QPushButton("↺ Replay")
        self.replay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.replay_btn.setStyleSheet("""
            QPushButton {
                background: #EDF2F7;
                color: #2D3748;
                font-size: 15px;
                font-weight: 700;
                border-radius: 12px;
                padding: 10px 18px;
                border: none;
            }
            QPushButton:hover { background: #E2E8F0; }
        """)
        self.replay_btn.clicked.connect(self.player.replay)
        controls_layout.addWidget(self.replay_btn)

        self.play_pause_btn = QPushButton("⏸ Pause")
        self.play_pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 800;
                border-radius: 16px;
                padding: 12px 30px;
                border: none;
            }
            QPushButton:hover { background-color: #38A169; }
            QPushButton:pressed { background-color: #2F855A; }
        """)
        self.play_pause_btn.clicked.connect(self._toggle_play_pause)
        controls_layout.addWidget(self.play_pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #FED7D7;
                color: #C53030;
                font-size: 15px;
                font-weight: 700;
                border-radius: 12px;
                padding: 10px 18px;
                border: none;
            }
            QPushButton:hover { background: #FEB2B2; }
        """)
        self.stop_btn.clicked.connect(self.player.stop)
        controls_layout.addWidget(self.stop_btn)

        controls_and_vol.addLayout(controls_layout)
        controls_and_vol.addStretch()

        # Volume Slider
        vol_layout = QHBoxLayout()
        vol_layout.setSpacing(8)
        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("font-size: 16px;")
        vol_layout.addWidget(vol_icon)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(110)
        self.volume_slider.valueChanged.connect(self.player.set_volume)
        vol_layout.addWidget(self.volume_slider)

        controls_and_vol.addLayout(vol_layout)
        left_column.addLayout(controls_and_vol)

        # ==========================================================
        # RIGHT COLUMN (40% / Right Corner): 3D Video Avatar Stage
        # ==========================================================
        right_column = QVBoxLayout()
        right_column.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar_stage = AvatarVideoWidget(self)
        self.player.set_video_output(self.avatar_stage.get_video_widget())
        right_column.addWidget(self.avatar_stage)

        card_layout.addLayout(left_column, stretch=3)
        card_layout.addLayout(right_column, stretch=2)

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
        """Load and start playing the story with synchronized 3D video avatar."""
        self.story = story
        self.title_label.setText(story.title)
        self.narrator_label.setText(f"Narrator: {voice_name}")
        self.story_text_label.setText(story.content)
        self.avatar_stage.set_narrator_name(voice_name)
        
        # Check if 3D animated video exists
        default_video = "data/avatars/barnaby_3d_storyteller.mp4"
        media_to_play = default_video if os.path.exists(default_video) else audio_path
        
        # Load media into player
        if self.player.load_file(media_to_play):
            self.player.play()
            self.avatar_stage.set_speaking_state(True)
        else:
            logger.error(f"Failed to play media from {media_to_play}")

    def _toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def _on_player_position_changed(self, pos_ms: int):
        if not self.is_slider_down:
            self.progress_slider.setValue(pos_ms)
        self.elapsed_time_label.setText(format_time(pos_ms))

        # Update lip-sync avatar frame in real time
        if self.lip_sync_track and self.player.is_playing():
            frame = self.lip_sync_track.get_frame(pos_ms)
            self.avatar_stage.set_viseme_frame(frame)

    def _on_player_duration_changed(self, duration_ms: int):
        self.progress_slider.setRange(0, duration_ms)
        self.total_time_label.setText(format_time(duration_ms))

    def _on_player_state_changed(self, state: str):
        if state == "playing":
            self.avatar_stage.set_speaking_state(True)
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
            self.avatar_stage.set_speaking_state(False)
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
        self.avatar_stage.reset_avatar()
        self.play_pause_btn.setText("▶ Play Again")

    def _on_slider_pressed(self):
        self.is_slider_down = True

    def _on_slider_released(self):
        self.is_slider_down = False
        seek_pos = self.progress_slider.value()
        self.player.seek(seek_pos)
        if self.lip_sync_track:
            self.lip_sync_track.reset_smoothing()
            self.avatar_stage.set_viseme_frame(self.lip_sync_track.get_frame(seek_pos))

    def _on_back_clicked(self):
        self.player.stop()
        self.avatar_stage.reset_avatar()
        self.back_to_library_clicked.emit()
