from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseIntent(ABC):
    """Base class for all intent handlers"""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    @abstractmethod
    def can_handle(self, context: Dict[str, Any]) -> bool:
        """Check if this intent can handle the context"""
        pass

    @abstractmethod
    def handle(self, context: Dict[str, Any]) -> str:
        """Handle the intent and return response"""
        pass

    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Build LLM prompt from context"""
        return f"User request: {user_input}"

    def _get_llm_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Get response from LLM"""
        if not self.llm_service:
            return "Unable to process request without LLM service"

        prompt = self._build_prompt(user_input, context)
        return self.llm_service.generate_response(prompt)
