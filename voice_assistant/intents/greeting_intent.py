from typing import Dict, Any
from .base_intent import BaseIntent
from config.constants import IntentType, Messages

class GreetingIntent(BaseIntent):
    """Handle greeting intents"""

    def can_handle(self, context: Dict[str, Any]) -> bool:
        intent = context.get('intent')
        return intent == IntentType.GREETING

    def handle(self, context: Dict[str, Any]) -> str:
        return Messages.GREETING_RESPONSE
