"""
Generate a clean 20-second adult reference voice sample for Phase 1 testing.
Matches the enrollment prompt from AI_Kids_Storytelling_MVP_Project_Instructions.md.
"""
import os
import pyttsx3
import soundfile as sf

OUTPUT_PATH = os.path.join("data", "voices", "reference_sample.wav")
REF_TEXT_PATH = os.path.join("data", "voices", "reference_text.txt")

PROMPT_TEXT = (
    "Hello! I am going to tell you a wonderful story. "
    "Once upon a time, there was a little rabbit. "
    "The rabbit loved exploring the beautiful forest, sniffing fresh flowers and watching butterflies dance in the warm sunshine."
)

def generate_reference():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    # Save reference transcript
    with open(REF_TEXT_PATH, "w", encoding="utf-8") as f:
        f.write(PROMPT_TEXT)
    
    print(f"Generating reference voice sample using Windows TTS engine...")
    engine = pyttsx3.init()
    
    # Set speech rate to a calm, clear storytelling pace (~140 wpm)
    engine.setProperty('rate', 140)
    
    # Save directly to wav
    engine.save_to_file(PROMPT_TEXT, OUTPUT_PATH)
    engine.runAndWait()
    
    # Verify file and duration
    info = sf.info(OUTPUT_PATH)
    print(f"[SUCCESS] Reference voice created at: {OUTPUT_PATH}")
    print(f"Duration: {info.duration:.2f} seconds | Sample Rate: {info.samplerate} Hz | Channels: {info.channels}")

if __name__ == "__main__":
    generate_reference()
