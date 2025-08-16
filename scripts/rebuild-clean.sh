#!/bin/bash
# Script para rebuild completo - Usar cuando hay cambios importantes

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Jarv1s - Rebuild Completo${NC}"

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Confirmar acción
echo -e "${YELLOW}⚠️  Esto eliminará todas las imágenes y contenedores de Jarv1s${NC}"
read -p "¿Continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Operación cancelada"
    exit 0
fi

# Parar y eliminar contenedores
log "🛑 Parando y eliminando contenedores..."
podman stop jarvis-backend-dev jarvis-frontend-dev jarvis-lm-studio jarvis-backend jarvis-frontend lm-studio 2>/dev/null || true
podman rm jarvis-backend-dev jarvis-frontend-dev jarvis-lm-studio jarvis-backend jarvis-frontend lm-studio 2>/dev/null || true

# Eliminar imágenes de desarrollo
log "🗑️  Eliminando imágenes de desarrollo..."
podman rmi jarvis-backend-dev jarvis-frontend-dev jarvis-backend jarvis-frontend 2>/dev/null || true

# Limpiar cache de dependencias
log "🧹 Limpiando cache de dependencias..."
rm -rf .dev-cache/

# Limpiar imágenes huérfanas
log "🧽 Limpiando imágenes huérfanas..."
podman image prune -f

# Reconstruir imágenes
log "🔨 Reconstruyendo imagen del backend..."
podman build -f Dockerfile.dev -t jarvis-backend-dev . --no-cache

if [ -d "frontend" ]; then
    log "🔨 Reconstruyendo imagen del frontend..."
    podman build -f frontend/Dockerfile -t jarvis-frontend-dev frontend/ --no-cache
fi

# Actualizar hashes de dependencias
log "📝 Actualizando cache de dependencias..."
mkdir -p .dev-cache
sha256sum pyproject.toml requirements.txt > .dev-cache/backend-deps.hash
if [ -f "frontend/package.json" ]; then
    sha256sum frontend/package.json frontend/package-lock.json > .dev-cache/frontend-deps.hash 2>/dev/null || true
fi

log "✅ Rebuild completo terminado"
log "🚀 Ahora puedes usar: ./scripts/dev-fast.sh"