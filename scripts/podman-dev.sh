#!/bin/bash
# Script optimizado para desarrollo con Podman

echo "🐳 Iniciando Jarv1s con Podman..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar que Podman esté instalado
if ! command -v podman &> /dev/null; then
    error "Podman no está instalado. Instálalo con: sudo apt install podman"
    exit 1
fi

# Crear red si no existe
if ! podman network exists jarvis-network; then
    log "Creando red jarvis-network..."
    podman network create jarvis-network
fi

# Función de limpieza
cleanup() {
    log "🧹 Limpiando contenedores..."
    
    # Parar contenedores
    podman stop jarvis-backend jarvis-frontend lm-studio 2>/dev/null || true
    
    # Remover contenedores
    podman rm jarvis-backend jarvis-frontend lm-studio 2>/dev/null || true
    
    log "✅ Limpieza completada"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Construir imagen del backend
log "📦 Construyendo imagen del backend..."
if ! podman build -t jarvis-backend .; then
    error "Falló la construcción del backend"
    exit 1
fi

# Construir imagen del frontend si existe
if [ -f "frontend/Dockerfile" ]; then
    log "📦 Construyendo imagen del frontend..."
    podman build -t jarvis-frontend frontend/
fi

# Iniciar LM Studio (simulado con Ollama)
log "🧠 Iniciando servidor LLM..."
podman run -d \
    --name lm-studio \
    --network jarvis-network \
    -p 1234:11434 \
    -v ollama-data:/root/.ollama \
    ollama/ollama:latest \
    sh -c "ollama serve & sleep 10 && ollama pull phi3:mini && wait" || warn "No se pudo iniciar LLM server"

# Esperar a que el LLM esté listo
log "⏳ Esperando a que el LLM esté listo..."
sleep 15

# Iniciar backend
log "🚀 Iniciando backend..."
podman run -d \
    --name jarvis-backend \
    --network jarvis-network \
    -p 8000:8000 \
    -v ./src:/app/src:Z \
    -v ./models:/app/models:Z \
    -e LLM_API_BASE=http://lm-studio:11434/v1 \
    -e WHISPER_MODEL=small \
    -e DEBUG=true \
    jarvis-backend

# Iniciar frontend si la imagen existe
if podman image exists jarvis-frontend; then
    log "🎨 Iniciando frontend..."
    podman run -d \
        --name jarvis-frontend \
        --network jarvis-network \
        -p 5173:5173 \
        -v ./frontend/src:/app/src:Z \
        -e VITE_API_BASE_URL=http://localhost:8000 \
        jarvis-frontend
fi

# Mostrar estado
log "📊 Estado de los contenedores:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# URLs de acceso
log "🌐 URLs de acceso:"
log "   Backend API: http://localhost:8000"
log "   Frontend:    http://localhost:5173"
log "   LLM Server:  http://localhost:1234"

# Mostrar logs del backend
log "📋 Mostrando logs del backend (Ctrl+C para salir)..."
podman logs -f jarvis-backend

# Mantener el script corriendo
wait