#!/bin/bash
# Script para desarrollo con Podman

echo "🐳 Iniciando Jarv1s con Podman..."

# Verificar si podman-compose está disponible
if command -v podman-compose &> /dev/null; then
    echo "📦 Usando podman-compose..."
    
    # Construir imágenes
    echo "📦 Construyendo imágenes..."
    podman-compose build
    
    # Iniciar servicios
    echo "🚀 Iniciando servicios..."
    podman-compose up -d
    
    # Mostrar logs
    echo "📋 Mostrando logs..."
    podman-compose logs -f jarvis-backend
    
    # Función de limpieza
    cleanup() {
        echo "🧹 Limpiando contenedores..."
        podman-compose down
        exit 0
    }
else
    echo "📦 Usando podman con pod..."
    
    # Crear pod si no existe
    if ! podman pod exists jarvis-pod; then
        echo "🔧 Creando pod jarvis-pod..."
        podman pod create --name jarvis-pod -p 8000:8000 -p 5173:5173 -p 1234:1234
    fi
    
    # Construir imagen
    echo "📦 Construyendo imagen backend..."
    podman build -t jarvis-backend .
    
    # Iniciar contenedores en el pod
    echo "🚀 Iniciando backend..."
    podman run -d --pod jarvis-pod --name jarvis-backend-container jarvis-backend
    
    # Mostrar logs
    echo "📋 Mostrando logs..."
    podman logs -f jarvis-backend-container
    
    # Función de limpieza
    cleanup() {
        echo "🧹 Limpiando contenedores y pod..."
        podman stop jarvis-backend-container 2>/dev/null || true
        podman rm jarvis-backend-container 2>/dev/null || true
        podman pod stop jarvis-pod 2>/dev/null || true
        podman pod rm jarvis-pod 2>/dev/null || true
        exit 0
    }
fi

# Capturar Ctrl+C
trap cleanup SIGINT

# Mantener el script corriendo
wait