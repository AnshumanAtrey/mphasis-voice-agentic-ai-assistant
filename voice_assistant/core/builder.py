"""Builder for creating fully configured VoiceAgent with all dependencies"""

from pipeline.pipeline_stages import (
    VoiceInputStage,
    SpeechToTextStage,
    TextProcessorStage,
    IntentClassificationStage,
    LLMGeneratorStage,
    TextToSpeechStage,
    PipelineExecutor,
)
from services import (
    create_llm_service,
    create_speech_service,
    create_audio_service,
)
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler
from .agent import VoiceAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentBuilder:
    @staticmethod
    def create_agent(use_mock: bool = False, use_api_key: str = None) -> VoiceAgent:
        """Create a fully configured VoiceAgent"""

        logger.info("Building VoiceAgent with dependencies...")

        # Create services
        llm_service = create_llm_service(use_mock=use_mock, api_key=use_api_key)
        speech_service = create_speech_service(use_mock=use_mock)
        audio_service = create_audio_service(use_mock=use_mock)

        # Create pattern processors
        entity_extractor = EntityExtractor()
        intent_classifier = IntentClassifier()

        # Create pipeline stages
        pipeline_stages = {
            'voice_input': VoiceInputStage(audio_service),
            'speech_to_text': SpeechToTextStage(speech_service),
            'text_processor': TextProcessorStage(entity_extractor),
            'intent_classifier': IntentClassificationStage(intent_classifier),
            'llm_generator': LLMGeneratorStage(llm_service),
            'text_to_speech': TextToSpeechStage(audio_service),
        }

        pipeline_executor = PipelineExecutor(**pipeline_stages)

        # Create storage
        csv_handler = CSVHandler()
        conversation_logger = ConversationLogger(csv_handler)

        # Create and return agent
        agent = VoiceAgent(
            pipeline_executor=pipeline_executor,
            llm_service=llm_service,
            conversation_logger=conversation_logger,
        )

        logger.info("VoiceAgent created successfully")
        return agent
