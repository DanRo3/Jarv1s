# Jarv1s: System Architecture

The system follows a modular and decoupled data flow:

1.  **Input (Voice):** The user speaks. `Whisper` transcribes the audio to text.
2.  **Agent Processing:** The text is sent to the **Agent Development Kit (ADK)**, which acts as the central orchestrator for **Jarv1s**.
3.  **LLM Logic:**
    * The ADK determines if it needs to use a tool or consult the LLM.
    * To consult the LLM, the ADK makes an OpenAI-formatted call.
    * **LiteLLM** intercepts this call, translates it, and redirects it to the local **LM Studio** server endpoint.
4.  **LLM Response:** LM Studio processes the request with the loaded model and returns the response via LiteLLM to the ADK.
5.  **Tool Actuators:** If the LLM decides to use a tool (e.g., read the calendar), the ADK executes the corresponding Python code.
6.  **Output (Voice):** The final text response from the agent is sent to `pyttsx3`, which converts it to audio and plays it back to the user.