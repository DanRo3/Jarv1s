# src/api/server.py (Versión Final con Manejo de Errores a Prueba de Balas)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import time

# Importamos todos nuestros servicios como siempre
from ..services.stt_service import transcribe_audio
from ..services.llm_service import get_llm_response, reset_conversation
from ..services.tts_service import synthesize_audio

# --- 1. Definición de la Aplicación y Configuración de CORS ---
# Esto no cambia, pero es el primer bloque de nuestro archivo.
app = FastAPI(
    title="Jarv1s Backend API",
    version="1.0.0-RC1", # ¡Versión Candidata a Release!
)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Central de Mensajes y Almacén de Audios de Fallback ---
# Centralizamos aquí todos los mensajes y variables que usaremos para los errores.
# Si queremos cambiar un mensaje de error, solo lo hacemos en un lugar.
FALLBACK_NO_TRANSCRIPTION_TEXT = "Disculpa, no te he escuchado bien. ¿Podrías repetirlo?"
FALLBACK_INTERNAL_ERROR_TEXT = "Lo siento, estoy teniendo un problema técnico. Por favor, inténtalo de nuevo en un momento."

# Estas variables globales guardarán los bytes de audio pre-generados.
# Empiezan como None.
fallback_no_transcription_audio: bytes | None = None
fallback_internal_error_audio: bytes | None = None


# --- 3. Lógica de Arranque del Servidor: El Kit de Emergencia ---
@app.on_event("startup")
def preload_fallback_audio():
    """
    Esta función especial se ejecuta UNA SOLA VEZ cuando lanzas Uvicorn.
    Su trabajo es crear nuestros audios de emergencia y guardarlos en las
    variables globales. Así, si el servicio TTS falla durante una petición,
    seguiremos teniendo una respuesta de audio lista para enviar.
    """
    global fallback_no_transcription_audio, fallback_internal_error_audio
    print("---------------------------------------------------------")
    print("STARTUP: Pre-sintetizando audios de fallback...")
    try:
        # Intentamos generar el audio para el caso de "no transcripción"
        fallback_no_transcription_audio, _ = synthesize_audio(FALLBACK_NO_TRANSCRIPTION_TEXT)
        # Intentamos generar el audio para el caso de "error interno"
        fallback_internal_error_audio, _ = synthesize_audio(FALLBACK_INTERNAL_ERROR_TEXT)
        print("STARTUP: Audios de fallback creados y listos.")
    except Exception as e:
        print(f"STARTUP WARNING: No se pudieron crear los audios de fallback. El sistema funcionará, pero las respuestas de error no tendrán voz si el TTS falla. Error: {e}")
    print("---------------------------------------------------------")


# --- 4. El Endpoint Principal: Ahora a Prueba de Balas ---
@app.post("/interact", summary="Ciclo completo de interacción con Jarv1s")
async def interact(audio_file: UploadFile = File(...)):
    """
    Este endpoint ahora maneja todos los casos posibles para nunca fallar.
    """
    start_time = time.time()
    try:
        # --- El "Camino Feliz" ---
        
        # 1. OÍR: Intentamos transcribir el audio.
        audio_bytes = await audio_file.read()
        user_text = transcribe_audio(audio_bytes)
        
        # 2. MANEJO DE SILENCIO: Si la transcripción está vacía, no continuamos.
        #    Devolvemos directamente la respuesta de fallback que ya tenemos preparada.
        if not user_text:
            print("HANDLER: Transcripción vacía. Devolviendo fallback de 'no-entendido'.")
            if fallback_no_transcription_audio:
                audio_base64 = base64.b64encode(fallback_no_transcription_audio).decode('utf-8')
                return {"responseText": FALLBACK_NO_TRANSCRIPTION_TEXT, "responseAudio": audio_base64}
            else: # Si la pre-síntesis falló, al menos devolvemos el texto.
                return {"responseText": FALLBACK_NO_TRANSCRIPTION_TEXT, "responseAudio": ""}

        # 3. PENSAR: Si hay texto, se lo pasamos al LLM.
        llm_response_text = get_llm_response(user_text)
        
        # 4. HABLAR: Sintetizamos la respuesta del LLM.
        response_audio_bytes, _ = synthesize_audio(llm_response_text)
        response_audio_base64 = base64.b64encode(response_audio_bytes).decode('utf-8')
        
        # 5. Devolvemos la respuesta exitosa.
        return {
            "responseText": llm_response_text,
            "responseAudio": response_audio_base64,
            "processing_time_seconds": round(time.time() - start_time, 2)
        }
            
    except Exception as e:
        # --- El "Paracaídas" ---
        # Si CUALQUIER cosa en el bloque `try` de arriba falla (el LLM, el TTS, etc.),
        # caemos aquí. En lugar de devolver un error 500, construimos una
        # respuesta de error amigable para el usuario.
        print(f"HANDLER: Error 500 capturado: {e}. Devolviendo fallback de 'error-interno'.")
        if fallback_internal_error_audio:
            audio_base64 = base64.b64encode(fallback_internal_error_audio).decode('utf-8')
            return {"responseText": FALLBACK_INTERNAL_ERROR_TEXT, "responseAudio": audio_base64}
        else:
            return {"responseText": FALLBACK_INTERNAL_ERROR_TEXT, "responseAudio": ""}


# --- Endpoints Auxiliares (sin cambios) ---
@app.get("/")
async def root():
    return {"status": "ok", "message": "Jarv1s API está en línea."}

@app.post("/reset")
async def reset_memory():
    return reset_conversation()