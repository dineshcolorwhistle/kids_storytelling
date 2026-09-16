"""
Verification test for personalized voice playback and UI fixes
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from app.database.connection import init_db
from app.database.seed_data import seed_stories
from app.database.models import Story, VoiceProfile
from app.ui.views.story_player_view import StoryPlayerView
from app.ui.views.story_details_view import StoryDetailsView
from app.ui.views.voice_enrollment_view import VoiceEnrollmentView
from app.ui.widgets.barnaby_bear_widget import BarnabyBearStageWidget
from app.services.voice_service import VoiceService

def run_tests():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    init_db()
    seed_stories()

    print("--- Test 1: StoryPlayerView Audio & Avatar Stage ---")
    player_view = StoryPlayerView()
    assert isinstance(player_view.avatar_stage, BarnabyBearStageWidget), "avatar_stage should be BarnabyBearStageWidget"

    # Test playing custom audio path
    test_story = Story(
        id=1,
        title="Test Story",
        description="A peaceful story",
        content="Once upon a time in a peaceful garden, a little rabbit hopped along...",
        thumbnail_path="data/stories/rabbit.png",
        estimated_duration=30
    )
    custom_audio_path = os.path.abspath("data/generated_audio/voice_005/story_1.wav")
    if not os.path.exists(custom_audio_path):
        custom_audio_path = os.path.abspath("data/generated_audio/default/story_1.wav")

    player_view.play_story(test_story, custom_audio_path, voice_name="My voice")

    # Verify that the player loaded the WAV file, NOT barnaby_3d_storyteller.mp4
    loaded_file = player_view.player.current_file
    assert loaded_file is not None, "Loaded file should not be None"
    print(f"Loaded media file: {loaded_file}")
    assert loaded_file.endswith(".wav"), f"Expected .wav file to be loaded, got {loaded_file}"
    assert "barnaby_3d_storyteller.mp4" not in loaded_file, "barnaby_3d_storyteller.mp4 should not be played!"

    # Verify LipSyncTrack was analyzed and attached
    assert player_view.lip_sync_track is not None, "LipSyncTrack should be computed"
    assert player_view.avatar_stage.lip_sync_track is not None, "BarnabyBearStageWidget should have LipSyncTrack"
    print("[PASS] Test 1: StoryPlayerView loads synthesized .wav and initializes Barnaby 3D lip-sync correctly!")

    player_view.player.stop()

    print("--- Test 2: StoryDetailsView Voice Selection Persistence ---")
    details_view = StoryDetailsView()
    voices = VoiceService.get_all_voices()
    print(f"Available voices: {[v.name for v in voices]}")

    if len(voices) > 1:
        custom_voice = voices[1]
        assert custom_voice.id is not None
        print(f"Selecting custom voice: {custom_voice.name} (ID: {custom_voice.id})")
        details_view.selected_voice_id = custom_voice.id
        details_view.refresh_voices(select_profile_id=custom_voice.id)
        assert details_view.voice_group.checkedId() == custom_voice.id

        # Switch story and ensure the selected voice remains custom_voice.id
        details_view.set_story(test_story)
        assert details_view.voice_group.checkedId() == custom_voice.id, \
            f"Expected checked ID {custom_voice.id}, got {details_view.voice_group.checkedId()}"
        print(f"[PASS] Test 2: StoryDetailsView retained voice selection ({custom_voice.name}) across story change!")
    else:
        print("[INFO] Only 1 voice in DB, skipping multi-voice test 2.")

    print("--- Test 3: VoiceEnrollmentView Unload & File Release ---")
    enroll_view = VoiceEnrollmentView()
    enroll_view.player.load_file(custom_audio_path)
    assert enroll_view.player.current_file is not None
    enroll_view.player.unload()
    assert enroll_view.player.current_file is None
    print("[PASS] Test 3: VoiceEnrollmentView successfully unloads audio file to release Windows handle!")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
