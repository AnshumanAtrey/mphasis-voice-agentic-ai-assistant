from typing import Optional, Dict, Any
from .base import BasePipelineStage
from services.audio_service import BaseAudioService
from services.speech_service import BaseSpeechService
from services.llm_service import BaseLLMService
from patterns.entity_extractor import EntityExtractor
from patterns.intent_classifier import IntentClassifier
from utils.logger import setup_logger
from utils.helpers import TextHelper
from config.constants import Messages
from core.error_handler import (
    InputValidator, ErrorHandler, FallbackResponseGenerator,
    EdgeCaseHandler, ErrorSeverity, ProcessingError, ServiceError
)

logger = setup_logger(__name__)

class VoiceInputStage(BasePipelineStage):
    """Capture voice input from microphone"""

    def __init__(self, audio_service: BaseAudioService):
        self.audio_service = audio_service
        self.error_handler = ErrorHandler()

    def process(self, duration: float = 5.0) -> Optional[bytes]:
        try:
            # Validate duration
            validation = InputValidator.validate_audio_duration(duration)
            if not validation['valid']:
                logger.warning(f"Invalid duration: {validation['errors']}")
                return None

            validated_duration = validation.get('duration', duration)
            logger.info(f"Recording audio for {validated_duration} seconds...")
            audio_data = self.audio_service.capture_audio(validated_duration)
            if audio_data:
                logger.info(f"Audio captured: {len(audio_data)} bytes")
            return audio_data
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.MEDIUM, "VoiceInputStage")
            return None

class SpeechToTextStage(BasePipelineStage):
    """Convert audio to text"""

    def __init__(self, speech_service: BaseSpeechService):
        self.speech_service = speech_service
        self.error_handler = ErrorHandler()

    def process(self, audio_data: Optional[bytes]) -> Optional[str]:
        try:
            if not audio_data:
                logger.warning("No audio data provided")
                self.error_handler.log_error(
                    ProcessingError("No audio data"),
                    ErrorSeverity.MEDIUM,
                    "SpeechToTextStage"
                )
                return None

            if not isinstance(audio_data, bytes):
                logger.error(f"Invalid audio data type: {type(audio_data)}")
                return None

            text = self.speech_service.recognize(audio_data)
            if text:
                logger.info(f"Transcribed: {text}")
            else:
                logger.warning("Speech recognition returned empty result")
            return text
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.MEDIUM, "SpeechToTextStage")
            return None

class TextProcessorStage(BasePipelineStage):
    """Process and clean text, extract entities"""

    def __init__(self, entity_extractor: EntityExtractor = None):
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.text_helper = TextHelper()
        self.error_handler = ErrorHandler()

    def process(self, text: Optional[str]) -> Optional[Dict[str, Any]]:
        try:
            if not text:
                return None

            # Validate input text
            validation = InputValidator.validate_text_input(text)
            if not validation['valid']:
                logger.warning(f"Text validation errors: {validation['errors']}")
                self.error_handler.log_error(
                    ProcessingError(f"Text validation: {validation['errors']}"),
                    ErrorSeverity.LOW,
                    "TextProcessorStage"
                )
                return None

            cleaned_text = self.text_helper.clean_text(validation['cleaned'])
            entities = self.entity_extractor.extract_all_entities(cleaned_text)
            keywords = self.entity_extractor.extract_keywords(cleaned_text)

            # Handle null entities
            entities = entities or {}

            return {
                'original': text,
                'cleaned': cleaned_text,
                'entities': entities,
                'keywords': keywords,
            }
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.MEDIUM, "TextProcessorStage")
            return None

class IntentClassificationStage(BasePipelineStage):
    """Classify user intent"""

    def __init__(self, intent_classifier: IntentClassifier = None):
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.error_handler = ErrorHandler()

    def process(self, processed_text: Optional[Dict]) -> Optional[Dict[str, Any]]:
        try:
            if not processed_text:
                return None

            text = processed_text.get('cleaned')
            if not text:
                logger.warning("No cleaned text for intent classification")
                return None

            intent_type, confidence = self.intent_classifier.classify(text)

            # Validate confidence score
            conf_validation = InputValidator.validate_confidence_score(confidence)
            if not conf_validation['valid']:
                logger.warning(f"Invalid confidence: {conf_validation['errors']}")
                confidence = conf_validation.get('score', 0.5)

            # Validate intent
            if intent_type is None:
                logger.warning("Intent classification returned None")
                return EdgeCaseHandler.handle_none_intent(text)

            intent_validation = InputValidator.validate_intent(intent_type)
            if not intent_validation['valid']:
                logger.warning(f"Invalid intent: {intent_validation['errors']}")
                return None

            return {
                **processed_text,
                'intent': intent_type,
                'confidence': confidence,
            }
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.MEDIUM, "IntentClassificationStage")
            return None

