# Guía de Desarrollo para Jarv1s

## Configuración del Entorno de Desarrollo

### Prerrequisitos del Sistema

**Herramientas Esenciales**
```bash
# Linux/Ubuntu
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm ffmpeg espeak-ng

# macOS (con Homebrew)
brew install python@3.11 node ffmpeg espeak

# Windows (con Chocolatey)
choco install python nodejs ffmpeg
```

**Verificación de Instalación**
```bash
python3.11 --version  # >= 3.11.0
node --version         # >= 18.0.0
npm --version          # >= 8.0.0
ffmpeg -version        # Cualquier versión reciente
```

### Configuración del Proyecto

**1. Clonar y Configurar el Backend**
```bash
# Clonar el repositorio
git clone <repository-url>
cd jarv1s

# Crear entorno virtual
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -e .
```

**2. Descargar Modelos de IA**
```bash
# Crear directorio para modelos TTS
mkdir -p models/tts

# Descargar modelo de voz español
cd models/tts
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json
cd ../..
```

**3. Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

Contenido del `.env`:
```bash
# Configuración del LLM
LLM_API_BASE=http://localhost:1234/v1
LLM_MODEL_NAME=openai/lmstudio-local-model

# Configuración de Whisper
WHISPER_MODEL=small

# Configuración de TTS
TTS_MODEL_PATH=models/tts/es_ES-sharvard-medium.onnx
TTS_CONFIG_PATH=models/tts/es_ES-sharvard-medium.onnx.json

# Configuración del servidor
HOST=127.0.0.1
PORT=8000
DEBUG=true
```

**4. Configurar el Frontend**
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

### Configuración de LM Studio

**1. Instalación**
- Descargar desde [lmstudio.ai](https://lmstudio.ai)
- Instalar siguiendo las instrucciones del sistema operativo

**2. Configuración de Modelo**
```bash
# Modelos recomendados para desarrollo:
# - Phi-3-mini-4k-instruct-q4.gguf (1.6GB)
# - Llama-3.2-1B-Instruct-q4_0.gguf (0.8GB)
# - Qwen2.5-1.5B-Instruct-q4_0.gguf (1.0GB)
```

**3. Iniciar Servidor Local**
- Abrir LM Studio
- Ir a "Local Server"
- Cargar modelo seleccionado
- Iniciar servidor en puerto 1234

## Estructura del Proyecto

```
jarv1s/
├── docs/                    # Documentación
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # Servicios de API
│   │   └── utils/          # Utilidades
│   ├── public/             # Archivos estáticos
│   └── package.json
├── src/                    # Backend Python
│   ├── api/                # Endpoints FastAPI
│   ├── services/           # Servicios de IA
│   ├── agent/              # Lógica del agente (futuro)
│   └── main.py             # Punto de entrada
├── models/                 # Modelos de IA
│   └── tts/                # Modelos TTS
├── tests/                  # Tests y scripts de prueba
├── .env                    # Variables de entorno
├── pyproject.toml          # Configuración Python
└── README.md
```

## Flujo de Desarrollo

### 1. Desarrollo del Backend

**Iniciar el servidor de desarrollo**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar con recarga automática
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Estructura de un nuevo servicio**
```python
# src/services/nuevo_servicio.py
class NuevoServicio:
    def __init__(self):
        # Inicialización
        pass
    
    def procesar(self, entrada: str) -> str:
        # Lógica del servicio
        return resultado
```

**Agregar endpoint a la API**
```python
# src/api/server.py
from ..services.nuevo_servicio import NuevoServicio

nuevo_servicio = NuevoServicio()

@app.post("/nuevo-endpoint")
async def nuevo_endpoint(data: dict):
    resultado = nuevo_servicio.procesar(data["entrada"])
    return {"resultado": resultado}
```

### 2. Desarrollo del Frontend

**Iniciar el servidor de desarrollo**
```bash
cd frontend
npm run dev
```

**Estructura de un nuevo componente**
```typescript
// frontend/src/components/NuevoComponente.tsx
import React from 'react';

interface NuevoComponenteProps {
  prop1: string;
  prop2?: number;
}

const NuevoComponente: React.FC<NuevoComponenteProps> = ({ prop1, prop2 }) => {
  return (
    <div>
      {/* JSX del componente */}
    </div>
  );
};

export default NuevoComponente;
```

**Servicio para comunicación con API**
```typescript
// frontend/src/services/apiService.ts
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiService = {
  async nuevoEndpoint(data: any) {
    const response = await axios.post(`${API_BASE}/nuevo-endpoint`, data);
    return response.data;
  }
};
```

## Testing y Validación

### Tests del Backend

**Ejecutar tests individuales**
```bash
# Test de Whisper STT
python tests/test_whisper.py

# Test de Piper TTS
python tests/test_tts.py

# Test de conexión LLM
python tests/test_llm.py

# Test del bucle completo
python tests/test_full_loop.py
```

**Crear un nuevo test**
```python
# tests/test_nuevo_servicio.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.nuevo_servicio import NuevoServicio

def test_nuevo_servicio():
    servicio = NuevoServicio()
    resultado = servicio.procesar("entrada de prueba")
    
    assert resultado is not None
    assert isinstance(resultado, str)
    print(f"✅ Test pasado: {resultado}")

if __name__ == "__main__":
    test_nuevo_servicio()
```

### Tests del Frontend

```bash
cd frontend

# Ejecutar tests
npm test

# Ejecutar tests con cobertura
npm run test:coverage

# Ejecutar tests en modo watch
npm run test:watch
```

## Debugging y Troubleshooting

### Problemas Comunes del Backend

**1. Error de importación de módulos**
```bash
# Solución: Instalar en modo desarrollo
pip install -e .
```

**2. Whisper no encuentra el modelo**
```bash
# Verificar instalación
python -c "import whisper; print(whisper.available_models())"

# Reinstalar si es necesario
pip uninstall openai-whisper
pip install openai-whisper
```

**3. Piper TTS no encuentra archivos**
```bash
# Verificar rutas de modelos
ls -la models/tts/
```

**4. LM Studio no responde**
```bash
# Verificar conexión
curl http://localhost:1234/v1/models

# Verificar logs del servidor
tail -f logs/server.log
```

### Problemas Comunes del Frontend

**1. CORS errors**
```typescript
// Verificar configuración en backend
// src/api/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**2. Permisos de micrófono**
```typescript
// Verificar en navegador
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => console.log("✅ Micrófono OK"))
  .catch(err => console.error("❌ Error micrófono:", err));
