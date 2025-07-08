# tests/test_llm.py
import litellm

def main():
    """
    Función principal para enviar un prompt a un LLM local a través de LiteLLM.
    """
    api_base = "http://localhost:1234/v1"
    
    # --- LA LÍNEA CORREGIDA ---
    # Le decimos a LiteLLM que el servidor en 'api_base' es compatible con OpenAI.
    # El nombre después de la barra es el que se enviará en la petición,
    # aunque LM Studio lo ignorará y usará el modelo que tiene cargado.
    model_name = "openai/lmstudio-local-model"
    # -------------------------

    messages = [
        {
            "role": "system",
            "content": "Eres Jarv1s, un copiloto de IA personal. Tus respuestas son útiles, concisas y directas."
        },
        {
            "role": "user",
            "content": "¡Hola, mundo! Preséntate brevemente y confirma que has recibido este mensaje."
        }
    ]

    print("Conectando con el servidor LLM en LM Studio...")
    print(f"Endpoint: {api_base}")
    print(f"Modelo (indicando a LiteLLM que es un endpoint de OpenAI): {model_name}")
    print(f"Prompt del usuario: '{messages[-1]['content']}'")
    print("-" * 30)

    try:
        response = litellm.completion(
            model=model_name,
            messages=messages,
            api_base=api_base,
            api_key="not-required",
            temperature=0.7
        )

        print("\nRespuesta recibida del modelo:")
        print("-" * 30)
        
        response_text = response.choices[0].message.content.strip()
        
        print(response_text)
        
        print("-" * 30)
        print("\n¡Prueba del LLM completada con éxito!")

    except Exception as e:
        print(f"\n\n--- ¡ERROR! ---")
        print(f"No se pudo conectar con el modelo. Error: {e}")
        print("\nPosibles Causas:")
        print("1. ¿Está el servidor de LM Studio realmente en marcha?")
        print("2. ¿Hay un modelo completamente cargado en LM Studio?")
        print("3. Si el modelo es muy grande o es la primera carga, puede haber tardado demasiado en responder (timeout).")

if __name__ == "__main__":
    main()