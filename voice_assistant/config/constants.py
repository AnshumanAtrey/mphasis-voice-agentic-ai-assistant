from enum import Enum

class IntentType(str, Enum):
    GREETING = "greeting"
    TASK_SHOW = "task_show"
    NOTE_SAVE = "note_save"
    SUMMARY = "summary"
    SEARCH = "search"
    COMMAND = "command"
    FALLBACK = "fallback"

class EntityType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    URL = "url"
    PERSON = "person"
    LOCATION = "location"

class CSVColumns:
    TIMESTAMP = "timestamp"
    USER_INPUT = "user_input"
    INTENT = "intent"
    ENTITIES = "entities"
    AI_RESPONSE = "ai_response"
    CONFIDENCE = "confidence"

class Messages:
    GREETING_RESPONSE = "Hello! How can I help you today?"
    ERROR_AUDIO = "Sorry, I couldn't capture audio. Please try again."
    ERROR_PROCESS = "I encountered an error processing your request."
    ERROR_TTS = "I couldn't generate a voice response."
    LISTENING = "I'm listening..."
    PROCESSING = "Processing your request..."
