# Guía de Instalación y Verificación de Componentes

Esta guía te llevará paso a paso a través de la configuración del entorno de desarrollo para Jarv1s y la verificación de cada uno de sus componentes clave de forma aislada. Seguir estos pasos asegurará que todas las dependencias y modelos funcionan correctamente antes de ejecutar la aplicación principal.

## 1. Configuración del Entorno

### Prerrequisitos del Sistema

Antes de instalar las dependencias de Python, Jarv1s necesita algunas herramientas a nivel de sistema.

- **FFmpeg:** Necesario para que `whisper` procese audio.
  - **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
  - **macOS (con Homebrew):** `brew install ffmpeg`
  - **Windows (con Chocolatey):** `choco install ffmpeg`

- **Espeak NG (Opcional, pero recomendado):** Usado por algunos motores de TTS. Es bueno tenerlo.
  - **Linux (Debian/Ubuntu):** `sudo apt install espeak-ng`
  - **macOS (con Homebrew):** `brew install espeak`
  - **Windows:** Generalmente no es necesario, `pyttsx3` usa las voces nativas.

### Entorno Virtual y Dependencias

1.  **Crea y activa un entorno virtual** en la raíz del proyecto para mantener las dependencias aisladas:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Instala todas las librerías de Python** necesarias con el siguiente comando:
    ```bash
    pip install openai-whisper torch sounddevice scipy litellm piper-tts numpy
    ```

### Descarga de Modelos de IA

Jarv1s depende de modelos pre-entrenados para funcionar.

1.  **Crea una carpeta para los modelos:**
    ```bash
    mkdir -p models/tts
    ```

2.  **Descarga el modelo de voz de Piper TTS:**
    Navega a la carpeta `models/tts` y descarga los dos archivos necesarios para la voz en español.
    ```bash
    cd models/tts
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json
    cd ../.. # Vuelve a la raíz del proyecto
    ```
    El modelo de Whisper se descargará automáticamente la primera vez que se use.

## 2. Verificación de Componentes

Para asegurarnos de que todo funciona, hemos creado scripts de prueba para cada módulo en la carpeta `tests/`. Ejecútalos en orden.

### Prueba 1: Oídos - Speech-to-Text (Whisper)

Este script valida que tu micrófono puede grabar audio y que Whisper puede transcribirlo.

**Archivo:** `tests/test_whisper.py`
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
    print(f"Cargando el modelo '{MODEL_TYPE}' de Whisper...")
    model = whisper.load_model(MODEL_TYPE)
    print("¡Modelo cargado!")

    print(f"\nPrepárate para hablar. Grabando durante {DURATION} segundos...")
    time.sleep(2)
    print("¡HABLA AHORA!")
    
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    print("Grabación finalizada.")

    write(FILENAME, SAMPLE_RATE, (recording * 32767).astype(np.int16))

    result = model.transcribe(FILENAME)
    os.remove(FILENAME)
    
    print("\n--- TRANSCRIPCIÓN ---")
    print(f"Texto reconocido: {result['text'].strip()}")
    print("----------------------\n")

if __name__ == "__main__":
    main()
```
**Ejecución:**
```bash
python tests/test_whisper.py
```
**Resultado esperado:** El texto que dijiste durante la grabación aparecerá en la consola.

---

### Prueba 2: Boca - Text-to-Speech (Piper TTS)

Este script valida que podemos generar una voz de alta calidad a partir de texto.

**Archivo:** `tests/test_tts.py`
```python
import os
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

def main():
    model_path = "models/tts/es_ES-sharvard-medium.onnx"
    config_path = "models/tts/es_ES-sharvard-medium.onnx.json"

    print("Cargando el modelo de voz de Piper usando el método 'load'...")
    voice = PiperVoice.load(model_path, config_path=config_path)
    print("¡Modelo cargado exitosamente!")

    samplerate = voice.config.sample_rate
    text = "Si puedes escuchar esto, la voz de alta calidad de Jarv1s está operativa."

    print(f"\nSintetizando texto y reproduciendo...")
    audio_data = b''
    for audio_bytes in voice.synthesize_stream_raw(text):
        audio_data += audio_bytes
    
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    sd.play(audio_array, samplerate=samplerate)
    sd.wait()
    print("¡Reproducción finalizada!")

if __name__ == "__main__":
    main()
```
**Ejecución (desde la raíz del proyecto):**
```bash
python tests/test_tts.py
```
**Resultado esperado:** Escucharás la frase sintetizada a través de tus altavoces.

---

### Prueba 3: Cerebro - Conexión con el LLM (LM Studio)

Este script valida la conexión con tu modelo de lenguaje local.

**Requisito previo:** Abre LM Studio, carga un modelo y **activa el servidor local** (normalmente en `http://localhost:1234/v1`).

**Archivo:** `tests/test_llm.py`
```python
import litellm

def main():
    model_name = "openai/lmstudio-local-model"
    api_base = "http://localhost:1234/v1"

    messages = [
        {"role": "system", "content": "Eres Jarv1s, un copiloto de IA personal. Responde de forma concisa."},
        {"role": "user", "content": "Confirma que estás operativo."}
    ]

    print("Conectando con el servidor LLM en LM Studio...")
    response = litellm.completion(
        model=model_name,
        messages=messages,
        api_base=api_base,
        api_key="not-required"
    )

    print("\n--- RESPUESTA DEL LLM ---")
    print(response.choices.message.content.strip())
    print("--------------------------\n")

if __name__ == "__main__":
    main()
```
**Ejecución:**
```bash
python tests/test_llm.py
```
**Resultado esperado:** Verás una respuesta coherente del modelo impresa en tu terminal.