import whisperx
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time
import os

# --- Configuración ---
# Con WhisperX y faster-whisper, podemos permitirnos usar un modelo grande incluso en CPU.
MODEL_TYPE = "large-v2" 
SAMPLE_RATE = 16000
DURATION = 5
FILENAME = "temp_recording.wav"

def record_audio():
    """Graba audio y lo guarda en un archivo temporal."""
    print("\n-----------------------------------------")
    print(f"Comienza a hablar. La grabación durará {DURATION} segundos.")
    time.sleep(1)
    print("¡HABLA AHORA!")
    
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    print("Grabación finalizada.")
    
    write(FILENAME, SAMPLE_RATE, (recording * 32767).astype(np.int16))
    print("-----------------------------------------")
    return FILENAME

def transcribe_with_whisperx(audio_path: str):
    """Carga WhisperX y transcribe el audio especificado usando optimizaciones de CPU."""
    
    # Parámetros optimizados para CPU
    device = "cpu"
    compute_type = "int8"
    
    print(f"Cargando el modelo WhisperX '{MODEL_TYPE}' en {device.upper()} con cómputo '{compute_type}'...")
    # La carga del modelo es el paso más lento
    model = whisperx.load_model(MODEL_TYPE, device, compute_type=compute_type, language="es")
    print("¡Modelo cargado!")

    # Cargamos el audio desde el archivo
    audio = whisperx.load_audio(audio_path)

    print("\nProcesando el audio con WhisperX...")
    # Para la prueba inicial, solo haremos la transcripción básica.
    # No haremos la alineación ni la diarización para mantenerlo simple.
    result = model.transcribe(audio, batch_size=4)
    
    transcribed_text = " ".join([segment['text'].strip() for segment in result["segments"]])

    # Liberamos memoria
    del model
    os.remove(audio_path)

    return transcribed_text

def main():
    """
    Función principal que graba y luego transcribe con WhisperX.
    """
    audio_file = record_audio()
    
    try:
        transcribed_text = transcribe_with_whisperx(audio_file)
        print("\n--- TRANSCRIPCIÓN (WhisperX) ---")
        print(f"Texto reconocido: {transcribed_text}")
        print("----------------------------------\n")
    except Exception as e:
        print(f"Error durante la transcripción con WhisperX: {e}")

if __name__ == "__main__":
    main()