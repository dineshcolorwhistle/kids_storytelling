"""
Kid-Friendly Visual Theme and Stylesheet (QSS)
"""

MAIN_STYLESHEET = """
QMainWindow {
    background-color: #F8F9FE;
}

QWidget {
    font-family: 'Segoe UI', 'Comic Sans MS', sans-serif;
    color: #2D3748;
}

/* Header & Titles */
QLabel#appTitle {
    font-size: 28px;
    font-weight: 800;
    color: #4C51BF;
    padding: 10px;
}

QLabel#appSubtitle {
    font-size: 16px;
    font-weight: 500;
    color: #718096;
    margin-bottom: 10px;
}

/* Cards */
QFrame#storyCard {
    background-color: #FFFFFF;
    border-radius: 18px;
    border: 2px solid #E2E8F0;
    padding: 16px;
}

QFrame#storyCard:hover {
    border: 2px solid #667EEA;
    background-color: #FFFFFF;
}

QLabel#cardTitle {
    font-size: 20px;
    font-weight: 700;
    color: #2D3748;
}

QLabel#cardDescription {
    font-size: 14px;
    color: #4A5568;
    line-height: 1.4;
}

QLabel#durationBadge {
    background-color: #EDF2F7;
    color: #4A5568;
    font-size: 13px;
    font-weight: 600;
    border-radius: 10px;
    padding: 4px 10px;
}

/* Primary Action Buttons */
QPushButton#primaryButton {
    background-color: #5A67D8;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 700;
    border-radius: 14px;
    padding: 10px 22px;
    border: none;
}

QPushButton#primaryButton:hover {
    background-color: #4C51BF;
}

QPushButton#primaryButton:pressed {
    background-color: #434190;
}

QPushButton#cardListenButton {
    background-color: #48BB78;
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 700;
    border-radius: 12px;
    padding: 8px 18px;
    border: none;
}

QPushButton#cardListenButton:hover {
    background-color: #38A169;
}

QPushButton#cardListenButton:pressed {
    background-color: #2F855A;
}

/* Scroll Area */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    border: none;
    background: #EDF2F7;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #CBD5E0;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #A0AEC0;
}
"""
