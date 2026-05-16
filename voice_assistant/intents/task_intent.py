from typing import Dict, Any
from .base_intent import BaseIntent
from config.constants import IntentType

class TaskIntent(BaseIntent):
    """Handle task-related intents"""

    def can_handle(self, context: Dict[str, Any]) -> bool:
        intent = context.get('intent')
        return intent == IntentType.TASK_SHOW

    def handle(self, context: Dict[str, Any]) -> str:
        user_input = context.get('original', '')

        prompt = f"""
        The user asked about their tasks. They said: "{user_input}"

        Please provide a helpful response about their tasks. You can:
        - Suggest creating a task list if they don't have one
        - Offer to help prioritize tasks
        - Ask what tasks they want to work on

        Keep the response concise (1-2 sentences).
        """

        return self._get_llm_response(prompt, context)

    def _build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        return f"User is asking about tasks: {user_input}"
