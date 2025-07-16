# Referencia de API - Jarv1s

## Visión General

La API de Jarv1s está construida con FastAPI y proporciona endpoints RESTful para interactuar con el sistema de IA conversacional. Todos los endpoints están disponibles en `http://localhost:8000` por defecto.

## Autenticación

Actualmente, la API no requiere autenticación ya que está diseñada para uso local. En futuras versiones se implementará autenticación para acceso remoto.

## Endpoints Principales

### POST /interact

Endpoint principal para la interacción conversacional completa.

**URL**: `/interact`  
**Método**: `POST`  
**Content-Type**: `multipart/form-data`

#### Parámetros de Entrada

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `audio` | File | Sí | Archivo de audio en formato WebM, WAV, MP3 o M4A |

#### Ejemplo de Request

```bash
curl -X POST "http://localhost:8000/interact" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@recording.webm"
```

#### Respuesta Exitosa

**Código**: `200 OK`  
**Content-Type**: `application/json`

```json
{
  "transcription": "Hola, ¿cómo estás?",
  "response": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
  "processing_time": {
    "stt": 1.23,
    "llm": 0.87,
    "tts": 0.45,
    "total": 2.55
  }
}
```

#### Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `transcription` | string | Texto transcrito del audio de entrada |
| `response` | string | Respuesta generada por el LLM |
| `audio_base64` | string | Audio de respuesta codificado en base64 (formato WAV) |
| `processing_time` | object | Tiempos de procesamiento de cada componente |

#### Errores Posibles

**400 Bad Request**
```json
{
  "detail": "No audio file provided"
}
```

**415 Unsupported Media Type**
```json
{
  "detail": "Unsupported audio format. Supported formats: webm, wav, mp3, m4a"
}
```

**500 Internal Server Error**
```json
{
  "detail": "STT processing failed: [error details]"
}
```

### GET /health

Endpoint para verificar el estado del sistema.

**URL**: `/health`  
**Método**: `GET`

#### Respuesta Exitosa

```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T10:30:00Z",
  "services": {
    "stt": "operational",
    "llm": "operational", 
    "tts": "operational"
  },
  "models": {
    "whisper": "small",
    "tts_voice": "es_ES-sharvard-medium"
  }
}
```

### GET /conversation/history

Obtiene el historial de la conversación actual.

**URL**: `/conversation/history`  
**Método**: `GET`

#### Respuesta Exitosa

```json
{
  "history": [
    {
      "role": "user",
      "content": "Hola, ¿cómo estás?",
      "timestamp": "2025-01-16T10:25:00Z"
    },
    {
      "role": "assistant", 
      "content": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
      "timestamp": "2025-01-16T10:25:02Z"
    }
  ],
  "message_count": 2
}
```

### DELETE /conversation/history

Limpia el historial de conversación.

**URL**: `/conversation/history`  
**Método**: `DELETE`

#### Respuesta Exitosa

```json
{
  "message": "Conversation history cleared",
  "cleared_messages": 4
}
```

## Endpoints de Servicios Individuales

### POST /stt/transcribe

Transcribe audio a texto usando solo el servicio STT.

**URL**: `/stt/transcribe`  
**Método**: `POST`  
**Content-Type**: `multipart/form-data`

#### Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `audio` | File | Sí | Archivo de audio |

#### Respuesta

```json
{
  "transcription": "Texto transcrito del audio",
  "processing_time": 1.23,
  "model_used": "small"
}
```

### POST /llm/generate

Genera respuesta usando solo el servicio LLM.

**URL**: `/llm/generate`  
**Método**: `POST`  
**Content-Type**: `application/json`

#### Parámetros

```json
{
  "message": "Tu mensaje aquí",
  "include_history": true
}
```

#### Respuesta

```json
{
  "response": "Respuesta generada por el LLM",
  "processing_time": 0.87,
  "tokens_used": 45
}
```

### POST /tts/synthesize

Sintetiza texto a audio usando solo el servicio TTS.

**URL**: `/tts/synthesize`  
**Método**: `POST`  
**Content-Type**: `application/json`

#### Parámetros

```json
{
  "text": "Texto a sintetizar",
  "voice": "es_ES-sharvard-medium"
}
```

#### Respuesta

```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
  "processing_time": 0.45,
  "audio_duration": 2.1
}
```

## Configuración y Estado

### GET /config

Obtiene la configuración actual del sistema.

**URL**: `/config`  
**Método**: `GET`

#### Respuesta

```json
{
  "llm": {
    "api_base": "http://localhost:1234/v1",
    "model_name": "openai/lmstudio-local-model"
  },
  "stt": {
    "model": "small",
    "language": "auto"
  },
  "tts": {
    "voice": "es_ES-sharvard-medium",
    "sample_rate": 22050
  }
}
```

### POST /config

Actualiza la configuración del sistema.

**URL**: `/config`  
**Método**: `POST`  
**Content-Type**: `application/json`

#### Parámetros

```json
{
  "llm": {
    "model_name": "nuevo-modelo"
  },
  "stt": {
    "model": "base"
  }
}
```

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Operación exitosa |
| 400 | Solicitud malformada o parámetros inválidos |
| 415 | Tipo de media no soportado |
| 422 | Error de validación de datos |
| 500 | Error interno del servidor |
| 503 | Servicio no disponible (modelo no cargado) |

## Límites y Restricciones

### Archivos de Audio
- **Tamaño máximo**: 50MB
- **Duración máxima**: 10 minutos
- **Formatos soportados**: WebM, WAV, MP3, M4A
- **Sample rate recomendado**: 16kHz

### Rate Limiting
- **Requests por minuto**: 60
- **Requests concurrentes**: 5

### Timeouts
- **STT processing**: 30 segundos
- **LLM generation**: 60 segundos  
- **TTS synthesis**: 15 segundos

## Ejemplos de Uso

### JavaScript/TypeScript (Frontend)

```typescript
// Enviar audio para interacción completa
const interactWithJarvis = async (audioBlob: Blob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob);
  
  try {
    const response = await fetch('http://localhost:8000/interact', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    // Reproducir audio de respuesta
    const audioData = atob(data.audio_base64);
    const audioBlob = new Blob([audioData], { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
    
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Python (Cliente)

```python
import requests
import base64
import io
from pydub import AudioSegment
from pydub.playback import play

def interact_with_jarvis(audio_file_path: str):
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post('http://localhost:8000/interact', files=files)
    
    if response.status_code == 200:
        data = response.json()
        
        # Decodificar y reproducir audio
        audio_data = base64.b64decode(data['audio_base64'])
        audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))
        play(audio_segment)
        
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Uso
result = interact_with_jarvis('mi_grabacion.wav')
print(f"Transcripción: {result['transcription']}")
print(f"Respuesta: {result['response']}")
```

### cURL

```bash
# Interacción completa
curl -X POST "http://localhost:8000/interact" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@recording.webm" \
  | jq '.'

# Solo transcripción
curl -X POST "http://localhost:8000/stt/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@recording.webm" \
  | jq '.transcription'

# Solo generación de texto
curl -X POST "http://localhost:8000/llm/generate" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿cómo estás?", "include_history": true}' \
  | jq '.response'
```

## WebSocket API (Futuro)

En futuras versiones se implementará una API WebSocket para streaming en tiempo real:

```typescript
// Ejemplo futuro de WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'transcription_partial') {
    console.log('Transcripción parcial:', data.text);
  }
};

// Enviar audio en chunks
const sendAudioChunk = (audioChunk: ArrayBuffer) => {
  ws.send(audioChunk);
};
```