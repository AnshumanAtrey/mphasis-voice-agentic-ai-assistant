from abc import ABC, abstractmethod
from typing import Optional
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseSpeechService(ABC):
    @abstractmethod
    def recognize(self, audio_data: bytes) -> Optional[str]:
        pass

class GoogleSpeechService(BaseSpeechService):
    def __init__(self, language: str = None):
        try:
            import speech_recognition as sr
            self.sr = sr
        except ImportError:
            logger.error("SpeechRecognition not installed. Install with: pip install SpeechRecognition")
            raise

        self.language = language or Settings.SPEECH_LANGUAGE
        self.recognizer = self.sr.Recognizer()

    def recognize(self, audio_data: bytes) -> Optional[str]:
        try:
            audio = self.sr.AudioData(audio_data, Settings.SAMPLE_RATE, 2)
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized: {text}")
            return text
        except self.sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except self.sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None

class MockSpeechService(BaseSpeechService):
    """Mock service for testing"""
    def recognize(self, audio_data: bytes) -> Optional[str]:
        return "Show today's tasks"

def create_speech_service(use_mock: bool = False, **kwargs) -> BaseSpeechService:
    if use_mock:
        return MockSpeechService()
    return GoogleSpeechService(**kwargs)
