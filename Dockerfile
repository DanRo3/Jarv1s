# Multi-stage Dockerfile para Jarv1s - Optimizado para desarrollo
FROM python:3.11-slim as base

# Instalar dependencias del sistema (se cachea)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak-ng \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Stage para descargar modelos (se cachea hasta que cambien los modelos)
FROM base as models
RUN mkdir -p models/tts
RUN wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx \
    -O models/tts/es_ES-sharvard-medium.onnx && \
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json \
    -O models/tts/es_ES-sharvard-medium.onnx.json

# Stage para dependencias Python (se cachea hasta que cambien requirements)
FROM base as dependencies
COPY pyproject.toml requirements.txt README.md ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage final - Solo se reconstruye cuando cambia el código
FROM dependencies as final

# Copiar modelos desde stage anterior
COPY --from=models /app/models ./models

# Copiar configuración
COPY .env.example .env

# Copiar código fuente (esto cambia frecuentemente)
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Instalar el paquete en modo desarrollo
RUN pip install --no-cache-dir -e .

# Exponer puerto del backend
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]