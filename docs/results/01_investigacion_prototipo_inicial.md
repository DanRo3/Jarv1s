# Investigación Inicial: Análisis del Prototipo de Bucle Completo

**Fecha:** 8 de Julio, 2025
**Versión del Prototipo:** v0.1

## Resumen Ejecutivo

El objetivo de esta fase inicial era validar la arquitectura central del proyecto **Jarv1s**: un sistema de IA conversacional que opera de forma **100% local**, garantizando la privacidad del usuario. Se buscaba probar la viabilidad de integrar un pipeline completo de Speech-to-Text (STT), Large Language Model (LLM) y Text-to-Speech (TTS) utilizando un stack tecnológico específico.

El resultado ha sido un **éxito rotundo**. El prototipo funcional (`tests/test_full_loop.py`) ha demostrado ser capaz de mantener una conversación coherente y natural, validando las tecnologías seleccionadas y estableciendo una base sólida para el desarrollo futuro.

## Stack Tecnológico y Arquitectura del Prototipo

El prototipo se construyó siguiendo un flujo de datos modular, donde cada componente fue seleccionado estratégicamente.

### 1. Entrada de Voz (STT): OpenAI Whisper

-   **Tecnología Utilizada:** `whisper`, el modelo de reconocimiento de voz de OpenAI.
-   **Modelo Específico:** `small`.
-   **Justificación de la Elección:** Aunque inicialmente se probó el modelo `base`, se observaron imprecisiones. La migración al modelo `small` ofreció un **salto cualitativo drástico en la precisión de la transcripción**, incluso operando exclusivamente en **CPU**.
-   **Implementación Clave:** Para evitar conflictos de hardware (observados entre la inicialización de PyTorch y el driver de audio `sounddevice`), se adoptó una estrategia de **carga y descarga dinámica**. El modelo Whisper no se mantiene en memoria, sino que se carga justo antes de la transcripción y se libera inmediatamente después, garantizando la estabilidad del bucle.

### 2. Procesamiento Central (LLM): LM Studio + LiteLLM

-   **Tecnología Utilizada:** Un modelo de 1B de parámetros servido localmente a través de **LM Studio**, con **LiteLLM** actuando como conector universal.
-   **Justificación de la Elección:** Esta combinación es el corazón de la filosofía de Jarv1s.
    -   **LM Studio** abstrae la complejidad de la inferencia de modelos locales, proporcionando un endpoint compatible con la API de OpenAI.
    -   **LiteLLM** permite que nuestro código Python se comunique con este endpoint de forma estandarizada, dándonos la flexibilidad de cambiar el servidor de LLM en el futuro sin reescribir el código de lógica.
-   **Implementación Clave (Memoria Conversacional):** El mayor logro en esta capa fue la implementación de un **historial de conversación**. La función `think` ahora mantiene una lista de los intercambios entre el usuario y el asistente. Este historial completo se envía al LLM en cada turno, lo que le permite entender el contexto y dar respuestas coherentes y relevantes, en lugar de tratar cada pregunta como un evento aislado.

### 3. Salida de Voz (TTS): Piper TTS

-   **Tecnología Utilizada:** `piper-tts`, un motor de síntesis de voz rápido y de alta calidad.
-   **Modelo Específico:** `es_ES-sharvard-medium`.
-   **Justificación de la Elección:** Después de descartar `pyttsx3` por su baja calidad, **Piper** demostró ser la solución ideal. Ofrece una voz natural y agradable con una latencia de síntesis extremadamente baja, crucial para una conversación fluida y en tiempo real. Su rendimiento en CPU es excelente.

## Análisis de Resultados de la Conversación

La prueba de conversación completa arrojó resultados muy positivos que validan las decisiones de arquitectura:

#### Alta Precisión en la Transcripción:
Incluso con frases coloquiales, el modelo `small` de Whisper demostró ser muy robusto.
> **Tú:** `Una Córmula de Matemáticas Bien Difícil`
>
> **Tú:** `Está interesante eso. Dime un chiste.`

#### Coherencia gracias a la Memoria:
El siguiente extracto demuestra perfectamente el éxito de la implementación del historial. Jarv1s recuerda el turno anterior y responde en contexto.
> **Tú:** `Está interesante eso. Dime un chiste.`
>
> **Jarv1s:** `¿Por qué los matemáticos prefieren las matemáticas a las personas? ¡Porque son más estables! 😂`
>
> **Tú:** `Ah me dio mucha gracia`
>
> **Jarv1s:** `¡Me alegro de que te haya gustado! ¿Quieres escuchar otro? 😊`

Este comportamiento es imposible sin un historial de conversación, y su correcto funcionamiento es una de las mayores victorias de este prototipo.
