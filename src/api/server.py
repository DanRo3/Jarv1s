"""
FastAPI server for Jarv1s backend.
Handles voice interaction endpoints with robust error handling and fallback mechanisms.
"""

import base64
import time
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..config.settings import get_settings
from ..utils.logger import get_api_logger
from ..utils.exceptions import JarvisBaseException, STTException, LLMException, TTSException
from ..services.stt_service import get_stt_service
from ..services.llm_service import get_llm_service
from ..services.tts_service import get_tts_service


# Response models
class InteractionResponse(BaseModel):
    """Response model for interaction endpoint."""
    transcription: str
    response: str
    audio_base64: str
    processing_time: Dict[str, float]


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    status: str
    timestamp: str
    services: Dict[str, str]
    models: Dict[str, str]


class ResetResponse(BaseModel):
    """Response model for reset endpoint."""
    status: str
    message: str


# Initialize FastAPI app
settings = get_settings()
logger = get_api_logger()

app = FastAPI(
    title=settings.app_name + " Backend API",
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global fallback audio storage
fallback_audio_cache: Dict[str, Optional[bytes]] = {
    "no_transcription": None,
    "internal_error": None
}


class FallbackManager:
    """Manages fallback responses for error scenarios."""
    
    def __init__(self):
        self.logger = get_api_logger()
        self.settings = get_settings()
    
    def preload_fallback_audio(self) -> None:
        """Preload fallback audio responses during startup."""
        global fallback_audio_cache
        
        self.logger.info("Preloading fallback audio responses")
        
        try:
            tts_service = get_tts_service()
            
            # Generate fallback audio for no transcription
            no_transcription_audio, _ = tts_service.synthesize_audio(
                self.settings.fallback_no_transcription
            )
            fallback_audio_cache["no_transcription"] = no_transcription_audio
            
            # Generate fallback audio for internal errors
            internal_error_audio, _ = tts_service.synthesize_audio(
                self.settings.fallback_internal_error
            )
            fallback_audio_cache["internal_error"] = internal_error_audio
            
            self.logger.info("Fallback audio responses preloaded successfully")
            
        except Exception as e:
            self.logger.warning(
                f"Failed to preload fallback audio: {e}. "
                "System will work but error responses may not have audio."
            )
    
    def get_fallback_response(self, fallback_type: str) -> Dict[str, str]:
        """Get a fallback response for error scenarios."""
        if fallback_type == "no_transcription":
            text = self.settings.fallback_no_transcription
            audio = fallback_audio_cache.get("no_transcription")
        elif fallback_type == "internal_error":
            text = self.settings.fallback_internal_error
            audio = fallback_audio_cache.get("internal_error")
        else:
            text = "An unexpected error occurred."
            audio = None
        
        audio_base64 = ""
        if audio:
            audio_base64 = base64.b64encode(audio).decode('utf-8')
        
        return {
            "transcription": "",
            "response": text,
            "audio_base64": audio_base64
        }


# Initialize fallback manager
fallback_manager = FallbackManager()


@app.on_event("startup")
async def startup_event():
    """Initialize services and preload fallback responses."""
    logger.info(f"Starting {settings.app_name} API server v{settings.app_version}")
    
    # Preload fallback audio
    fallback_manager.preload_fallback_audio()
    
    # Log service availability
    stt_service = get_stt_service()
    llm_service = get_llm_service()
    tts_service = get_tts_service()
    
    logger.info(f"STT Service available: {stt_service.is_available()}")
    logger.info(f"LLM Service available: {llm_service.is_available()}")
    logger.info(f"TTS Service available: {tts_service.is_available()}")
    
    logger.info("Startup completed successfully")


@app.post("/interact", response_model=InteractionResponse)
async def interact(audio_file: UploadFile = File(...)):
    """
    Complete voice interaction cycle: STT -> LLM -> TTS.
    
    Handles the full conversation pipeline with robust error handling
    and fallback mechanisms to ensure the API never returns errors.
    """
    start_time = time.time()
    processing_times = {}
    
    logger.info("Processing voice interaction request")
    
    try:
        # Step 1: Speech-to-Text
        stt_start = time.time()
        audio_bytes = await audio_file.read()
        
        stt_service = get_stt_service()
        user_text = stt_service.transcribe_audio(audio_bytes)
        processing_times["stt"] = round(time.time() - stt_start, 3)
        
        logger.info(f"Transcription completed: '{user_text}'")
        
        # Handle empty transcription
        if not user_text.strip():
            logger.info("Empty transcription, returning fallback response")
            fallback_response = fallback_manager.get_fallback_response("no_transcription")
            fallback_response["processing_time"] = processing_times
            return fallback_response
        
        # Step 2: LLM Processing
        llm_start = time.time()
        llm_service = get_llm_service()
        llm_response = llm_service.get_response(user_text)
        processing_times["llm"] = round(time.time() - llm_start, 3)
        
        logger.info(f"LLM response generated: '{llm_response}'")
        
        # Step 3: Text-to-Speech
        tts_start = time.time()
        tts_service = get_tts_service()
        response_audio_bytes, _ = tts_service.synthesize_audio(llm_response)
        processing_times["tts"] = round(time.time() - tts_start, 3)
        
        # Encode audio to base64
        response_audio_base64 = base64.b64encode(response_audio_bytes).decode('utf-8')
        
        # Calculate total processing time
        processing_times["total"] = round(time.time() - start_time, 3)
        
        logger.info(f"Interaction completed successfully in {processing_times['total']}s")
        
        return {
            "transcription": user_text,
            "response": llm_response,
            "audio_base64": response_audio_base64,
            "processing_time": processing_times
        }
        
    except JarvisBaseException as e:
        # Handle known service exceptions
        logger.error(f"Service error during interaction: {e}")
        fallback_response = fallback_manager.get_fallback_response("internal_error")
        fallback_response["processing_time"] = processing_times
        return fallback_response
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during interaction: {e}")
        fallback_response = fallback_manager.get_fallback_response("internal_error")
        fallback_response["processing_time"] = processing_times
        return fallback_response


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Get the health status of all services."""
    from datetime import datetime
    
    stt_service = get_stt_service()
    llm_service = get_llm_service()
    tts_service = get_tts_service()
    
    services_status = {
        "stt": "operational" if stt_service.is_available() else "unavailable",
        "llm": "operational" if llm_service.is_available() else "unavailable",
        "tts": "operational" if tts_service.is_available() else "unavailable"
    }
    
    models_info = {
        "whisper": settings.stt.model_size,
        "tts_voice": settings.tts.model_path.split('/')[-1].replace('.onnx', '')
    }
    
    overall_status = "healthy" if all(
        status == "operational" for status in services_status.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": services_status,
        "models": models_info
    }


@app.post("/reset", response_model=ResetResponse)
async def reset_conversation():
    """Reset the conversation history."""
    logger.info("Resetting conversation history")
    
    try:
        llm_service = get_llm_service()
        result = llm_service.reset_conversation()
        logger.info("Conversation history reset successfully")
        return result
        
    except Exception as e:
        logger.error(f"Failed to reset conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "status": "online",
        "docs": "/docs"
    }


@app.get("/conversation/info")
async def get_conversation_info():
    """Get information about the current conversation."""
    try:
        llm_service = get_llm_service()
        return llm_service.get_conversation_info()
    except Exception as e:
        logger.error(f"Failed to get conversation info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation info")