import whisperx
import os
import torch
import subprocess
from tempfile import NamedTemporaryFile

# --- Configuración de WhisperX ---
# Leemos el modelo desde una variable de entorno, usando 'large-v2' como un
# excelente y potente valor por defecto que funciona bien en CPU con int8.
WHISPERX_MODEL = os.getenv("WHISPERX_MODEL_SIZE", "large-v2")
DEVICE = "cpu"
COMPUTE_TYPE = "int8" # ¡La clave para un alto rendimiento en CPU!

print("---------------------------------------------------------")
print(f"STT Service (WhisperX): Cargando modelo '{WHISPERX_MODEL}' en {DEVICE.upper()} con cómputo '{COMPUTE_TYPE}'...")

try:
    # Cargamos el modelo una sola vez cuando el servidor arranca.
    # Especificamos el español para optimizar la carga inicial.
    model = whisperx.load_model(WHISPERX_MODEL, device=DEVICE, compute_type=COMPUTE_TYPE, language="es")
    print("STT Service (WhisperX): Modelo cargado exitosamente.")
except Exception as e:
    print(f"Error cargando el modelo WhisperX: {e}")
    model = None

print("---------------------------------------------------------")


def transcribe_audio(audio_file_bytes: bytes) -> str:
    """
    Transcribe audio usando WhisperX. Primero convierte el audio a WAV con FFmpeg
    y luego lo procesa con el modelo WhisperX optimizado.
    """
    if not model:
        return "Error: El modelo de transcripción no está disponible."

    try:
        # Creamos un archivo temporal para el WAV de salida.
        with NamedTemporaryFile(suffix=".wav", delete=True) as temp_wav_file:
            wav_filename = temp_wav_file.name

            # 1. Usamos FFmpeg para una conversión robusta (como antes).
            ffmpeg_command = [
                "ffmpeg", "-i", "pipe:0", "-ac", "1", "-ar", "16000", "-f", "wav", "-y", wav_filename
            ]
            process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(input=audio_file_bytes)

            if process.returncode != 0:
                print(f"Error de FFmpeg al convertir a WAV: {stderr.decode()}")
                raise RuntimeError("FFmpeg falló al convertir el audio.")
            
            # 2. Cargamos el audio convertido con la función de utilidad de WhisperX.
            audio = whisperx.load_audio(wav_filename)
            
            print("Transcribiendo con WhisperX...")
            # 3. Transcribimos con el modelo precargado.
            #    Usamos un batch_size pequeño ya que procesamos un solo archivo.
            result = model.transcribe(audio, batch_size=4)
            
            # 4. Unimos los segmentos de texto para obtener la transcripción completa.
            #    WhisperX devuelve una lista de segmentos, que es muy útil para el futuro.
            transcribed_text = " ".join([segment['text'].strip() for segment in result["segments"]])
            print(f"Texto transcrito (WhisperX): '{transcribed_text}'")
    
    except Exception as e:
        print(f"Error durante la transcripción con WhisperX: {e}")
        return "" # Devolvemos una cadena vacía en caso de error

    return transcribed_text