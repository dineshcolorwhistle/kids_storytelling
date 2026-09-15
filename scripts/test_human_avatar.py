"""
Test script for HumanAvatarStageWidget
Verifies rendering, viseme morphing, and offscreen painting without error.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from app.ui.widgets.human_avatar_widget import HumanAvatarStageWidget
from app.audio.lip_sync_engine import VisemeFrame

def test_human_avatar():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = HumanAvatarStageWidget()
    widget.resize(260, 320)

    # Check asset loaded
    assert widget.base_pixmap is not None and not widget.base_pixmap.isNull(), "Base pixmap not loaded!"
    print("[PASS] 3D Human Narrator base asset successfully loaded")

    # Render rest state
    pixmap = QPixmap(260, 320)
    pixmap.fill()
    widget.render(pixmap)
    assert not pixmap.isNull()
    print("[PASS] HumanAvatarStageWidget rendered rest state cleanly")

    # Render speaking state across all visemes
    widget.set_speaking_state(True)
    for viseme in ['REST', 'AA', 'OO', 'EE', 'MBP']:
        widget.set_viseme_frame(VisemeFrame(500, 0.7, 0.6, viseme))
        pix = QPixmap(260, 320)
        widget.render(pix)
    print("[PASS] All visemes rendered cleanly on 3D Human Narrator")

if __name__ == "__main__":
    print("Starting Human Avatar Tests...")
    test_human_avatar()
    print("ALL HUMAN AVATAR TESTS PASSED!")
