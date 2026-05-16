from typing import Tuple
from .regex_library import RegexLibrary
from config.constants import IntentType

class IntentClassifier:
    def __init__(self):
        self.regex_lib = RegexLibrary()

    def classify(self, text: str) -> Tuple[IntentType, float]:
        """Classify intent and return intent type with confidence score."""

        if self.regex_lib.is_greeting(text):
            return IntentType.GREETING, 0.95

        # Check for task keywords first (includes "today's tasks")
        if self._contains_task_keywords(text):
            if self.regex_lib.COMMAND_SHOW.search(text):
                return IntentType.TASK_SHOW, 0.85

        command_type = self.regex_lib.detect_command_type(text)

        if command_type == 'show':
            return IntentType.COMMAND, 0.75

        if command_type == 'save':
            return IntentType.NOTE_SAVE, 0.85

        if command_type == 'summarize':
            return IntentType.SUMMARY, 0.85

        if command_type == 'search':
            return IntentType.SEARCH, 0.80

        return IntentType.FALLBACK, 0.5

    def _contains_task_keywords(self, text: str) -> bool:
        return self.regex_lib.TASK_KEYWORDS.search(text) is not None
