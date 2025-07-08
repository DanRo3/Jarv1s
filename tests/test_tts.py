# tests/test_tts.py (Versión 6, usando el método correcto 'load')
import os
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

def main():
    model_path = "models/tts/es_ES-sharvard-medium.onnx"
    config_path = "models/tts/es_ES-sharvard-medium.onnx.json"

    print("Verificando la existencia de los archivos del modelo...")
    if not os.path.exists(model_path) or not os.path.exists(config_path):
        print("\n¡ERROR: Archivos de modelo no encontrados!")
        print("Asegúrate de que estás ejecutando el script desde la carpeta 'tests'.")
        return
    print("Archivos de modelo encontrados.")

    # --- MÉTODO CORRECTO PARA CARGAR LA VOZ ---
    # Usamos el factory method 'load' que se encarga de todo el proceso.
    print("\nCargando el modelo de voz de Piper usando el método 'load'...")
    try:
        voice = PiperVoice.load(model_path, config_path=config_path)
    except Exception as e:
        print(f"Error fatal al cargar el modelo de voz: {e}")
        return
    print("¡Modelo cargado exitosamente!")

    # Una vez que 'voice' está cargado correctamente, AHORA SÍ podemos acceder a su configuración.
    samplerate = voice.config.sample_rate
    print(f"Sample rate obtenido de la configuración del modelo: {samplerate}")

    text_to_speak = "Jarv1s, operativo. La voz de alta calidad está funcionando. Gracias por tu paciencia y por proporcionar la documentación que resolvió el problema."

    print(f"\nSintetizando el texto...")
    audio_data = b''
    # El método synthesize ahora devuelve un generador, lo iteramos
    for audio_bytes in voice.synthesize_stream_raw(text_to_speak):
        audio_data += audio_bytes
    
    print("Reproduciendo audio...")
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    sd.play(audio_array, samplerate=samplerate)
    sd.wait()

    print("\n¡Reproducción finalizada!")

if __name__ == "__main__":
    main()