# Installation and Component Verification Guide

This guide will take you step by step through setting up the development environment for Jarv1s and verifying each of its key components in isolation. Following these steps will ensure that all dependencies and models work correctly before running the main application.

## 1. Environment Setup

### System Prerequisites

Before installing Python dependencies, Jarv1s needs some system-level tools.

- **FFmpeg:** Required for `whisper` to process audio.
  - **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
  - **macOS (with Homebrew):** `brew install ffmpeg`
  - **Windows (with Chocolatey):** `choco install ffmpeg`

- **Espeak NG (Optional, but recommended):** Used by some TTS engines. Good to have.
  - **Linux (Debian/Ubuntu):** `sudo apt install espeak-ng`
  - **macOS (with Homebrew):** `brew install espeak`
  - **Windows:** Generally not needed, `pyttsx3` uses native voices.

### Virtual Environment and Dependencies

1.  **Create and activate a virtual environment** at the project root to keep dependencies isolated:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install all necessary Python libraries** with the following command:
    ```bash
    pip install openai-whisper torch sounddevice scipy litellm piper-tts numpy
    ```

### AI Model Download

Jarv1s depends on pre-trained models to function.

1.  **Create a folder for the models:**
    ```bash
    mkdir -p models/tts
    ```

2.  **Download the Piper TTS voice model:**
    Navigate to the `models/tts` folder and download the two necessary files for the Spanish voice.
    ```bash
    cd models/tts
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json
    cd ../.. # Return to project root
    ```
    The Whisper model will be downloaded automatically the first time it's used.

## 2. Component Verification

To ensure everything works, we have created test scripts for each module in the `tests/` folder. Run them in order.

### Test 1: Ears - Speech-to-Text (Whisper)

This script validates that your microphone can record audio and that Whisper can transcribe it.

**File:** `tests/test_whisper.py`
```python
import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import time

MODEL_TYPE = "base"
SAMPLE_RATE = 16000
DURATION = 5
FILENAME = "temp_recording.wav"

def main():
    print(f"Loading Whisper '{MODEL_TYPE}' model...")
    model = whisper.load_model(MODEL_TYPE)
    print("Model loaded!")

    print(f"\nGet ready to speak. Recording for {DURATION} seconds...")
    time.sleep(2)
    print("SPEAK NOW!")
    
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    print("Recording finished.")

    write(FILENAME, SAMPLE_RATE, (recording * 32767).astype(np.int16))

    result = model.transcribe(FILENAME)
    os.remove(FILENAME)
    
    print("\n--- TRANSCRIPTION ---")
    print(f"Recognized text: {result['text'].strip()}")
    print("---------------------\n")

if __name__ == "__main__":
    main()
```
**Execution:**
```bash
python tests/test_whisper.py
```
**Expected result:** The text you said during recording will appear in the console.

---

### Test 2: Voice - Text-to-Speech (Piper TTS)

This script validates that we can generate high-quality voice from text.

**File:** `tests/test_tts.py`
```python
import os
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

def main():
    model_path = "models/tts/es_ES-sharvard-medium.onnx"
    config_path = "models/tts/es_ES-sharvard-medium.onnx.json"

    print("Loading Piper voice model using 'load' method...")
    voice = PiperVoice.load(model_path, config_path=config_path)
    print("Model loaded successfully!")

    samplerate = voice.config.sample_rate
    text = "If you can hear this, Jarv1s high-quality voice is operational."

    print(f"\nSynthesizing text and playing...")
    audio_data = b''
    for audio_bytes in voice.synthesize_stream_raw(text):
        audio_data += audio_bytes
    
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    sd.play(audio_array, samplerate=samplerate)
    sd.wait()
    print("Playback finished!")

if __name__ == "__main__":
    main()
```
**Execution (from project root):**
```bash
python tests/test_tts.py
```
**Expected result:** You will hear the synthesized phrase through your speakers.

---

### Test 3: Brain - LLM Connection (LM Studio)

This script validates the connection with your local language model.

**Prerequisite:** Open LM Studio, load a model and **activate the local server** (usually at `http://localhost:1234/v1`).

**File:** `tests/test_llm.py`
```python
import litellm

def main():
    model_name = "openai/lmstudio-local-model"
    api_base = "http://localhost:1234/v1"

    messages = [
        {"role": "system", "content": "You are Jarv1s, a personal AI copilot. Respond concisely."},
        {"role": "user", "content": "Confirm that you are operational."}
    ]

    print("Connecting to LLM server in LM Studio...")
    response = litellm.completion(
        model=model_name,
        messages=messages,
        api_base=api_base,
        api_key="not-required"
    )

    print("\n--- LLM RESPONSE ---")
    print(response.choices[0].message.content.strip())
    print("-------------------\n")

if __name__ == "__main__":
    main()
```
**Execution:**
```bash
python tests/test_llm.py
```
**Expected result:** You will see a coherent response from the model printed in your terminal.