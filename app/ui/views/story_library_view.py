"""
Story Library View
Displays all available children's stories in a clean, scrollable card grid.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import Signal, Qt
from app.services.story_service import StoryService
from app.ui.widgets.story_card import StoryCard
from app.database.models import Story

class StoryLibraryView(QWidget):
    story_chosen = Signal(object)  # Emits Story

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.load_stories()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)

        # Header Section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title = QLabel("✨ Story Library")
        title.setObjectName("appTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("Choose a story below to start storytime!")
        subtitle.setObjectName("appSubtitle")
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # Scroll Area for Story Cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.grid_layout = QGridLayout(self.cards_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(16)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)

    def load_stories(self):
        """Fetch stories from database and populate grid."""
        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        stories = StoryService.get_all_stories()
        cols = 2
        for index, story in enumerate(stories):
            row = index // cols
            col = index % cols
            card = StoryCard(story)
            card.story_selected.connect(self._on_story_selected)
            self.grid_layout.addWidget(card, row, col)

    def _on_story_selected(self, story: Story):
        self.story_chosen.emit(story)
