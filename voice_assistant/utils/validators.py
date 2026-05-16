import re
from typing import List, Tuple

class EntityValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        pattern = r'^(\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def is_valid_url(url: str) -> bool:
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # MM-DD-YYYY or DD-MM-YYYY
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',    # YYYY-MM-DD
        ]
        return any(re.match(p, date_str) for p in patterns)