```

### Logging y Monitoreo

**Backend Logging**
```python
# src/services/base_service.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseService:
    def log_info(self, message: str):
        logger.info(f"[{self.__class__.__name__}] {message}")
    
    def log_error(self, message: str, error: Exception = None):
        logger.error(f"[{self.__class__.__name__}] {message}")
        if error:
            logger.error(f"Error details: {str(error)}")
```

**Frontend Logging**
```typescript
// frontend/src/utils/logger.ts
export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data);
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error);
  },
  debug: (message: string, data?: any) => {
    if (import.meta.env.DEV) {
      console.debug(`[DEBUG] ${message}`, data);
    }
  }
};
```

## Contribución al Proyecto

### Workflow de Git

```bash
# Crear rama para nueva feature
git checkout -b feature/nueva-funcionalidad

# Hacer commits descriptivos
git commit -m "feat: agregar servicio de búsqueda web"
git commit -m "fix: corregir error de memoria en Whisper"
git commit -m "docs: actualizar guía de instalación"

# Push y crear PR
git push origin feature/nueva-funcionalidad
```

### Estándares de Código

**Python (Backend)**
- Usar type hints
- Seguir PEP 8
- Documentar funciones con docstrings
- Manejar excepciones apropiadamente

**TypeScript (Frontend)**
- Usar interfaces para props
- Componentes funcionales con hooks
- Manejar estados con useState/useEffect
- Tipado estricto habilitado

### Checklist antes de PR

- [ ] Tests pasan localmente
- [ ] Código formateado correctamente
- [ ] Documentación actualizada
- [ ] Variables de entorno documentadas
- [ ] Sin console.log en producción
- [ ] Manejo de errores implementado

## Herramientas de Desarrollo

### Recomendadas para Backend
- **IDE**: PyCharm, VS Code con Python extension
- **Linting**: flake8, black
- **Testing**: pytest
- **Debugging**: pdb, IDE debugger

### Recomendadas para Frontend
- **IDE**: VS Code con extensiones React/TypeScript
- **Linting**: ESLint, Prettier
- **Testing**: Vitest, React Testing Library
- **Debugging**: Browser DevTools, React DevTools

### Extensiones VS Code Útiles
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```