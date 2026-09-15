"""
3D Animated Video Avatar Widget
Hosts PySide6.QtMultimediaWidgets.QVideoWidget to render genuine 3D Pixar CGI
animated video of Barnaby Bear reading the story in lockstep with the audio.
"""
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QStackedLayout, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtMultimediaWidgets import QVideoWidget

class AvatarVideoWidget(QWidget):
    """
    Renders 3D Pixar Barnaby Bear using hardware-accelerated video playback
    via QVideoWidget in the right corner of the story player.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 270)
        self.setMaximumWidth(320)
        self.setMaximumHeight(350)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Outer Rounded Card Container
        self.card = QFrame()
        self.card.setObjectName("avatarVideoCard")
        self.card.setStyleSheet("""
            QFrame#avatarVideoCard {
                background: #1A202C;
                border-radius: 20px;
                border: 2.5px solid #E2E8F0;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(4, 4, 4, 4)
        card_layout.setSpacing(0)

        # Stacked display: VideoWidget + Poster fallback
        self.stack = QStackedLayout()
        self.stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # 1. Hardware-accelerated Video Widget
        self.video_widget = QVideoWidget(self.card)
        self.video_widget.setStyleSheet("""
            background-color: transparent;
            border-radius: 16px;
        """)
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.stack.addWidget(self.video_widget)

        # 2. High-res 3D Pixar Poster (shown when stopped/paused)
        self.poster_label = QLabel(self.card)
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster_label.setStyleSheet("""
            background-color: transparent;
            border-radius: 16px;
        """)
        poster_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\802a9d26-1236-4a7c-91ee-c0ada0de8356\sample_3d_avatar_animal_1789368460060.jpg"
        if os.path.exists(poster_path):
            pix = QPixmap(poster_path)
            self.poster_label.setPixmap(pix.scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.stack.addWidget(self.poster_label)
        card_layout.addLayout(self.stack)
        main_layout.addWidget(self.card)

        # Status Badge below video card
        self.status_badge = QLabel("📖 Ready for Story")
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setStyleSheet("""
            background-color: #2D3748;
            color: #F7FAFC;
            font-size: 13px;
            font-weight: 700;
            border-radius: 12px;
            padding: 6px 14px;
        """)
        main_layout.addWidget(self.status_badge)

    def get_video_widget(self) -> QVideoWidget:
        """Return the QVideoWidget to connect with QMediaPlayer."""
        return self.video_widget

    def set_speaking_state(self, is_playing: bool):
        """Update visual state when media plays or pauses."""
        if is_playing:
            # Video is playing: hide static poster so live video shows
            self.poster_label.setVisible(False)
            self.card.setStyleSheet("""
                QFrame#avatarVideoCard {
                    background: #1A202C;
                    border-radius: 20px;
                    border: 2.5px solid #48BB78;
                }
            """)
            self.status_badge.setText("✨ Barnaby 3D Reading to You...")
            self.status_badge.setStyleSheet("""
                background-color: #276749;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 700;
                border-radius: 12px;
                padding: 6px 14px;
            """)
        else:
            self.status_badge.setText("📖 Ready for Story")
            self.status_badge.setStyleSheet("""
                background-color: #2D3748;
                color: #F7FAFC;
                font-size: 13px;
                font-weight: 700;
                border-radius: 12px;
                padding: 6px 14px;
            """)

    def reset_avatar(self):
        """Reset avatar back to poster / rest pose."""
        self.poster_label.setVisible(True)
        self.set_speaking_state(False)

    def set_narrator_name(self, name: str):
        pass

    def set_lip_sync_track(self, track):
        pass

    def set_viseme_frame(self, frame):
        pass
