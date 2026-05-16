import re
from typing import List
from datetime import datetime

class TextHelper:
    @staticmethod
    def clean_text(text: str) -> str:
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\-\@]', '', text)
        return text.lower()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return text.split()

    @staticmethod
    def remove_punctuation(text: str) -> str:
        return re.sub(r'[^\w\s]', '', text)

    @staticmethod
    def get_timestamp() -> str:
        return datetime.now().isoformat()

    @staticmethod
    def format_timestamp(ts: str) -> str:
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ts
