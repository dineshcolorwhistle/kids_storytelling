"""
Application Entry Point
"""
import sys
import os

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.config.settings import APP_NAME
from app.utils.logger import logger
from app.database.connection import init_db
from app.database.seed_data import seed_stories
from app.ui.main_window import MainWindow

def main():
    logger.info("=" * 50)
    logger.info(f"Starting {APP_NAME}...")
    logger.info("=" * 50)

    # 1. Initialize SQLite Database & Seed Stories
    try:
        init_db()
        seed_stories()
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)

    # 2. Launch Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    window = MainWindow()
    window.show()

    logger.info("Application event loop started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
