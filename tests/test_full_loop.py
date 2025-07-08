# tests/test_full_loop.py (Versión con bucle mejorado)

# (Todas las importaciones y funciones anteriores se mantienen igual)
import whisper
import litellm
from piper.voice import PiperVoice
from piper.config import PiperConfig
import sounddevice as sd
import numpy as np
import os
import time
from scipy.io.wavfile import write as write_wav

# --- Configuración Centralizada ---
WHISPER_MODEL = "base"
TTS_MODEL_PATH = "../models/tts/es_ES-sharvard-medium.onnx"
TTS_CONFIG_PATH = "../models/tts/es_ES-sharvard-medium.onnx.json"
LLM_PROVIDER = "openai/lmstudio-local-model"
LLM_API_BASE = "http://localhost:1234/v1"

# --- Módulos Funcionales (sin cambios) ---

def load_models():
    print("Cargando modelos, por favor espera...")
    try:
        stt_model = whisper.load_model(WHISPER_MODEL)
        print("Modelo Whisper cargado.")
        print("Cargando modelo Piper TTS...")
        tts_model = PiperVoice.load(TTS_MODEL_PATH, config_path=TTS_CONFIG_PATH)
        print("¡Todos los modelos cargados exitosamente!")
        return stt_model, tts_model
    except Exception as e:
        print(f"Error crítico al cargar modelos: {e}")
        return None, None

def write_int16(filename, data, sample_rate):
    write_wav(filename, sample_rate, (data * 32767).astype(np.int16))

def listen(stt_model):
    print("\n----------------------------------")
    print("Escuchando durante 5 segundos...")
    recording = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    temp_file = "temp_recording.wav"
    write_int16(temp_file, recording, 16000)
    print("Transcribiendo...")
    result = stt_model.transcribe(temp_file, fp16=False) # fp16=False puede mejorar la estabilidad en CPU
    os.remove(temp_file)
    transcribed_text = result["text"].strip()
    print(f"Tú: {transcribed_text}")
    return transcribed_text

def think(text):
    print("Jarv1s está pensando...")
    messages = [
        {"role": "system", "content": "Eres Jarv1s, un copiloto de IA personal. Tus respuestas son siempre concisas y en español."},
        {"role": "user", "content": text}
    ]
    try:
        response = litellm.completion(model=LLM_PROVIDER, messages=messages, api_base=LLM_API_BASE, api_key="not-required", temperature=0.7)
        response_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error de conexión con el LLM: {e}")
        response_text = "Lo siento, estoy teniendo problemas para conectar con mi cerebro."
    print(f"Jarv1s: {response_text}")
    return response_text

def speak(tts_model, text):
    print("Sintetizando respuesta...")
    samplerate = tts_model.config.sample_rate
    audio_data = b''
    for audio_bytes in tts_model.synthesize_stream_raw(text):
        audio_data += audio_bytes
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    sd.play(audio_array, samplerate=samplerate)
    sd.wait()

# --- Bucle Principal (LA PARTE MODIFICADA) ---
def main():
    stt_model, tts_model = load_models()
    if not stt_model or not tts_model:
        return

    speak(tts_model, "Sistema Jarv1s iniciado. Estoy listo para conversar.")

    while True:
        user_input = listen(stt_model)
        
        # 1. Primero, verificamos si no escuchó nada.
        if not user_input:
            speak(tts_model, "No te he escuchado bien, ¿puedes repetirlo?")
            continue # Vuelve al inicio del bucle para escuchar de nuevo.

        # 2. Luego, verificamos si el usuario quiere salir.
        if "adiós" in user_input.lower():
            speak(tts_model, "Entendido. Desconectando. ¡Hasta la próxima!")
            break # Rompe el bucle y termina el programa.
            
        # 3. Si todo está bien, procesa la petición.
        response = think(user_input)
        speak(tts_model, response)
        time.sleep(1)

if __name__ == "__main__":
    main()