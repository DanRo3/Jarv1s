import whisper
import torch
import os
from tempfile import NamedTemporaryFile
import subprocess

# Configuración (sin cambios)
WHISPER_MODEL = os.getenv("WHISPER_MODEL_SIZE", "small")
DEVICE = "cpu"

print("---------------------------------------------------------")
print(f"STT Service: Cargando modelo Whisper '{WHISPER_MODEL}' en {DEVICE.upper()}...")
try:
    model = whisper.load_model(WHISPER_MODEL, device=DEVICE)
    print("STT Service: Modelo Whisper cargado exitosamente.")
except Exception as e:
    print(f"Error cargando el modelo Whisper: {e}")
    model = None
print("---------------------------------------------------------")


def transcribe_audio(audio_file_bytes: bytes) -> str:
    """
    Transcribe audio usando un método robusto de archivo a archivo con ffmpeg.
    """
    if not model:
        return "Error: El modelo de transcripción no está disponible."

    try:
        # 1. Creamos un archivo temporal para el audio WEBM de entrada.
        with NamedTemporaryFile(delete=True, suffix=".webm") as temp_webm_file:
            temp_webm_file.write(audio_file_bytes)
            temp_webm_file.flush() # Asegura que todos los bytes se escriban en disco.
            
            # 2. Creamos otro archivo temporal para el audio WAV de salida.
            with NamedTemporaryFile(delete=True, suffix=".wav") as temp_wav_file:
                input_filename = temp_webm_file.name
                output_filename = temp_wav_file.name

                # 3. Construimos el comando FFmpeg para convertir de archivo a archivo.
                ffmpeg_command = [
                    "ffmpeg",
                    "-i", input_filename,   # <-- Leemos desde el archivo de entrada
                    "-ac", "1",
                    "-ar", "16000",
                    "-y", output_filename, # <-- Escribimos en el archivo de salida
                ]

                # 4. Ejecutamos el comando de forma más simple y segura con 'run'.
                print("Ejecutando conversión de archivo a archivo con FFmpeg...")
                result = subprocess.run(
                    ffmpeg_command, 
                    capture_output=True, 
                    text=True
                )

                # 5. Verificamos el resultado.
                if result.returncode != 0:
                    print("¡Error de FFmpeg!")
                    print("STDERR:", result.stderr)
                    raise RuntimeError("FFmpeg falló al convertir el audio.")
                
                print("Conversión completada. Transcribiendo...")
                
                # 6. Transcribimos el archivo WAV de salida.
                transcription_result = model.transcribe(output_filename)
                transcribed_text = transcription_result["text"].strip()
                print(f"Texto transcrito: {transcribed_text}")
    
    except Exception as e:
        print(f"Error durante la transcripción o conversión: {e}")
        return "Error al procesar el audio."

    return transcribed_text