# MyStory — Kids AI Storytelling Desktop App 🪄📖

An engaging, kid-friendly Windows desktop application designed to deliver personalized audio storytelling for children. The application pairs curated short stories with AI voice cloning technology, enabling parents, grandparents, and caregivers to record a short voice sample once and have the application narrate stories in their familiar voice.

---

## ✨ Features

- **📚 Curated Story Library**: 6 wholesome, age-appropriate children's stories with illustrations, descriptions, and estimated read times.
- **🎙️ Zero-Shot AI Voice Cloning**: Record a 20–30 second adult voice sample once; the AI synthesizes stories matching the tone, pitch, and timbre of the speaker using **Qwen3-TTS (0.6B Base)**.
- **⭐ Built-in Default Narrator**: Pre-generated audio (`Aiden`) available instantly right out of the box with zero wait time.
- **⚡ Smart Audio Caching**: Stories generated with personal voices are stored locally (`data/generated_audio/`) and registered in SQLite. Once synthesized, stories replay **instantly** on subsequent visits without re-synthesizing.
- **🗑️ Voice Profile Management**: Easily manage multiple family voice profiles (Mom, Dad, Grandparents) and delete custom profiles and their associated audio caches directly from the interface.
- **🎧 Kid-Friendly Audio Player**: Large play/pause controls, interactive progress scrubbers, volume adjustment, and friendly visual elements designed for young children.
- **🔒 Privacy & Child Safety by Design**: 
  - 100% local-first data processing.
  - No accounts, logins, or personal identification collected.
  - Zero cloud telemetry or third-party audio transmission in local mode.

---

## 🏗️ Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────┐
│                   PySide6 Desktop UI                   │
│         (Story Library, Details, Voice Enrollment,     │
│          Generation Progress, and Audio Player)        │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                      Service Layer                     │
│    (AudioService, VoiceService, GenerationWorker)      │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
┌──────────────▼──────────────┐ ┌─────────▼──────────────┐
│       Database & Audio      │ │   TTS Provider Layer   │
│ ┌─────────────────────────┐ │ │ ┌────────────────────┐ │
│ │   SQLite (Metadata)     │ │ │ │    TTSProvider     │ │
│ ├─────────────────────────┤ │ │ ├────────────────────┤ │
│ │ Local Storage (WAV)     │ │ │ │ QwenTTSProvider    │ │
│ └─────────────────────────┘ │ │ │ (Local CPU/Remote) │ │
│                             │ │ └────────────────────┘ │
└─────────────────────────────┘ └────────────────────────┘
```

- **Frontend / GUI**: [PySide6 (Qt 6)](https://wiki.qt.io/Qt_for_Python) with custom QSS visual theme.
- **Database**: SQLite 3 with Foreign Key cascades and indexed audio cache lookups.
- **AI Voice Engine**: [Qwen/Qwen3-TTS](https://huggingface.co/Qwen) (0.6B Base model for voice cloning, 0.6B CustomVoice for default voice).
- **Audio Recording & Processing**: `sounddevice`, `soundfile`, `PySide6.QtMultimedia`.
- **Concurrency**: Asynchronous `QThread` (`GenerationWorker`) to ensure the desktop UI remains responsive during AI synthesis.

---

## 📁 Project Directory Structure

```
kids_storytelling/
├── app/
│   ├── config/              # Application settings and paths
│   │   └── settings.py
│   ├── database/            # SQLite schema, connection, and repositories
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── seed_data.py
│   │   └── repositories/
│   ├── audio/               # Recording and playback engine
│   │   ├── recorder.py
│   │   └── player.py
│   ├── services/            # Business logic
│   │   ├── audio_service.py
│   │   ├── voice_service.py
│   │   └── generation_worker.py
│   ├── tts/                 # Text-To-Speech providers
│   │   ├── base.py
│   │   └── qwen_provider.py
│   ├── ui/                  # PySide6 UI views and widgets
│   │   ├── main_window.py
│   │   ├── styles.py
│   │   ├── views/           # Library, Details, Enrollment, Player, Generation
│   │   └── widgets/         # StoryCard
│   └── utils/
│       └── logger.py
├── data/                    # Local storage (excluded from git tracking)
│   ├── database/            # SQLite database (app.db)
│   ├── stories/             # Story thumbnails & assets
│   ├── voices/              # Recorded voice samples (reference.wav)
│   ├── generated_audio/     # Cached story WAV audio files
│   └── logs/                # Application runtime logs
├── requirements-poc.txt     # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Operating System**: Windows 10 / 11 (64-bit)
- **Python**: Version 3.10, 3.11, or 3.12
- **Hardware**: Minimum 8 GB RAM (16 GB recommended for CPU inference)
- **Microphone**: Working audio input for voice enrollment

