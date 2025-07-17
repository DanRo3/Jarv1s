# Dockerfile para Jarv1s
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak-ng \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml requirements.txt ./
COPY .env.example .env

# Instalar dependencias de Python
RUN pip install --no-cache-dir -e .

# Crear directorio para modelos
RUN mkdir -p models/tts

# Descargar modelos TTS automáticamente
RUN wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx \
    -O models/tts/es_ES-sharvard-medium.onnx && \
    wget -q https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json \
    -O models/tts/es_ES-sharvard-medium.onnx.json

# Copiar código fuente
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Exponer puerto del backend
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]