"""Tests for pattern matching and entity extraction"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from patterns.regex_library import RegexLibrary
from patterns.entity_extractor import EntityExtractor
from patterns.intent_classifier import IntentClassifier

def test_regex_emails():
    emails = RegexLibrary.find_emails("Contact me at john@example.com or jane@test.org")
    assert "john@example.com" in emails
    assert "jane@test.org" in emails

def test_regex_phones():
    phones = RegexLibrary.find_phones("Call me at 555-123-4567 or +1-555-123-4567")
    assert len(phones) > 0

def test_greetings():
    assert RegexLibrary.is_greeting("Hello there")
    assert RegexLibrary.is_greeting("Hi, how are you?")
    assert not RegexLibrary.is_greeting("Show me my tasks")

def test_entity_extraction():
    extractor = EntityExtractor()
    text = "Email me at test@example.com or call 555-123-4567"
    entities = extractor.extract_all_entities(text)
    assert len(entities.get('email', [])) > 0

def test_intent_classification():
    classifier = IntentClassifier()

    greeting_intent, conf = classifier.classify("Hello")
    assert greeting_intent.value == 'greeting'

    task_intent, conf = classifier.classify("Show today's tasks")
    assert task_intent.value == 'task_show'

    save_intent, conf = classifier.classify("Save this note")
    assert save_intent.value == 'note_save'

if __name__ == '__main__':
    test_regex_emails()
    test_regex_phones()
    test_greetings()
    test_entity_extraction()
    test_intent_classification()
    print("✅ All pattern tests passed!")
