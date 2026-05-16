from typing import Dict, Any, Optional
from .csv_handler import CSVHandler
from config.constants import CSVColumns
from utils.helpers import TextHelper
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ConversationLogger:
    """High-level interface for logging conversations"""

    def __init__(self, csv_handler: CSVHandler = None):
        self.csv_handler = csv_handler or CSVHandler()

    def log_conversation(
        self,
        user_input: str,
        ai_response: str,
        intent: Optional[str] = None,
        entities: Optional[Dict] = None,
        confidence: float = 0.0,
    ) -> bool:
        """Log a complete conversation exchange"""

        data = {
            CSVColumns.TIMESTAMP: TextHelper.get_timestamp(),
            CSVColumns.USER_INPUT: user_input,
            CSVColumns.INTENT: intent or 'unknown',
            CSVColumns.ENTITIES: entities or {},
            CSVColumns.AI_RESPONSE: ai_response,
            CSVColumns.CONFIDENCE: confidence,
        }

        return self.csv_handler.save_conversation(data)

    def get_conversation_history(self, limit: int = 10) -> list:
        """Get recent conversations"""
        return self.csv_handler.read_conversations(limit)

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return self.csv_handler.get_summary()
