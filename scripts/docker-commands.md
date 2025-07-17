# Comandos Podman para Jarv1s

## Desarrollo Rápido
```bash
# Iniciar todo el stack
./scripts/podman-dev.sh

# O manualmente:
podman-compose up --build
# O si no tienes podman-compose:
podman play kube jarvis-pod.yaml
```

## Comandos Útiles

### Construcción
```bash
# Construir solo el backend
podman build -t jarvis-backend .

# Construir todo
podman-compose build
```

### Ejecución
```bash
# Iniciar en background
podman-compose up -d

# Ver logs en tiempo real
podman-compose logs -f jarvis-backend

# Parar todo
podman-compose down
```

### Debugging
```bash
# Entrar al contenedor del backend
podman exec -it jarvis-backend bash

# Ver logs específicos
podman logs jarvis-backend

# Reiniciar solo un servicio
podman restart jarvis-backend
```

### Limpieza
```bash
# Limpiar contenedores parados
podman container prune

# Limpiar imágenes no usadas
podman image prune

# Limpieza completa (¡cuidado!)
podman system prune -a
```

## URLs de Acceso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **LM Studio/Ollama**: http://localhost:1234

## Variables de Entorno

Crear `.env` con:
```bash
# LLM Configuration
LLM_API_BASE=http://lm-studio:1234/v1
LLM_MODEL_NAME=phi3:mini

# Whisper Configuration  
WHISPER_MODEL=small

# TTS Configuration
TTS_MODEL_PATH=models/tts/es_ES-sharvard-medium.onnx

# Development
DEBUG=true
LOG_LEVEL=INFO
```