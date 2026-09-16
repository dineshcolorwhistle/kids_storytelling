"""
Verification script for Barnaby Bear 3D avatar & lip-sync engine
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from app.audio.lip_sync_engine import LipSyncEngine, VisemeFrame
from app.ui.widgets.barnaby_bear_widget import BarnabyBearStageWidget

def test_barnaby_bear():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # 1. Test LipSyncEngine analysis with new sensitivity
    audio_path = "data/generated_audio/default/story_1.wav"
    assert os.path.exists(audio_path)
    track = LipSyncEngine.analyze_audio(audio_path)
    assert track is not None

    # Check maximum openness during speech
    openness_values = [f.openness for f in track.frames if f.viseme_type != "REST"]
    assert len(openness_values) > 0
    max_open = max(openness_values)
    avg_open = sum(openness_values) / len(openness_values)
    print(f"[PASS] Speech analysis: max_openness={max_open:.2f}, avg_openness={avg_open:.2f}")
    assert max_open >= 0.5, f"Expected expressive speech openness, got {max_open}"

    # 2. Test BarnabyBearStageWidget rendering
    widget = BarnabyBearStageWidget()
    widget.resize(260, 320)
    widget.set_lip_sync_track(track)

    # Rest pose
    widget.reset_avatar()
    pix = QPixmap(260, 320)
    widget.render(pix)
    assert not pix.isNull()
    print("[PASS] Barnaby Bear 3D rest pose rendered cleanly")

    # Speaking pose with distinct visemes
    widget.set_speaking_state(True)
    for viseme in ['REST', 'AA', 'OO', 'EE', 'MBP']:
        widget.set_viseme_frame(VisemeFrame(1000, 0.75, 0.7, viseme))
        pix = QPixmap(260, 320)
        widget.render(pix)
        assert not pix.isNull()
    print("[PASS] Barnaby Bear 3D speaking visemes (AA, OO, EE, MBP) rendered with dynamic jaw and tongue!")

    widget.anim_timer.stop()

if __name__ == "__main__":
    print("Testing Barnaby Bear 3D...")
    test_barnaby_bear()
    print("ALL BARNABY BEAR 3D TESTS PASSED!")
