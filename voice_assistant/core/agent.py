from typing import Dict, Any, Optional, List
from .context import ConversationContext
from pipeline.pipeline_stages import PipelineExecutor
from intents import (
    GreetingIntent,
    TaskIntent,
    NoteIntent,
    SummaryIntent,
    FallbackIntent,
)
from storage.conversation_log import ConversationLogger
from config.constants import IntentType, Messages, CSVColumns
from utils.logger import setup_logger
from utils.helpers import TextHelper

logger = setup_logger(__name__)

class VoiceAgent:
    """Main agent orchestrating the voice assistant workflow"""

    def __init__(
        self,
        pipeline_executor: PipelineExecutor,
        llm_service,
        conversation_logger: Optional[ConversationLogger] = None,
    ):
        self.pipeline = pipeline_executor
        self.llm_service = llm_service
        self.logger = conversation_logger or ConversationLogger()
        self.context = ConversationContext()

        # Initialize intent handlers
        self.intent_handlers = {
            IntentType.GREETING: GreetingIntent(llm_service),
            IntentType.TASK_SHOW: TaskIntent(llm_service),
            IntentType.NOTE_SAVE: NoteIntent(llm_service),
            IntentType.SUMMARY: SummaryIntent(llm_service),
            IntentType.FALLBACK: FallbackIntent(llm_service),
        }

    def process_voice_input(self, duration: float = 5.0) -> Dict[str, Any]:
        """Process a complete voice interaction"""
        logger.info("Starting voice input processing...")

        try:
            # Execute pipeline
            result = self.pipeline.execute(duration)

            if not result['success']:
                return {
                    'success': False,
                    'response': Messages.ERROR_PROCESS,
                    'error': result.get('error'),
                }

            user_input = result.get('user_input')
            intent = result.get('intent')
            llm_response = result.get('response')

            # Route to intent handler if needed
            if intent and intent != IntentType.FALLBACK:
                handler = self.intent_handlers.get(intent)
                if handler:
                    context_data = {
                        'original': user_input,
                        'intent': intent,
                        'history': self.context.get_history(),
                    }
                    response = handler.handle(context_data)
                else:
                    response = llm_response
            else:
                response = llm_response

            # Log conversation
            self.logger.log_conversation(
                user_input=user_input,
                ai_response=response,
                intent=str(intent) if intent else 'unknown',
                confidence=0.8,  # TODO: use actual confidence from pipeline
            )

            # Add to context history
            self.context.add_turn(user_input, response, str(intent) if intent else 'unknown')

            return {
                'success': True,
                'user_input': user_input,
                'intent': intent,
                'response': response,
            }

        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {
                'success': False,
                'response': Messages.ERROR_PROCESS,
                'error': str(e),
            }

    def process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text input directly (for testing/UI)"""
        logger.info(f"Processing text input: {text}")

        try:
            # Process through text processing stages of pipeline
            from pipeline.pipeline_stages import (
                TextProcessorStage,
                IntentClassificationStage,
                LLMGeneratorStage,
            )

            processed = TextProcessorStage().process(text)
            classified = IntentClassificationStage().process(processed)
            response = LLMGeneratorStage(self.llm_service).process(classified)

            # Log conversation
            self.logger.log_conversation(
                user_input=text,
                ai_response=response,
                intent=str(classified.get('intent')) if classified else 'unknown',
                confidence=classified.get('confidence', 0.5) if classified else 0.5,
            )

            # Add to context
            self.context.add_turn(
                text,
                response,
                str(classified.get('intent')) if classified else 'unknown'
            )

            return {
                'success': True,
                'user_input': text,
                'intent': classified.get('intent') if classified else IntentType.FALLBACK,
                'response': response,
            }

        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            return {
                'success': False,
                'response': Messages.ERROR_PROCESS,
                'error': str(e),
            }

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.context.get_history()

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return self.logger.get_statistics()

    def clear_context(self):
        """Clear conversation context"""
        self.context.clear()
        logger.info("Conversation context cleared")
