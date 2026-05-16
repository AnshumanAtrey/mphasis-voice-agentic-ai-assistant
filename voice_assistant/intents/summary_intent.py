from typing import Dict, Any
from .base_intent import BaseIntent
from config.constants import IntentType

class SummaryIntent(BaseIntent):
    """Handle summarization intents"""

    def can_handle(self, context: Dict[str, Any]) -> bool:
        intent = context.get('intent')
        return intent == IntentType.SUMMARY

    def handle(self, context: Dict[str, Any]) -> str:
        user_input = context.get('original', '')

        prompt = f"""
        The user wants a summary. They said: "{user_input}"

        Please provide a helpful response offering to summarize their message or providing a summary.
        Keep the response concise (1-2 sentences).
        """

        return self._get_llm_response(prompt, context)

    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        return f"User wants to summarize: {user_input}"
