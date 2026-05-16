import csv
from pathlib import Path
from typing import Dict, List, Any
from config.settings import Settings
from config.constants import CSVColumns
from utils.logger import setup_logger
from utils.helpers import TextHelper

logger = setup_logger(__name__)

class CSVHandler:
    """Handles CSV file operations for conversations"""

    def __init__(self, filepath: Path = None):
        self.filepath = filepath or (Settings.CSV_DIR / Settings.CSV_FILENAME)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_file()

    def _initialize_file(self):
        """Create CSV file with headers if it doesn't exist"""
        if not self.filepath.exists():
            headers = [
                CSVColumns.TIMESTAMP,
                CSVColumns.USER_INPUT,
                CSVColumns.INTENT,
                CSVColumns.ENTITIES,
                CSVColumns.AI_RESPONSE,
                CSVColumns.CONFIDENCE,
            ]
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
            logger.info(f"CSV file initialized: {self.filepath}")

    def save_conversation(self, data: Dict[str, Any]) -> bool:
        """Save a conversation record to CSV"""
        try:
            with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    CSVColumns.TIMESTAMP,
                    CSVColumns.USER_INPUT,
                    CSVColumns.INTENT,
                    CSVColumns.ENTITIES,
                    CSVColumns.AI_RESPONSE,
                    CSVColumns.CONFIDENCE,
                ])
                writer.writerow({
                    CSVColumns.TIMESTAMP: data.get(CSVColumns.TIMESTAMP, TextHelper.get_timestamp()),
                    CSVColumns.USER_INPUT: data.get(CSVColumns.USER_INPUT, ''),
                    CSVColumns.INTENT: str(data.get(CSVColumns.INTENT, '')),
                    CSVColumns.ENTITIES: str(data.get(CSVColumns.ENTITIES, {})),
                    CSVColumns.AI_RESPONSE: data.get(CSVColumns.AI_RESPONSE, ''),
                    CSVColumns.CONFIDENCE: data.get(CSVColumns.CONFIDENCE, 0),
                })
            logger.info("Conversation saved to CSV")
            return True
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False

    def read_conversations(self, limit: int = None) -> List[Dict[str, Any]]:
        """Read conversations from CSV"""
        try:
            conversations = []
            with open(self.filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break
                    conversations.append(row)
            logger.info(f"Read {len(conversations)} conversations from CSV")
            return conversations
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return []

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics from conversations"""
        conversations = self.read_conversations()
        if not conversations:
            return {'total': 0}

        intents = {}
        for conv in conversations:
            intent = conv.get(CSVColumns.INTENT, 'unknown')
            intents[intent] = intents.get(intent, 0) + 1

        return {
            'total': len(conversations),
            'intents': intents,
        }
