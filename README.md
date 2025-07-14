# Jarv1s: Your Personal AI Co-pilot

[![Status](https://img.shields.io/badge/status-Functional%20Prototype-green.svg)](https://github.com/danrodev/Jarv1s)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

## Unleash Your Potential with a Truly Personal AI

**Jarv1s** isn't just another assistant; it's a powerful, privacy-focused AI co-pilot designed to run entirely on your own machine. Built for ultimate control and customization, Jarv1s integrates seamlessly into your digital life, helping you organize, research, and create like never before. **Forget the cloud—your data, your rules, your AI.**

## Project Status: Functional Prototype

El proyecto ha alcanzado con éxito su primer gran hito: un **prototipo full-stack funcional**. El sistema actual permite mantener una conversación de voz fluida y coherente a través de una interfaz web, validando la arquitectura central y el stack tecnológico. La base está construida y es robusta.

## Core Features (Vision)

Esta es la visión a largo plazo para las capacidades de Jarv1s:

*   🗣️ **Fluid Voice Conversation:** Interact naturally with Jarv1s using your voice.
*   🔒 **100% Local & Private:** Your conversations and data never leave your computer.
*   🚀 **Productivity Maximizer:** Manage your calendar, organize notes, and streamline daily tasks.
*   🧠 **Intelligent Research Assistant:** Summarize complex PDF documents and scour the web for information.
*   🛠️ **Hyper-Modular Architecture:** Built on Google's Agent Development Kit for straightforward extensibility.

## Architecture of the Functional Prototype

El sistema actual opera con una arquitectura desacoplada Cliente-Servidor. El Frontend (React) captura el audio y renderiza la respuesta, mientras que el Backend (Python/FastAPI) realiza todo el procesamiento de IA.

```mermaid
graph TD
    subgraph Frontend (React @ localhost:5173)
        A[UI Orb: Push-to-Talk] -->|1. Records Audio (WEBM)| B(Sends via POST Request);
        B --> C{Backend API};
        D[Receives JSON Response] --> E(Decodes Base64 & Plays Audio);
    end

    subgraph Backend (Python @ localhost:8000)
        C --> F[Endpoint /interact];
        F --> G[STT Service];
        G --Converts WEBM to WAV w/ FFmpeg--> H((Whisper Model));
        H -->|Transcribed Text| I[LLM Service];
        I -->|Prompt w/ History| J{LM Studio};
        J -->|LLM Response| I;
        I -->|Response Text| K[TTS Service];
        K --Generates PCM Audio--> L((Piper TTS Model));
        L --Packages into valid WAV--> K;
        K -->|JSON with Base64 Audio| F;
        F --> D;
    end

    style A fill:#87CEEB,stroke:#333,stroke-width:2px
    style E fill:#87CEEB,stroke:#333,stroke-width:2px
    style F fill:#90EE90,stroke:#333,stroke-width:2px
    style J fill:#FFD700,stroke:#333,stroke-width:2px
```

## The Tech Stack Powering Jarv1s

El stack tecnológico ha sido cuidadosamente seleccionado para cumplir con los objetivos de rendimiento y privacidad.

#### Backend
*   **Lenguaje:** Python 3.10+
*   **Framework de API:** FastAPI con Uvicorn
*   **Speech-to-Text (STT):** OpenAI Whisper (Modelo `small` ejecutándose en CPU)
*   **Text-to-Speech (TTS):** Piper TTS (Voz de alta calidad y baja latencia)
*   **Conector Universal de LLM:** LiteLLM
*   **Manipulación de Audio:** FFmpeg (invocado directamente para una conversión robusta)

#### Frontend
*   **Framework:** React (con Vite y TypeScript)
*   **Animación:** Framer Motion
*   **Cliente HTTP:** Axios
*   **Grabación de Audio:** API nativa `MediaRecorder` del navegador.

#### Inferencia de IA
*   **Servidor LLM Local:** LM Studio

---

## Getting Started: ¡Poniendo en Marcha el Prototipo!

Sigue estos pasos para ejecutar el ecosistema completo de Jarv1s en tu máquina.

### 1. Prerrequisitos
Asegúrate de tener instalado:
-   **Python 3.10+** y `pip`.
-   **Node.js y `npm`**.
-   **FFmpeg:** `sudo apt install ffmpeg` (Linux) o `brew install ffmpeg` (macOS).
-   **LM Studio:** Descargado, instalado y con un modelo de lenguaje (ej. `Phi-3-mini-4k-instruct-q4.gguf`) listo para usar.

### 2. Configuración del Backend

```bash
# 1. Navega a la carpeta del backend
cd local-agent-suite # O el nombre que le hayas dado

# 2. Crea y activa un entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instala las dependencias de Python
pip install -r requirements.txt # (Asegúrate de crear este archivo con 'pip freeze')
# O instálalas manualmente: pip install fastapi uvicorn python-multipart python-dotenv openai-whisper torch piper-tts pydub litellm

# 4. Configura tus variables de entorno
cp .env.example .env

# 5. Inicia el servidor de LM Studio y asegúrate de que esté escuchando.

# 6. Lanza el backend de Jarv1s
uvicorn src.main:app --reload
```

### 3. Configuración del Frontend

Abre una **nueva terminal**.

```bash
# 1. Navega a la carpeta del frontend
cd jarv1s-frontend # O el nombre que le hayas dado

# 2. Instala las dependencias de Node.js
npm install

# 3. Lanza el servidor de desarrollo
npm run dev
```

### 4. ¡A Conversar!

Abre tu navegador y ve a la dirección que te proporcionó Vite (normalmente `http://localhost:5173`). ¡Mantén presionada la barra espaciadora y comienza tu primera conversación con Jarv1s!

---

## Hoja de Ruta (Roadmap)

Este prototipo funcional es solo el comienzo. Los próximos pasos se centrarán en construir sobre esta sólida base:
-   [ ] **Integrar Google Agent Development Kit (ADK):** Reemplazar la lógica simple del LLM por un verdadero framework de agente para una orquestación avanzada de herramientas.
-   [ ] **Desarrollar Herramientas (Tools):** Implementar las habilidades clave del MVP:
    -   [ ] Búsqueda en la web.
    -   [ ] Lector y resumidor de documentos PDF.
-   [ ] **Optimizar el STT:** Investigar la implementación de `whisper.cpp` para una transcripción aún más rápida en CPU.
-   [ ] **Mejorar la UX:** Implementar la visualización de los "pensamientos" o herramientas que Jarv1s está usando en tiempo real en la interfaz.

---

### A Note on the Project's Purpose

**Jarv1s** is an ambitious open-source project born from a passion for learning. Its primary goal is to serve as a practical testbed to explore, understand, and deepen knowledge in the fascinating fields of **agentic AI systems**, **multi-agent construction**, and **Natural Language Processing (NLP)**. Every feature and challenge is a stepping stone on this educational journey.