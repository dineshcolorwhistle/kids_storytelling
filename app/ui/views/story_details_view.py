"""
Story Details View
Displays story overview, text preview, dynamic voice profile selection, and generation trigger.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QFrame, QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from app.database.models import Story, VoiceProfile
from app.services.voice_service import VoiceService
from app.utils.logger import logger

class StoryDetailsView(QWidget):
    back_clicked = Signal()
    record_new_voice_clicked = Signal()
    play_requested = Signal(object, int)  # Emits (Story, voice_profile_id)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.story = None
        self.voice_buttons = {}
        self.selected_voice_id = 1
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(16)

        # Top Bar: Back Button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Stories")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.back_btn.clicked.connect(self.back_clicked.emit)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Title & Duration
        title_row = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("appTitle")
        title_row.addWidget(self.title_label, stretch=1)

        self.duration_badge = QLabel()
        self.duration_badge.setObjectName("durationBadge")
        title_row.addWidget(self.duration_badge)
        layout.addLayout(title_row)

        # Description
        self.desc_label = QLabel()
        self.desc_label.setObjectName("cardDescription")
        self.desc_label.setStyleSheet("font-size: 15px; color: #4A5568;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        # Story Content Box
        content_header = QLabel("Story Script:")
        content_header.setStyleSheet("font-weight: 700; color: #4C51BF; font-size: 14px;")
        layout.addWidget(content_header)

        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setStyleSheet("""
            QTextEdit {
                background: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 12px;
                font-size: 15px;
                line-height: 1.6;
                color: #2D3748;
            }
        """)
        layout.addWidget(self.content_text, stretch=1)

        # Voice Selection Box
        self.voice_box = QFrame()
        self.voice_box.setObjectName("voiceBox")
        self.voice_box.setStyleSheet("""
            QFrame#voiceBox {
                background: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 14px;
                padding: 14px;
            }
        """)
        self.voice_layout = QVBoxLayout(self.voice_box)
        self.voice_layout.setSpacing(10)

        # Header with "+ Record New Voice" Button
        vh_layout = QHBoxLayout()
        voice_title = QLabel("Choose Narrator Voice:")
        voice_title.setStyleSheet("font-weight: 700; color: #2D3748; font-size: 15px;")
        vh_layout.addWidget(voice_title)
        vh_layout.addStretch()

        self.record_btn = QPushButton("🎙️ + Record New Voice")
        self.record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: #EBF4FF;
                color: #3182CE;
                font-weight: 700;
                font-size: 13px;
                border-radius: 8px;
                padding: 6px 12px;
                border: 1px solid #BEE3F8;
            }
            QPushButton:hover { background: #BEE3F8; }
        """)
        self.record_btn.clicked.connect(self.record_new_voice_clicked.emit)
        vh_layout.addWidget(self.record_btn)
        self.voice_layout.addLayout(vh_layout)

        # Radio button container
        self.radios_container = QWidget()
        self.radios_layout = QVBoxLayout(self.radios_container)
        self.radios_layout.setContentsMargins(0, 4, 0, 0)
        self.radios_layout.setSpacing(8)
        self.voice_layout.addWidget(self.radios_container)

        self.voice_group = QButtonGroup(self)
        self.voice_group.idToggled.connect(self._on_voice_toggled)
        layout.addWidget(self.voice_box)

        # Play Action Button
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.play_btn = QPushButton("▶ Generate & Listen")
        self.play_btn.setObjectName("primaryButton")
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 800;
                border-radius: 16px;
                padding: 14px 32px;
                border: none;
            }
            QPushButton:hover { background-color: #38A169; }
            QPushButton:pressed { background-color: #2F855A; }
        """)
        self.play_btn.clicked.connect(self._on_play_clicked)
        action_layout.addWidget(self.play_btn)

        layout.addLayout(action_layout)
        self.refresh_voices()

    def _on_voice_toggled(self, voice_id: int, checked: bool):
        if checked:
            self.selected_voice_id = voice_id

    def refresh_voices(self, select_profile_id: Optional[int] = None):
        """Populate voice profiles from database with delete options for custom profiles."""
        if select_profile_id is not None:
            self.selected_voice_id = select_profile_id

        # Clear existing buttons from voice_group
        for btn in self.voice_group.buttons():
            self.voice_group.removeButton(btn)

        # Clear layout recursively
        while self.radios_layout.count():
            item = self.radios_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        while sub_layout.count():
                            sub_item = sub_layout.takeAt(0)
                            if sub_item is not None:
                                sub_widget = sub_item.widget()
                                if sub_widget is not None:
                                    sub_widget.deleteLater()

        voices = VoiceService.get_all_voices()
        voice_ids = [v.id for v in voices]

        # If current selected_voice_id no longer exists, fallback to default (ID 1)
        if self.selected_voice_id not in voice_ids:
            self.selected_voice_id = 1

        for idx, voice in enumerate(voices):
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(8)

            if voice.is_default:
                label = f"⭐ {voice.name} (Pre-generated • Instant)"
            else:
                label = f"🎙️ {voice.name} (Custom Cloned Voice)"

            radio = QRadioButton(label)
            radio.setStyleSheet("font-size: 14px; font-weight: 600; color: #2D3748;")
            row_layout.addWidget(radio, stretch=1)
            if voice.id is not None:
                self.voice_group.addButton(radio, voice.id)

            if not voice.is_default:
                del_btn = QPushButton("🗑️ Delete")
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.setToolTip(f"Delete voice '{voice.name}'")
                del_btn.setStyleSheet("""
                    QPushButton {
                        background: #FFF5F5;
                        color: #E53E3E;
                        font-size: 12px;
                        font-weight: 700;
                        border: 1px solid #FEB2B2;
                        border-radius: 6px;
                        padding: 3px 10px;
                    }
                    QPushButton:hover {
                        background: #FED7D7;
                        border-color: #E53E3E;
                    }
                    QPushButton:pressed {
                        background: #FEB2B2;
                    }
                """)
                # Capture current voice profile via default argument
                del_btn.clicked.connect(lambda checked=False, v=voice: self._on_delete_voice(v))
                row_layout.addWidget(del_btn)

            self.radios_layout.addLayout(row_layout)

            if voice.id == self.selected_voice_id:
                radio.setChecked(True)

    def _on_delete_voice(self, voice: VoiceProfile):
        """Confirm and delete a custom voice profile."""
        reply = QMessageBox.question(
            self,
            "Delete Voice Profile",
            f"Are you sure you want to delete '{voice.name}'?\n\n"
            "This will remove the recorded voice and any generated stories for this voice.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes and voice.id is not None:
            logger.info(f"User requested deletion of voice profile: {voice.name} (ID: {voice.id})")
            success = VoiceService.delete_voice_profile(voice.id)
            if success:
                # Default back to Aiden (ID 1)
                self.selected_voice_id = 1
                self.refresh_voices(select_profile_id=1)
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete '{voice.name}'.")

    def set_story(self, story: Story):
        self.story = story
        self.title_label.setText(story.title)
        self.duration_badge.setText(f"⏱️ {story.estimated_duration}s")
        self.desc_label.setText(story.description)
        self.content_text.setText(story.content)
        self.refresh_voices(select_profile_id=self.selected_voice_id)

    def _on_play_clicked(self):
        checked_id = self.voice_group.checkedId()
        if checked_id == -1:
            checked_id = self.selected_voice_id or 1
        self.selected_voice_id = checked_id
        self.play_requested.emit(self.story, checked_id)
