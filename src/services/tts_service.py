from piper.voice import PiperVoice
import os
import wave  # <-- Importamos el módulo estándar de Python para archivos WAV
import io    # <-- Importamos el módulo para manejar bytes en memoria

# Configuración (sin cambios)
MODEL_PATH = os.getenv("TTS_MODEL_PATH", "models/tts/es_ES-sharvard-medium.onnx")
CONFIG_PATH = os.getenv("TTS_CONFIG_PATH", "models/tts/es_ES-sharvard-medium.onnx.json")

print("---------------------------------------------------------")
print(f"TTS Service: Cargando modelo Piper TTS desde {MODEL_PATH}...")
try:
    tts_model = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
    print("TTS Service: Modelo Piper TTS cargado exitosamente.")
except Exception as e:
    print(f"Error cargando el modelo Piper TTS: {e}")
    tts_model = None
print("---------------------------------------------------------")


def synthesize_audio(text: str) -> tuple[bytes, int]:
    """
    Sintetiza texto, genera audio PCM en bruto, y luego lo empaqueta
    en un archivo WAV completo y válido en memoria.
    """
    if not tts_model:
        raise RuntimeError("El modelo TTS no está disponible o no se cargó correctamente.")

    try:
        print(f"Sintetizando texto: {text}")
        samplerate = tts_model.config.sample_rate
        
        # 1. Obtenemos los datos de audio en bruto (PCM) de Piper
        audio_raw_bytes = b''
        for audio_bytes in tts_model.synthesize_stream_raw(text):
            audio_raw_bytes += audio_bytes
        
        print("Audio en bruto generado. Creando archivo WAV en memoria...")

        # 2. Creamos un "archivo" WAV en la memoria RAM
        wav_in_memory = io.BytesIO()
        with wave.open(wav_in_memory, 'wb') as wav_file:
            # 3. Configuramos la cabecera del WAV
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit audio (2 bytes por muestra)
            wav_file.setframerate(samplerate)
            
            # 4. Escribimos los datos de audio en bruto en el archivo
            wav_file.writeframes(audio_raw_bytes)

        # 5. Obtenemos el contenido completo del archivo en memoria (cabecera + datos)
        wav_bytes = wav_in_memory.getvalue()
        
        print("Archivo WAV en memoria creado exitosamente.")
        return wav_bytes, samplerate

    except Exception as e:
        print(f"Error durante la síntesis o creación del WAV: {e}")
        raise RuntimeError("Error al generar el audio.")