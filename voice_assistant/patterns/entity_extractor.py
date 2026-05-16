from typing import Dict, List, Any
from .regex_library import RegexLibrary
from config.constants import EntityType
from utils.validators import EntityValidator

class EntityExtractor:
    def __init__(self):
        self.regex_lib = RegexLibrary()
        self.validator = EntityValidator()

    def extract_all_entities(self, text: str) -> Dict[str, List[str]]:
        return {
            EntityType.EMAIL: self.extract_emails(text),
            EntityType.PHONE: self.extract_phones(text),
            EntityType.DATE: self.extract_dates(text),
            EntityType.URL: self.extract_urls(text),
        }

    def extract_emails(self, text: str) -> List[str]:
        emails = self.regex_lib.find_emails(text)
        return [e for e in emails if self.validator.is_valid_email(e)]

    def extract_phones(self, text: str) -> List[str]:
        phones = self.regex_lib.find_phones(text)
        return [p for p in phones if self.validator.is_valid_phone(p)]

    def extract_dates(self, text: str) -> List[str]:
        dates = self.regex_lib.find_dates(text)
        return [d for d in dates if self.validator.is_valid_date(d)]

    def extract_urls(self, text: str) -> List[str]:
        urls = self.regex_lib.find_urls(text)
        return [u for u in urls if self.validator.is_valid_url(u)]

    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        return {
            'task_keywords': self.regex_lib.TASK_KEYWORDS.findall(text),
            'note_keywords': self.regex_lib.NOTE_KEYWORDS.findall(text),
            'time_keywords': self.regex_lib.TIME_KEYWORDS.findall(text),
        }
