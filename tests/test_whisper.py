# tests/test_whisper.py (Versión con orden de operaciones corregido)

import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time
import torch

# --- Configuración ---
MODEL_TYPE = "base"  # Empezamos con 'base', puedes subir a 'small' si la calidad no es suficiente
SAMPLE_RATE = 16000
DURATION = 5
FILENAME = "temp_recording.wav"

def record_audio():
    """Graba audio y lo devuelve como un array numpy."""
    print("\n-----------------------------------------")
    print(f"Comienza a hablar. La grabación durará {DURATION} segundos.")
    for i in range(3, 0, -1):
        print(f"...{i}")
        time.sleep(1)
    print("¡HABLA AHORA!")
    
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    print("Grabación finalizada.")
    print("-----------------------------------------")
    return recording

def transcribe_audio(audio_data):
    """Carga Whisper en la GPU y transcribe el audio proporcionado."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo detectado: {device.upper()}")
    
    print(f"Cargando el modelo '{MODEL_TYPE}' de Whisper en {device.upper()}...")
    model = whisper.load_model(MODEL_TYPE, device=device)
    print("¡Modelo cargado!")

    # Guardamos los datos de audio en un archivo temporal para que Whisper lo procese
    write(FILENAME, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))

    print("\nProcesando el audio con Whisper...")
    result = model.transcribe(FILENAME, fp16=(device=="cuda"))
    
    # Liberamos memoria eliminando el modelo y el archivo
    del model
    torch.cuda.empty_cache()
    import os
    os.remove(FILENAME)

    return result["text"]

def main():
    """
    Función principal que primero graba y LUEGO transcribe.
    """
    # 1. Grabar primero, sin modelos de IA cargados
    try:
        my_recording = record_audio()
    except Exception as e:
        print(f"Error durante la grabación de audio: {e}")
        return

    # 2. Ahora, con el audio ya en memoria, cargamos el modelo y transcribimos
    try:
        transcribed_text = transcribe_audio(my_recording)
        print("\n--- TRANSCRIPCIÓN ---")
        print(f"Texto reconocido: {transcribed_text}")
        print("----------------------\n")
    except Exception as e:
        print(f"Error durante la transcripción: {e}")

if __name__ == "__main__":
    main()