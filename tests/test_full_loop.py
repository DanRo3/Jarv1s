# tests/test_full_loop.py (Optimizado para CPU)

# --- Importaciones ---
import whisper
import litellm
from piper.voice import PiperVoice
import sounddevice as sd
import numpy as np
import os
import time
from scipy.io.wavfile import write as write_wav

# --- Configuración Centralizada ---
# Usamos 'small' para un gran salto en precisión. ¡La diferencia es notable!
WHISPER_MODEL = "small" 
TTS_MODEL_PATH = "models/tts/es_ES-sharvard-medium.onnx"
TTS_CONFIG_PATH = "models/tts/es_ES-sharvard-medium.onnx.json"
LLM_PROVIDER = "openai/lmstudio-local-model"
LLM_API_BASE = "http://localhost:1234/v1"
RECORD_DURATION = 5

# --- Módulos Funcionales ---

def load_tts_model():
    print("Cargando modelo de voz (Piper TTS)...")
    try:
        tts_model = PiperVoice.load(TTS_MODEL_PATH, config_path=TTS_CONFIG_PATH)
        print("¡Modelo TTS cargado!")
        return tts_model
    except Exception as e:
        print(f"Error crítico al cargar el modelo TTS: {e}")
        return None

def record_audio():
    print("\n----------------------------------")
    print(f"Escuchando durante {RECORD_DURATION} segundos...")
    recording = sd.rec(int(RECORD_DURATION * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    print("Grabación finalizada.")
    return recording

def transcribe(audio_data):
    """
    Carga Whisper en la CPU, transcribe el audio y libera la memoria.
    """
    temp_file = "temp_recording.wav"
    try:
        write_wav(temp_file, 16000, (audio_data * 32767).astype(np.int16))
        
        print(f"Cargando modelo Whisper ('{WHISPER_MODEL}') en CPU...")
        model = whisper.load_model(WHISPER_MODEL, device="cpu")
        
        print("Transcribiendo...")
        # Eliminamos la lógica de FP16, ya que no es relevante para CPU.
        result = model.transcribe(temp_file)
        transcribed_text = result["text"].strip()
        print(f"Tú: {transcribed_text}")
        
    except Exception as e:
        print(f"Error durante la transcripción: {e}")
        transcribed_text = ""
    finally:
        if 'model' in locals():
            del model
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    return transcribed_text

# El resto de funciones (think, speak, main) se mantienen exactamente igual
# a la última versión con memoria.
def think(user_input, history):
    print("Jarv1s está pensando...")
    history.append({"role": "user", "content": user_input})
    try:
        response = litellm.completion(model=LLM_PROVIDER, messages=history, api_base=LLM_API_BASE, api_key="not-required", temperature=0.7)
        response_text = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": response_text})
    except Exception as e:
        print(f"Error de conexión con el LLM: {e}")
        response_text = "Lo siento, estoy teniendo problemas para conectar con mi cerebro."
    print(f"Jarv1s: {response_text}")
    return response_text, history

def speak(tts_model, text):
    print("Sintetizando respuesta...")
    samplerate = tts_model.config.sample_rate
    audio_data = b''
    for audio_bytes in tts_model.synthesize_stream_raw(text):
        audio_data += audio_bytes
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    sd.play(audio_array, samplerate=samplerate)
    sd.wait()

def main():
    tts_model = load_tts_model()
    if not tts_model:
        return

    conversation_history = [
        {"role": "system", "content": "Eres Jarv1s, un copiloto de IA personal. Tus respuestas son siempre concisas, amables y en español. Recuerdas la conversación anterior para dar respuestas coherentes."}
    ]

    speak(tts_model, "Sistema Jarv1s iniciado. Estoy listo para conversar.")

    while True:
        audio_clip = record_audio()
        user_input = transcribe(audio_clip)
        
        if not user_input:
            speak(tts_model, "No te he escuchado bien, ¿puedes repetirlo?")
            continue

        if "adiós" in user_input.lower():
            speak(tts_model, "Entendido. Desconectando. ¡Hasta la próxima!")
            break
            
        response, conversation_history = think(user_input, conversation_history)
        
        if len(conversation_history) > 10:
            conversation_history = [conversation_history[0]] + conversation_history[-9:]

        speak(tts_model, response)
        time.sleep(1)

if __name__ == "__main__":
    main()