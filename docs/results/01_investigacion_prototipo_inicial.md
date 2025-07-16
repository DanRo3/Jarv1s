# Initial Research: Complete Loop Prototype Analysis

**Date:** July 8, 2025
**Prototype Version:** v0.1

## Executive Summary

The objective of this initial phase was to validate the core architecture of the **Jarv1s** project: a conversational AI system that operates **100% locally**, ensuring user privacy. The goal was to test the viability of integrating a complete Speech-to-Text (STT), Large Language Model (LLM), and Text-to-Speech (TTS) pipeline using a specific technology stack.

The result has been a **resounding success**. The functional prototype (`tests/test_full_loop.py`) has proven capable of maintaining coherent and natural conversation, validating the selected technologies and establishing a solid foundation for future development.

## Technology Stack and Prototype Architecture

The prototype was built following a modular data flow, where each component was strategically selected.

### 1. Voice Input (STT): OpenAI Whisper

-   **Technology Used:** `whisper`, OpenAI's speech recognition model.
-   **Specific Model:** `small`.
-   **Choice Justification:** Although the `base` model was initially tested, inaccuracies were observed. Migration to the `small` model offered a **dramatic qualitative leap in transcription accuracy**, even operating exclusively on **CPU**.
-   **Key Implementation:** To avoid hardware conflicts (observed between PyTorch initialization and the `sounddevice` audio driver), a **dynamic loading and unloading** strategy was adopted. The Whisper model is not kept in memory, but is loaded just before transcription and released immediately after, ensuring loop stability.

### 2. Central Processing (LLM): LM Studio + LiteLLM

-   **Technology Used:** A 1B parameter model served locally through **LM Studio**, with **LiteLLM** acting as a universal connector.
-   **Choice Justification:** This combination is the heart of Jarv1s philosophy.
    -   **LM Studio** abstracts the complexity of local model inference, providing an OpenAI API-compatible endpoint.
    -   **LiteLLM** allows our Python code to communicate with this endpoint in a standardized way, giving us the flexibility to change the LLM server in the future without rewriting the logic code.
-   **Key Implementation (Conversational Memory):** The greatest achievement in this layer was implementing a **conversation history**. The `think` function now maintains a list of exchanges between user and assistant. This complete history is sent to the LLM on each turn, allowing it to understand context and give coherent and relevant responses, rather than treating each question as an isolated event.

### 3. Voice Output (TTS): Piper TTS

-   **Technology Used:** `piper-tts`, a fast and high-quality voice synthesis engine.
-   **Specific Model:** `es_ES-sharvard-medium`.
-   **Choice Justification:** After discarding `pyttsx3` due to its low quality, **Piper** proved to be the ideal solution. It offers a natural and pleasant voice with extremely low synthesis latency, crucial for fluid and real-time conversation. Its CPU performance is excellent.

## Conversation Results Analysis

The complete conversation test yielded very positive results that validate the architectural decisions:

#### High Transcription Accuracy:
Even with colloquial phrases, Whisper's `small` model proved to be very robust.
> **You:** `A Very Difficult Math Formula`
>
> **You:** `That's interesting. Tell me a joke.`

#### Coherence Thanks to Memory:
The following excerpt perfectly demonstrates the success of the history implementation. Jarv1s remembers the previous turn and responds in context.
> **You:** `That's interesting. Tell me a joke.`
>
> **Jarv1s:** `Why do mathematicians prefer math to people? Because they're more stable! 😂`
>
> **You:** `That was really funny`
>
> **Jarv1s:** `I'm glad you liked it! Would you like to hear another one? 😊`

This behavior is impossible without conversation history, and its correct functioning is one of the greatest victories of this prototype.
