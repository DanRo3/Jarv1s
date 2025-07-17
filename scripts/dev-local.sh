#!/bin/bash
# Script para desarrollo local sin contenedores

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}💻 Jarv1s - Desarrollo Local${NC}"

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    log "Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
log "Activando entorno virtual..."
source .venv/bin/activate

# Verificar si hay cambios en dependencias
if [ ! -f ".dev-cache/local-deps.hash" ] || ! sha256sum -c .dev-cache/local-deps.hash &>/dev/null; then
    log "Instalando/actualizando dependencias..."
    pip install --upgrade pip
    pip install -e .
    
    mkdir -p .dev-cache
    sha256sum pyproject.toml requirements.txt > .dev-cache/local-deps.hash
else
    log "✅ Dependencias actualizadas"
fi

# Verificar modelos TTS
if [ ! -f "models/tts/es_ES-sharvard-medium.onnx" ]; then
    log "Descargando modelos TTS..."
    mkdir -p models/tts
    
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx \
        -O models/tts/es_ES-sharvard-medium.onnx
    
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json \
        -O models/tts/es_ES-sharvard-medium.onnx.json
    
    log "✅ Modelos TTS descargados"
else
    log "✅ Modelos TTS disponibles"
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    log "Creando archivo .env desde template..."
    cp .env.example .env
    warn "Revisa y actualiza el archivo .env con tu configuración"
fi

# Verificar LM Studio
log "Verificando conexión con LM Studio..."
if curl -s http://localhost:1234/v1/models > /dev/null; then
    log "✅ LM Studio conectado"
else
    warn "⚠️  LM Studio no detectado en http://localhost:1234"
    warn "   Asegúrate de que LM Studio esté corriendo con un modelo cargado"
fi

# Crear directorio de logs
mkdir -p logs

log "🚀 Iniciando servidor de desarrollo..."
log "   Backend: http://localhost:8000"
log "   Docs: http://localhost:8000/docs"

# Iniciar servidor con auto-reload
python -m src.main