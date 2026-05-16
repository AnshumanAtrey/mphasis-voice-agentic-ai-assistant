from typing import Dict, Any
from .base_intent import BaseIntent
from config.constants import IntentType

class NoteIntent(BaseIntent):
    """Handle note-taking intents"""

    def can_handle(self, context: Dict[str, Any]) -> bool:
        intent = context.get('intent')
        return intent == IntentType.NOTE_SAVE

    def handle(self, context: Dict[str, Any]) -> str:
        user_input = context.get('original', '')

        prompt = f"""
        The user wants to save a note. They said: "{user_input}"

        Please provide a helpful response confirming the note is being saved and ask clarifying questions if needed.
        Keep the response concise (1-2 sentences).
        """

        return self._get_llm_response(prompt, context)

    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        return f"User wants to save a note: {user_input}"
