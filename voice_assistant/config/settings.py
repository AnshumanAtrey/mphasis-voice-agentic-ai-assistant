import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    CSV_DIR = DATA_DIR / "conversations"

    # Create directories if they don't exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    CSV_DIR.mkdir(exist_ok=True)

    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = 'wav'

    # API keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # LLM settings
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-flash')  # Latest Gemini model
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.7))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', 500))

    # Speech recognition
    SPEECH_ENGINE = os.getenv('SPEECH_ENGINE', 'google')  # 'google' or 'whisper'
    SPEECH_LANGUAGE = os.getenv('SPEECH_LANGUAGE', 'en-US')

    # Text-to-speech
    TTS_ENGINE = os.getenv('TTS_ENGINE', 'pyttsx3')  # 'pyttsx3' or 'gtts'
    TTS_RATE = int(os.getenv('TTS_RATE', 150))
    TTS_VOLUME = float(os.getenv('TTS_VOLUME', 1.0))

    # Storage
    CSV_FILENAME = 'conversations.csv'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Agent settings
    CONTEXT_WINDOW_SIZE = int(os.getenv('CONTEXT_WINDOW_SIZE', 5))
    INTENT_CONFIDENCE_THRESHOLD = float(os.getenv('INTENT_CONFIDENCE_THRESHOLD', 0.6))