class LLMGeneratorStage(BasePipelineStage):
    """Generate response using LLM"""

    def __init__(self, llm_service: BaseLLMService):
        self.llm_service = llm_service
        self.error_handler = ErrorHandler()

    def process(self, processed_data: Optional[Dict[str, Any]]) -> Optional[str]:
        try:
            if not processed_data:
                return FallbackResponseGenerator.generate_generic_recovery_response()

            original_text = processed_data.get('original')
            intent = processed_data.get('intent')

            if not original_text:
                logger.warning("No original text for LLM generation")
                return FallbackResponseGenerator.generate_generic_recovery_response()

            if not intent:
                logger.warning("No intent for LLM generation")
                return FallbackResponseGenerator.generate_processing_error_response('intent')

            prompt = self._build_prompt(original_text, intent, processed_data)
            response = self.llm_service.generate_response(prompt)

            # Handle empty response
            if not response:
                logger.warning("LLM returned empty response")
                return FallbackResponseGenerator.generate_processing_error_response('service')

            # Validate response format
            if not isinstance(response, str):
                logger.error(f"Invalid response type: {type(response)}")
                return FallbackResponseGenerator.generate_generic_recovery_response()

            logger.info(f"LLM Response: {response}")
            return response
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.HIGH, "LLMGeneratorStage")
            return FallbackResponseGenerator.generate_processing_error_response('service')

    def _build_prompt(self, text: str, intent: Any, processed_data: Dict) -> str:
        entities = processed_data.get('entities', {}) or {}
        entities_str = ', '.join(
            f"{k}: {v}" for k, v in entities.items() if v
        ) or "None"

        intent_str = getattr(intent, 'value', str(intent))

        return f"""
        User Intent: {intent_str}
        User Input: {text}
        Extracted Entities: {entities_str}

        Please provide a helpful and concise response to the user's request. Keep the response brief (1-2 sentences).
        """

class TextToSpeechStage(BasePipelineStage):
    """Convert text response to speech"""

    def __init__(self, audio_service: BaseAudioService):
        self.audio_service = audio_service
        self.error_handler = ErrorHandler()

    def process(self, text: Optional[str]) -> bool:
        try:
            if not text:
                logger.warning("No text to convert to speech")
                return False

            if not isinstance(text, str):
                logger.error(f"Invalid text type: {type(text)}")
                return False

            success = self.audio_service.play_audio(text)
            if success:
                logger.info("Audio played successfully")
            else:
                logger.warning("Failed to play audio")
            return success
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.MEDIUM, "TextToSpeechStage")
            return False

class PipelineExecutor:
    """Orchestrates the complete pipeline with comprehensive error handling"""

    def __init__(
        self,
        voice_input: VoiceInputStage,
        speech_to_text: SpeechToTextStage,
        text_processor: TextProcessorStage,
        intent_classifier: IntentClassificationStage,
        llm_generator: LLMGeneratorStage,
        text_to_speech: TextToSpeechStage,
    ):
        self.voice_input = voice_input
        self.speech_to_text = speech_to_text
        self.text_processor = text_processor
        self.intent_classifier = intent_classifier
        self.llm_generator = llm_generator
        self.text_to_speech = text_to_speech
        self.error_handler = ErrorHandler()

    def execute(self, duration: float = 5.0) -> Dict[str, Any]:
        """Execute the complete pipeline with error recovery"""
        try:
            # 1. Capture voice
            audio = self.voice_input.process(duration)
            if not audio:
                logger.warning("Failed to capture audio")
                return EdgeCaseHandler.handle_empty_result("Audio capture failed")

            # 2. Convert to text
            text = self.speech_to_text.process(audio)
            if not text:
                logger.warning("Failed to transcribe audio")
                return EdgeCaseHandler.handle_empty_result("No speech detected")

            # 3. Process text
            processed = self.text_processor.process(text)
            if not processed:
                logger.warning("Failed to process text")
                return EdgeCaseHandler.handle_empty_result(text)

            # 4. Classify intent
            classified = self.intent_classifier.process(processed)
            if not classified:
                logger.warning("Failed to classify intent")
                return EdgeCaseHandler.handle_none_intent(text)

            # Handle missing confidence
            classified = EdgeCaseHandler.handle_missing_confidence(classified)

            # Handle null entities
            classified = EdgeCaseHandler.handle_null_entities(classified)

            # 5. Generate response
            response = self.llm_generator.process(classified)
            if not response:
                logger.warning("Failed to generate response")
                response = FallbackResponseGenerator.generate_processing_error_response('service')

            # 6. Play response (non-blocking failure)
            try:
                self.text_to_speech.process(response)
            except Exception as e:
                logger.warning(f"Text-to-speech failed (non-blocking): {e}")

            # Validate result structure
            result = {
                'success': True,
                'user_input': text,
                'intent': classified.get('intent') if classified else None,
                'response': response,
                'confidence': classified.get('confidence', 0.5) if classified else 0.5,
                'entities': classified.get('entities', {}) if classified else {},
            }

            result = EdgeCaseHandler.validate_result_structure(result)
            return result

        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.HIGH, "PipelineExecutor.execute")
            fallback_response = FallbackResponseGenerator.generate_generic_recovery_response()
            result = {
                'success': False,
                'error': str(e),
                'response': fallback_response,
                'user_input': '',
                'intent': None,
            }
            return EdgeCaseHandler.validate_result_structure(result)
