from typing import Dict, List, Any
from collections import deque
from config.settings import Settings

class ConversationContext:
    """Manages conversation state and history"""

    def __init__(self, max_history: int = None):
        self.max_history = max_history or Settings.CONTEXT_WINDOW_SIZE
        self.history = deque(maxlen=self.max_history)
        self.metadata = {}

    def add_turn(self, user_input: str, ai_response: str, intent: str = None, entities: Dict = None):
        """Add a conversation turn to history"""
        self.history.append({
            'user': user_input,
            'response': ai_response,
            'intent': intent,
            'entities': entities or {},
        })

    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return list(self.history)

    def clear(self):
        """Clear conversation history"""
        self.history.clear()
        self.metadata.clear()

    def get_context_summary(self) -> str:
        """Get summary of recent context"""
        if not self.history:
            return "No previous context"

        summaries = [f"User: {turn['user']}\nAssistant: {turn['response']}" for turn in self.history]
        return "\n---\n".join(summaries)
