#!/bin/bash
# Script de desarrollo rápido - Solo reconstruye lo que cambió

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Jarv1s - Desarrollo Rápido${NC}"

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar si hay cambios en dependencias
REBUILD_BACKEND=false
REBUILD_FRONTEND=false

if [ ! -f ".dev-cache/backend-deps.hash" ] || ! sha256sum -c .dev-cache/backend-deps.hash &>/dev/null; then
    log "Detectados cambios en dependencias del backend"
    REBUILD_BACKEND=true
    mkdir -p .dev-cache
    sha256sum pyproject.toml requirements.txt > .dev-cache/backend-deps.hash
fi

if [ ! -f ".dev-cache/frontend-deps.hash" ] || ! sha256sum -c .dev-cache/frontend-deps.hash &>/dev/null; then
    log "Detectados cambios en dependencias del frontend"
    REBUILD_FRONTEND=true
    mkdir -p .dev-cache
    sha256sum frontend/package.json frontend/package-lock.json > .dev-cache/frontend-deps.hash 2>/dev/null || true
fi

# Verificar si las imágenes existen
if ! podman image exists jarvis-backend-dev; then
    log "Imagen del backend no existe, construyendo..."
    REBUILD_BACKEND=true
fi

if ! podman image exists jarvis-frontend-dev; then
    log "Imagen del frontend no existe, construyendo..."
    REBUILD_FRONTEND=true
fi

# Construir solo lo necesario
if [ "$REBUILD_BACKEND" = true ]; then
    log "🔨 Construyendo imagen del backend..."
    podman build -f Dockerfile.dev -t jarvis-backend-dev .
else
    log "✅ Backend: usando imagen cacheada"
fi

if [ "$REBUILD_FRONTEND" = true ]; then
    log "🔨 Construyendo imagen del frontend..."
    podman build -f frontend/Dockerfile -t jarvis-frontend-dev frontend/
else
    log "✅ Frontend: usando imagen cacheada"
fi

# Parar contenedores existentes si están corriendo
log "🛑 Parando contenedores existentes..."
podman stop jarvis-backend-dev jarvis-frontend-dev jarvis-lm-studio 2>/dev/null || true

# Crear red si no existe
if ! podman network exists jarvis-dev-network; then
    log "🌐 Creando red de desarrollo..."
    podman network create jarvis-dev-network
fi

# Iniciar LM Studio (Ollama) si no está corriendo
if ! podman container exists jarvis-lm-studio || [ "$(podman inspect jarvis-lm-studio --format='{{.State.Status}}')" != "running" ]; then
    log "🧠 Iniciando LM Studio..."
    podman run -d \
        --name jarvis-lm-studio \
        --network jarvis-dev-network \
        -p 1234:11434 \
        -v jarvis-ollama-data:/root/.ollama \
        -e OLLAMA_HOST=0.0.0.0 \
        ollama/ollama:latest \
        sh -c "ollama serve & sleep 15 && ollama pull phi3:mini && wait" || warn "No se pudo iniciar LM Studio"
fi

# Iniciar backend con volúmenes para desarrollo en vivo
log "🚀 Iniciando backend de desarrollo..."
podman run -d \
    --name jarvis-backend-dev \
    --network jarvis-dev-network \
    -p 8000:8000 \
    -v ./src:/app/src:Z \
    -v ./tests:/app/tests:Z \
    -v ./scripts:/app/scripts:Z \
    -v jarvis-models:/app/models \
    -v ./logs:/app/logs:Z \
    -v ./.env:/app/.env:Z \
    -e LLM_API_BASE=http://jarvis-lm-studio:11434/v1 \
    -e WHISPERX_MODEL_SIZE=small \
    -e DEBUG=true \
    -e LOG_LEVEL=DEBUG \
    jarvis-backend-dev

# Iniciar frontend con volúmenes para hot-reload
log "🎨 Iniciando frontend de desarrollo..."
podman run -d \
    --name jarvis-frontend-dev \
    --network jarvis-dev-network \
    -p 5173:5173 \
    -v ./frontend/src:/app/src:Z \
    -v ./frontend/public:/app/public:Z \
    -v jarvis-node-modules:/app/node_modules \
    -e VITE_API_BASE_URL=http://localhost:8000 \
    jarvis-frontend-dev

# Mostrar estado
log "📊 Estado de los contenedores:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep jarvis

# URLs de acceso
log "🌐 URLs de acceso:"
log "   Backend API: http://localhost:8000"
log "   Frontend:    http://localhost:5173"
log "   LLM Server:  http://localhost:1234"

log "✅ Desarrollo iniciado. Los cambios en el código se reflejarán automáticamente."
log "📋 Para ver logs: podman logs -f jarvis-backend-dev"
log "🛑 Para parar: podman stop jarvis-backend-dev jarvis-frontend-dev"