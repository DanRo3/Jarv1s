# src/services/llm_service.py

import litellm
import os

# Configuración del LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai/lmstudio-local-model")
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://localhost:1234/v1")

# Historial de conversación (simple, en memoria)
# NOTA: Esto no soporta múltiples usuarios, pero es perfecto para nuestro MVP.
conversation_history = [
    {"role": "system", "content": "Eres Jarv1s, un copiloto de IA personal. Tus respuestas son siempre concisas, amables y en español. Recuerdas la conversación anterior para dar respuestas coherentes."}
]

def get_llm_response(user_input: str) -> str:
    """
    Obtiene una respuesta del LLM manteniendo un historial de la conversación.

    Args:
        user_input (str): El texto transcrito del usuario.

    Returns:
        str: La respuesta de texto generada por el LLM.
    """
    global conversation_history
    print(f"Input para el LLM: {user_input}")

    # Añadimos el mensaje del usuario al historial
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        response = litellm.completion(
            model=LLM_PROVIDER,
            messages=conversation_history,
            api_base=LLM_API_BASE,
            api_key="not-required",
            temperature=0.7
        )
        response_text = response.choices[0].message.content.strip()
        
        # Añadimos la respuesta del asistente al historial
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Limitamos el historial para que no crezca indefinidamente
        if len(conversation_history) > 11: # System prompt + 5 pares de conversación
            conversation_history = [conversation_history[0]] + conversation_history[-10:]

    except Exception as e:
        print(f"Error de conexión con el LLM: {e}")
        response_text = "Lo siento, mi cerebro está desconectado en este momento."
        # No añadimos la respuesta de error al historial para no confundir al LLM.

    print(f"Respuesta del LLM: {response_text}")
    return response_text

def reset_conversation():
    """Resetea el historial de la conversación."""
    global conversation_history
    print("Reseteando el historial de la conversación.")
    conversation_history = [conversation_history[0]] # Mantiene solo el system prompt
    return {"status": "ok", "message": "Historial de conversación reseteado."}