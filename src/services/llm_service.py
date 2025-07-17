"""
Large Language Model service using LiteLLM.
Handles conversation management with memory and robust error handling.
"""

from typing import List, Dict, Any, Optional
import litellm

from ..config.settings import get_settings
from ..utils.logger import get_llm_logger
from ..utils.exceptions import LLMException


class ConversationManager:
    """Manages conversation history and context."""
    
    def __init__(self, system_prompt: str, max_history_pairs: int = 5):
        self.system_prompt = system_prompt
        self.max_history_pairs = max_history_pairs
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the conversation history."""
        self.history.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str) -> None:
        """Add an assistant message to the conversation history."""
        self.history.append({"role": "assistant", "content": message})
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get the current conversation messages."""
        return self.history.copy()
    
    def trim_history(self) -> None:
        """Trim conversation history to maintain reasonable size."""
        # Keep system prompt + last N pairs of conversation
        max_messages = 1 + (self.max_history_pairs * 2)  # system + user/assistant pairs
        
        if len(self.history) > max_messages:
            # Keep system prompt and last N pairs
            self.history = [self.history[0]] + self.history[-(max_messages-1):]
    
    def reset(self) -> None:
        """Reset conversation to just the system prompt."""
        self.history = [{"role": "system", "content": self.system_prompt}]
    
    def get_conversation_length(self) -> int:
        """Get the number of message pairs (excluding system prompt)."""
        return (len(self.history) - 1) // 2


class LLMService:
    """Large Language Model service using LiteLLM."""
    
    def __init__(self):
        self.settings = get_settings().llm
        self.logger = get_llm_logger()
        
        # Initialize conversation manager
        system_prompt = (
            "You are Jarv1s, a personal AI copilot. Your responses are always "
            "concise, helpful, and friendly. You remember previous conversation "
            "context to provide coherent responses. Respond in the same language "
            "the user is using."
        )
        
        self.conversation = ConversationManager(
            system_prompt=system_prompt,
            max_history_pairs=self.settings.max_history_pairs
        )
        
        self.logger.info("LLM service initialized")
    
    def _make_llm_request(self, messages: List[Dict[str, str]]) -> str:
        """Make a request to the LLM service."""
        try:
            self.logger.debug(f"Making LLM request with {len(messages)} messages")
            
            response = litellm.completion(
                model=self.settings.provider,
                messages=messages,
                api_base=self.settings.api_base,
                api_key=self.settings.api_key,
                temperature=self.settings.temperature
            )
            
            response_text = response.choices[0].message.content.strip()
            self.logger.debug(f"LLM response received: {len(response_text)} characters")
            
            return response_text
            
        except Exception as e:
            error_msg = f"LLM request failed: {str(e)}"
            self.logger.error(error_msg)
            raise LLMException(error_msg, str(e))
    
    def get_response(self, user_input: str) -> str:
        """
        Get a response from the LLM for the given user input.
        
        Args:
            user_input: The user's message
            
        Returns:
            The LLM's response text
            
        Raises:
            LLMException: If the LLM request fails
        """
        if not user_input.strip():
            raise LLMException("Empty user input provided")
        
        self.logger.info(f"Processing user input: '{user_input}'")
        
        try:
            # Add user message to conversation
            self.conversation.add_user_message(user_input)
            
            # Get current messages for LLM
            messages = self.conversation.get_messages()
            
            # Make LLM request
            response_text = self._make_llm_request(messages)
            
            # Add assistant response to conversation
            self.conversation.add_assistant_message(response_text)
            
            # Trim history if needed
            self.conversation.trim_history()
            
            self.logger.info(f"LLM response generated: '{response_text}'")
            return response_text
            
        except LLMException:
            # Don't add error responses to conversation history
            raise
        except Exception as e:
            error_msg = f"Unexpected error in LLM service: {str(e)}"
            self.logger.error(error_msg)
            raise LLMException(error_msg, str(e))
    
    def reset_conversation(self) -> Dict[str, str]:
        """Reset the conversation history."""
        self.logger.info("Resetting conversation history")
        self.conversation.reset()
        return {
            "status": "ok", 
            "message": "Conversation history reset successfully"
        }
    
    def get_conversation_info(self) -> Dict[str, Any]:
        """Get information about the current conversation."""
        return {
            "message_count": len(self.conversation.history),
            "conversation_pairs": self.conversation.get_conversation_length(),
            "max_history_pairs": self.settings.max_history_pairs
        }
    
    def is_available(self) -> bool:
        """Check if the LLM service is available by making a test request."""
        try:
            test_messages = [
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say 'OK' if you can hear me."}
            ]
            response = self._make_llm_request(test_messages)
            return len(response.strip()) > 0
        except Exception:
            return False


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def get_llm_response(user_input: str) -> str:
    """
    Convenience function for getting LLM responses.
    Maintains backward compatibility with existing code.
    """
    service = get_llm_service()
    return service.get_response(user_input)


def reset_conversation() -> Dict[str, str]:
    """
    Convenience function for resetting conversation.
    Maintains backward compatibility with existing code.
    """
    service = get_llm_service()
    return service.reset_conversation()