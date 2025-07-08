import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import time

# --- Configuración ---
MODEL_TYPE = "tiny"  # Modelo de Whisper a usar (opciones: tiny, base, small, medium, large)
SAMPLE_RATE = 16000  # Tasa de muestreo (16kHz es estándar para Whisper)
DURATION = 5         # Duración de la grabación en segundos
FILENAME = "temp_recording.wav" # Nombre del archivo temporal para guardar la grabación

def main():
    """
    Función principal para grabar audio y transcribirlo con Whisper.
    """
    print(f"Cargando el modelo '{MODEL_TYPE}' de Whisper. Esto puede tardar un momento la primera vez...")
    # Carga el modelo de Whisper en memoria. La primera vez, lo descargará.
    try:
        model = whisper.load_model(MODEL_TYPE)
        print("¡Modelo cargado exitosamente!")
    except Exception as e:
        print(f"Error cargando el modelo de Whisper: {e}")
        print("Asegúrate de tener PyTorch instalado ('pip install torch').")
        print("También, verifica tu conexión a internet si es la primera vez que ejecutas esto.")
        return

    # --- Grabación de Audio ---
    print("\n-----------------------------------------")
    print(f"Comienza a hablar. La grabación durará {DURATION} segundos.")
    
    # Notifica al usuario con una cuenta regresiva
    for i in range(3, 0, -1):
        print(f"...{i}")
        time.sleep(1)
    print("¡HABLA AHORA!")

    try:
        # Graba audio desde el dispositivo de entrada por defecto
        recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()  # Espera a que la grabación termine
        print("Grabación finalizada.")
        print("-----------------------------------------")

        # Guarda la grabación en un archivo .wav temporal
        # Whisper espera una ruta de archivo, por lo que este paso es necesario.
        # Normalizamos y convertimos a int16, que es un formato de audio común.
        write(FILENAME, SAMPLE_RATE, (recording * 32767).astype(np.int16))

    except Exception as e:
        print(f"Error durante la grabación de audio: {e}")
        print("Asegúrate de tener un micrófono conectado y de que los permisos estén concedidos.")
        return

    # --- Transcripción con Whisper ---
    print("\nProcesando el audio con Whisper...")
    try:
        # Llama a Whisper para transcribir el archivo de audio
        result = model.transcribe(FILENAME)
        transcribed_text = result["text"]

        print("\n--- TRANSCRIPCIÓN ---")
        print(f"Texto reconocido: {transcribed_text}")
        print("----------------------\n")

    except Exception as e:
        print(f"Error durante la transcripción: {e}")

if __name__ == "__main__":
    main()