# Jarv1s: Your Personal AI Co-pilot

[![Status](https://img.shields.io/badge/status-Functional%20Prototype-green.svg)](https://github.com/danrodev/Jarv1s)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

## Unleash Your Potential with a Truly Personal AI

**Jarv1s** isn't just another assistant; it's a powerful, privacy-focused AI co-pilot designed to run entirely on your own machine. Built for ultimate control and customization, Jarv1s integrates seamlessly into your digital life, helping you organize, research, and create like never before. **Forget the cloud—your data, your rules, your AI.**

## Project Status: Functional Prototype

The project has successfully reached its first major milestone: a **functional full-stack prototype**. The current system enables fluid and coherent voice conversations through a web interface, validating the core architecture and technology stack. The foundation is built and robust.

## Core Features (Vision)

This is the long-term vision for Jarv1s capabilities:

*   🗣️ **Fluid Voice Conversation:** Interact naturally with Jarv1s using your voice.
*   🔒 **100% Local & Private:** Your conversations and data never leave your computer.
*   🚀 **Productivity Maximizer:** Manage your calendar, organize notes, and streamline daily tasks.
*   🧠 **Intelligent Research Assistant:** Summarize complex PDF documents and scour the web for information.
*   🛠️ **Hyper-Modular Architecture:** Built on Google's Agent Development Kit for straightforward extensibility.

## Architecture of the Functional Prototype

The current system operates with a decoupled Client-Server architecture. The Frontend (React) captures audio and renders responses, while the Backend (Python/FastAPI) handles all AI processing.

```mermaid
graph TD
    subgraph "Frontend React @ localhost:5173"
        A[UI Orb: Push-to-Talk] -->|1. Records Audio ((WEBM))| B((Sends via POST Request));
        B --> C{Backend API};
        D[Receives JSON Response] --> E((Decodes Base64 & Plays Audio));
    end

    subgraph "Backend Python/FastAPI @ localhost:8000"
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

The technology stack has been carefully selected to meet performance and privacy objectives.

#### Backend
*   **Language:** Python 3.10+
*   **API Framework:** FastAPI with Uvicorn
*   **Speech-to-Text (STT):** OpenAI Whisper (`small` model running on CPU)
*   **Text-to-Speech (TTS):** Piper TTS (High-quality voice with low latency)
*   **Universal LLM Connector:** LiteLLM
*   **Audio Processing:** FFmpeg (directly invoked for robust conversion)

#### Frontend
*   **Framework:** React (with Vite and TypeScript)
*   **Animation:** Framer Motion
*   **HTTP Client:** Axios
*   **Audio Recording:** Native browser `MediaRecorder` API

#### AI Inference
*   **Local LLM Server:** LM Studio

---

## Getting Started: Launch the Prototype!

Follow these steps to run the complete Jarv1s ecosystem on your machine.

### 1. Prerequisites
Make sure you have installed:
-   **Python 3.10+** and `pip`
-   **Node.js and `npm`**
-   **FFmpeg:** `sudo apt install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)
-   **LM Studio:** Downloaded, installed, and with a language model (e.g., `Phi-3-mini-4k-instruct-q4.gguf`) ready to use

### 2. Backend Setup

```bash
# 1. Navigate to the project folder
cd jarv1s # Or whatever name you gave it

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -e .

# 4. Configure your environment variables
cp .env.example .env

# 5. Start LM Studio server and make sure it's listening

# 6. Launch the Jarv1s backend
uvicorn src.main:app --reload
```

### 3. Frontend Setup

Open a **new terminal**.

```bash
# 1. Navigate to the frontend folder
cd frontend

# 2. Install Node.js dependencies
npm install

# 3. Launch the development server
npm run dev
```

### 4. Start Talking!

Open your browser and go to the address provided by Vite (usually `http://localhost:5173`). Hold down the spacebar and start your first conversation with Jarv1s!

---

## Complete Documentation

For detailed information about the project, check the documentation in the `docs/` folder:

- **[Project Overview](docs/project_overview.md)**: Philosophy, capabilities, and use cases
- **[Technical Details](docs/technical_details.md)**: Deep architecture and system components
- **[Development Guide](docs/development_guide.md)**: Complete setup and development workflow
- **[API Reference](docs/api_reference.md)**: Complete endpoint documentation
- **[Roadmap](docs/roadmap.md)**: Detailed project roadmap
- **[Setup Guide](docs/setup_guide.md)**: Step-by-step installation and verification
- **[Architecture](docs/architecture.md)**: System diagram and flow
- **[Git Workflow](docs/git_workflow.md)**: Branching strategy and development process

## Next Steps

The complete roadmap is available at [docs/roadmap.md](docs/roadmap.md). Key milestones include:

- **Q1 2025**: Migration to Google Agent Development Kit (ADK)
- **Q2 2025**: Essential tools (web search, PDF processing)
- **Q3 2025**: Performance optimizations and UX improvements
- **Q4 2025**: Extensible plugin system

---

### A Note on the Project's Purpose

**Jarv1s** is an ambitious open-source project born from a passion for learning. Its primary goal is to serve as a practical testbed to explore, understand, and deepen knowledge in the fascinating fields of **agentic AI systems**, **multi-agent construction**, and **Natural Language Processing (NLP)**. Every feature and challenge is a stepping stone on this educational journey.