### 2. Environment Setup
Clone or navigate to the project directory and create a virtual environment:

```powershell
# Navigate to project directory
cd d:\Projects\kids_storytelling

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install the required dependencies:

```powershell
pip install -r requirements-poc.txt
```

*(Note: PySide6, torch, sounddevice, soundfile, and qwen-tts / transformers are included.)*

### 4. Run the Application
Launch the desktop application:

```powershell
python app/main.py
```

The database and default stories will automatically initialize and seed on the first run.

---

## 📖 User Guide & Key Workflows

### 1. Playing Default Stories
- Browse stories in the **Story Library**.
- Click **"Listen Now"** on any story card.
- By default, **⭐ Default Narrator (Aiden)** is selected.
- Click **"▶ Generate & Listen"** to start the story player instantly.

### 2. Creating a Personalized Voice
1. On any story details screen, click **"🎙️ + Record New Voice"**.
2. Read the displayed passage aloud (aim for 20–30 seconds for optimal voice similarity).
3. Click **"Start Recording"**, speak clearly into the microphone, then click **"Stop Recording"**.
4. Play back the recorded sample to verify quality.
5. Enter a name (e.g., `"Mom's Voice"` or `"Dad's Voice"`) and click **"Save Voice Profile"**.

### 3. Generating Stories with Your Voice
- Select your custom voice profile from the **"Choose Narrator Voice"** list.
- Click **"▶ Generate & Listen"**.
- **First-Time Model Loading**: If generating with a cloned voice for the very first time, the application will download the base voice cloning model (`Qwen3-TTS-12Hz-0.6B-Base`, ~1.5 GB) and load it into memory.
- Once synthesis finishes, the story opens automatically in the audio player.
- **Cached Playback**: Subsequent plays of that story in that voice will play **instantly** without waiting!

### 4. Deleting Voice Profiles
- On the Story Details screen under **Choose Narrator Voice**, each custom voice profile displays a **`🗑️ Delete`** button.
- Clicking **Delete** prompts for confirmation, then safely cleans up the voice profile, reference audio, and all cached stories associated with that voice.

---

## ⚙️ Configuration & Remote GPU Mode

Settings can be customized in [`app/config/settings.py`](file:///d:/Projects/kids_storytelling/app/config/settings.py):

| Setting | Default Value | Description |
| :--- | :--- | :--- |
| `DEFAULT_TTS_MODEL` | `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` | Narrator voice model |
| `BASE_CLONE_TTS_MODEL`| `Qwen/Qwen3-TTS-12Hz-0.6B-Base` | Voice cloning base model |
| `AUDIO_SAMPLE_RATE` | `24000` | Audio sampling rate in Hz |
| `TTS_MODE` | `"local"` | Set to `"remote"` to offload synthesis to a GPU server |
| `REMOTE_TTS_URL` | `"http://localhost:8000"` | Remote FastAPI / TTS backend endpoint |

---

## 🛡️ Child Safety & Content Guidelines

- **Zero Third-Party Tracking**: Audio recordings and database metadata stay entirely on the user's computer.
- **Curated Content**: All included stories promote gentle, positive themes (friendship, bravery, bedtime calm) suitable for early childhood development.
- **Adult Voice Cloning Only**: Designed for parents and guardians to read to children. Child voice cloning is not supported.