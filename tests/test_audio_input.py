# tests/test_audio_input.py
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time

# --- Configuración ---
SAMPLE_RATE = 16000
DURATION = 5
FILENAME = "audio_test_output.wav"

def main():
    """
    Script de diagnóstico para grabar y reproducir audio,
    y para analizar los datos grabados.
    """
    print("\n--- INICIANDO PRUEBA DE DIAGNÓSTICO DE AUDIO ---")
    print(f"La grabación durará {DURATION} segundos.")
    time.sleep(1)
    print("¡HABLA AHORA!")

    try:
        # 1. Grabar audio
        recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        print("Grabación finalizada.")

        # 2. Analizar el array de audio grabado
        # Si el micrófono funciona, estos valores no deberían ser cero.
        print("\n--- Análisis de la Señal de Audio ---")
        max_amplitude = np.max(np.abs(recording))
        print(f"Amplitud máxima de la señal: {max_amplitude:.4f}")
        
        if max_amplitude < 0.01:
            print("¡ADVERTENCIA! La señal es muy débil o inexistente. Revisa el micrófono.")
        else:
            print("Se detectó una señal de audio válida.")
        
        # 3. Reproducir el audio directamente desde la memoria
        print("\nReproduciendo la grabación directamente...")
        sd.play(recording, SAMPLE_RATE)
        sd.wait()
        print("Reproducción finalizada.")

        # 4. Guardar en un archivo (para doble verificación)
        print(f"\nGuardando la grabación en '{FILENAME}'...")
        write(FILENAME, SAMPLE_RATE, (recording * 32767).astype(np.int16))
        print("Archivo guardado.")
        
    except Exception as e:
        print(f"\nError durante la prueba de audio: {e}")
        print("Posibles causas:")
        print("- ¿Micrófono desconectado?")
        print("- ¿Permisos de acceso al micrófono denegados por el sistema operativo?")
        print("- ¿Otro programa está usando el micrófono?")

if __name__ == "__main__":
    main()