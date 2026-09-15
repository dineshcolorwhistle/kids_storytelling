"""
Verification script for Avatar Stage and Lip-Sync Engine
Tests audio analysis, frame lookup, and PySide6 Avatar widget rendering.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter
from app.audio.lip_sync_engine import LipSyncEngine, VisemeFrame
from app.ui.widgets.avatar_widget import AvatarStageWidget

def test_lip_sync_engine():
    audio_path = "data/generated_audio/default/story_1.wav"
    assert os.path.exists(audio_path), f"Audio file not found: {audio_path}"
    
    track = LipSyncEngine.analyze_audio(audio_path)
    assert track is not None, "Failed to analyze audio"
    assert len(track.frames) > 0, "No frames generated"
    assert track.duration_ms > 0, "Duration should be positive"
    print(f"[PASS] LipSyncEngine: successfully generated {len(track.frames)} frames ({track.duration_ms}ms)")

    # Test edge conditions
    f_start = track.get_frame(0)
    assert f_start is not None, "Frame at 0ms should exist"
    
    f_mid = track.get_frame(track.duration_ms // 2)
    assert 0.0 <= f_mid.openness <= 1.0, f"Openness out of range: {f_mid.openness}"
    assert 0.0 <= f_mid.width <= 1.0, f"Width out of range: {f_mid.width}"
    assert f_mid.viseme_type in ['REST', 'AA', 'OO', 'EE', 'MBP'], f"Invalid viseme: {f_mid.viseme_type}"
    print(f"[PASS] LipSyncEngine frame at mid-point: openness={f_mid.openness}, width={f_mid.width}, type={f_mid.viseme_type}")

    f_beyond = track.get_frame(track.duration_ms + 10000)
    assert f_beyond.viseme_type == 'REST', "Beyond duration should be REST"
    print("[PASS] LipSyncEngine edge cases passed")

def test_avatar_widget_rendering():
    # Initialize headless QApplication if not present
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    widget = AvatarStageWidget()
    widget.resize(260, 240)

    # Test rest state
    widget.reset_avatar()
    assert widget.openness == 0.0
    assert widget.viseme_type == "REST"

    # Test speaking state and frame setting
    widget.set_speaking_state(True)
    widget.set_viseme_frame(VisemeFrame(500, 0.75, 0.8, "AA"))
    assert widget.openness == 0.75
    assert widget.viseme_type == "AA"

    # Test rendering into a pixmap buffer (ensures no Qt drawing crash)
    pixmap = QPixmap(260, 240)
    pixmap.fill()
    widget.render(pixmap)
    assert not pixmap.isNull(), "Rendered pixmap should not be null"
    print("[PASS] AvatarStageWidget rendered cleanly to buffer without errors")

    # Test all visemes
    for viseme in ['REST', 'AA', 'OO', 'EE', 'MBP']:
        widget.set_viseme_frame(VisemeFrame(100, 0.6, 0.5, viseme))
        pix = QPixmap(260, 240)
        widget.render(pix)
    print("[PASS] All viseme types rendered cleanly")

if __name__ == "__main__":
    print("Starting Avatar & Lip-Sync tests...")
    test_lip_sync_engine()
    test_avatar_widget_rendering()
    print("ALL TESTS PASSED SUCCESSFULLY!")
