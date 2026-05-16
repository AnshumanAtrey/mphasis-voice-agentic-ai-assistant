import io
from abc import ABC, abstractmethod
from typing import Optional
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseAudioService(ABC):
    @abstractmethod
    def capture_audio(self, duration: float = 5.0) -> Optional[bytes]:
        pass

    @abstractmethod
    def play_audio(self, text: str, rate: int = 150) -> bool:
        pass

class PyAudioService(BaseAudioService):
    def __init__(self):
        try:
            import pyaudio
            import speech_recognition as sr
            self.pyaudio = pyaudio
            self.sr = sr
        except ImportError:
            logger.error("PyAudio not installed")
            raise

    def capture_audio(self, duration: float = 5.0) -> Optional[bytes]:
        try:
            recognizer = self.sr.Recognizer()
            with self.sr.Microphone(sample_rate=Settings.SAMPLE_RATE) as source:
                logger.info("Listening...")
                audio = recognizer.listen(source, timeout=duration)
                return audio.get_raw_data()
        except Exception as e:
            logger.error(f"Audio capture error: {e}")
            return None

    def play_audio(self, text: str, rate: int = 150) -> bool:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', Settings.TTS_VOLUME)
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            return False

class MockAudioService(BaseAudioService):
    """Mock service for testing"""
    def capture_audio(self, duration: float = 5.0) -> Optional[bytes]:
        return b"mock_audio_data"

    def play_audio(self, text: str, rate: int = 150) -> bool:
        logger.info(f"[TTS] {text}")
        return True

def create_audio_service(use_mock: bool = False, **kwargs) -> BaseAudioService:
    if use_mock:
        return MockAudioService()
    return PyAudioService(**kwargs)
