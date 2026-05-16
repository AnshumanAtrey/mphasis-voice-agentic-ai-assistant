from typing import Dict, Any
from .base_intent import BaseIntent
from config.constants import IntentType

class FallbackIntent(BaseIntent):
    """Handle unrecognized intents"""

    def can_handle(self, context: Dict[str, Any]) -> bool:
        intent = context.get('intent')
        return intent == IntentType.FALLBACK

    def handle(self, context: Dict[str, Any]) -> str:
        user_input = context.get('original', '')

        prompt = f"""
        The user said: "{user_input}"

        I'm not sure what they're asking for. Please provide a helpful response acknowledging their request
        and asking them to clarify or provide more information.
        Keep the response concise (1-2 sentences).
        """

        return self._get_llm_response(prompt, context)

    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        return f"User said: {user_input}"
