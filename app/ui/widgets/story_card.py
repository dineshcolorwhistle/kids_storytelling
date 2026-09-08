"""
Interactive Story Card Widget
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from app.database.models import Story

class StoryCard(QFrame):
    """Card widget representing a single story in the library."""
    story_selected = Signal(object)  # Emits Story instance

    def __init__(self, story: Story, parent=None):
        super().__init__(parent)
        self.story = story
        self.setObjectName("storyCard")
        self.setCursor(Qt.PointingHandCursor)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Row: Title and Duration Badge
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Title
        title_label = QLabel(self.story.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, stretch=1)

        # Duration Badge
        duration_badge = QLabel(f"⏱️ {self.story.estimated_duration}s")
        duration_badge.setObjectName("durationBadge")
        header_layout.addWidget(duration_badge)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.story.description)
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Footer Row: Listen Action
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        listen_btn = QPushButton("▶ Listen")
        listen_btn.setObjectName("cardListenButton")
        listen_btn.clicked.connect(lambda: self.story_selected.emit(self.story))
        footer_layout.addWidget(listen_btn)

        layout.addLayout(footer_layout)

    def mousePressEvent(self, event):
        """Allow clicking anywhere on the card to select the story."""
        if event.button() == Qt.LeftButton:
            self.story_selected.emit(self.story)
        super().mousePressEvent(event)
