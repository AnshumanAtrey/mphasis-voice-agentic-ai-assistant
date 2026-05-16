import re
from typing import Dict, List, Pattern

class RegexLibrary:
    # Email pattern
    EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Phone patterns
    PHONE_US = re.compile(r'(\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}\b')
    PHONE_INTERNATIONAL = re.compile(r'\+[0-9]{1,3}[-.\s]?[0-9]{1,14}\b')

    # Date patterns
    DATE_DMY = re.compile(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b')
    DATE_YMD = re.compile(r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b')
    DATE_MONTH_DAY = re.compile(r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}\b', re.IGNORECASE)

    # URL pattern
    URL = re.compile(r'https?://[^\s]+')

    # Greetings
    GREETINGS = re.compile(
        r'\b(hello|hi|hey|greetings|good\s+(morning|afternoon|evening)|welcome)\b',
        re.IGNORECASE
    )

    # Commands
    COMMAND_SHOW = re.compile(r'\b(show|display|list|get)\s+', re.IGNORECASE)
    COMMAND_SAVE = re.compile(r'\b(save|store|write|note)\s+', re.IGNORECASE)
    COMMAND_SUMMARIZE = re.compile(r'\b(summarize|summary|brief|condense)\s+', re.IGNORECASE)
    COMMAND_SEARCH = re.compile(r'\b(search|find|look\s+for|find\s+me)\b', re.IGNORECASE)

    # Keywords
    TASK_KEYWORDS = re.compile(r'\b(tasks?|todo|to-do|remind|schedule)\b', re.IGNORECASE)
    NOTE_KEYWORDS = re.compile(r'\b(notes?|memo|reminder|message)\b', re.IGNORECASE)
    TIME_KEYWORDS = re.compile(r'\b(today|tomorrow|today\'s|this|next|now)\b', re.IGNORECASE)

    @classmethod
    def find_emails(cls, text: str) -> List[str]:
        return cls.EMAIL.findall(text)

    @classmethod
    def find_phones(cls, text: str) -> List[str]:
        phones = cls.PHONE_US.findall(text)
        phones.extend(cls.PHONE_INTERNATIONAL.findall(text))
        return list(set(phones))

    @classmethod
    def find_dates(cls, text: str) -> List[str]:
        dates = cls.DATE_DMY.findall(text)
        dates.extend(cls.DATE_YMD.findall(text))
        dates.extend(cls.DATE_MONTH_DAY.findall(text))
        return list(set(dates))

    @classmethod
    def find_urls(cls, text: str) -> List[str]:
        return cls.URL.findall(text)

    @classmethod
    def is_greeting(cls, text: str) -> bool:
        return cls.GREETINGS.search(text) is not None

    @classmethod
    def detect_command_type(cls, text: str) -> str:
        if cls.COMMAND_SHOW.search(text):
            return 'show'
        elif cls.COMMAND_SAVE.search(text):
            return 'save'
        elif cls.COMMAND_SUMMARIZE.search(text):
            return 'summarize'
        elif cls.COMMAND_SEARCH.search(text):
            return 'search'
        return 'none'
