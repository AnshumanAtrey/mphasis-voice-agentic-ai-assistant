"""Enhanced VoiceAgent with sophisticated agentic behavior"""

from typing import Dict, Any, Optional, List
from .agent import VoiceAgent
from .context import ConversationContext
from pipeline.pipeline_stages import PipelineExecutor
from storage.conversation_log import ConversationLogger
from config.constants import IntentType, Messages
from utils.logger import setup_logger
from core.error_handler import (
    ErrorHandler, ErrorSeverity, InputValidator, EdgeCaseHandler,
    FallbackResponseGenerator
)
import re

logger = setup_logger(__name__)


class EnhancedVoiceAgent(VoiceAgent):
    """VoiceAgent with context awareness, follow-up detection, and conditional routing"""

    def __init__(
        self,
        pipeline_executor: PipelineExecutor,
        llm_service,
        conversation_logger: Optional[ConversationLogger] = None,
    ):
        super().__init__(pipeline_executor, llm_service, conversation_logger)
        self.error_handler = ErrorHandler()
        self.follow_up_patterns = {
            'also': 'additional_intent',
            'additionally': 'additional_intent',
            'besides': 'additional_intent',
            'furthermore': 'additional_intent',
            'too': 'additional_intent',
            'as well': 'additional_intent',
            'what about': 'follow_up_question',
            'and': 'continuation',
            'but': 'correction',
            'actually': 'correction',
            'wait': 'correction',
            'no': 'negation',
            'cancel': 'negation',
        }

    def process_voice_input(self, duration: float = 5.0) -> Dict[str, Any]:
        """Process voice with enhanced context awareness"""
        result = super().process_voice_input(duration)

        if result['success']:
            # Enhance with context-aware logic
            result = self._apply_context_awareness(result)
            # Detect if follow-up or clarification needed
            result = self._detect_follow_up_needs(result)
            # Apply conditional routing
            result = self._apply_conditional_routing(result)

        return result

    def process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text with enhanced context awareness and error handling"""
        try:
            # Validate input
            validation = InputValidator.validate_text_input(text)
            if not validation['valid']:
                logger.warning(f"Text validation failed: {validation['errors']}")
                self.error_handler.log_error(
                    ValueError(f"Input validation: {validation['errors']}"),
                    ErrorSeverity.LOW,
                    "EnhancedVoiceAgent.process_text_input"
                )
                return {
                    'success': False,
                    'user_input': text,
                    'response': FallbackResponseGenerator.generate_input_error_response(validation['errors']),
                    'intent': None,
                    'error': 'Input validation failed'
                }

            result = super().process_text_input(validation['cleaned'])

            if result.get('success'):
                # Ensure result structure
                result = EdgeCaseHandler.validate_result_structure(result)
                # Enhance with context-aware logic
                result = self._apply_context_awareness(result)
                # Detect if follow-up or clarification needed
                result = self._detect_follow_up_needs(result)
                # Apply conditional routing
                result = self._apply_conditional_routing(result)
            else:
                # Handle failed processing
                result = EdgeCaseHandler.validate_result_structure(result)

            return result
        except Exception as e:
            self.error_handler.log_error(e, ErrorSeverity.HIGH, "EnhancedVoiceAgent.process_text_input")
            return {
                'success': False,
                'user_input': text,
                'response': FallbackResponseGenerator.generate_generic_recovery_response(),
                'intent': None,
                'error': str(e)
            }

    def _apply_context_awareness(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Make responses context-aware using conversation history"""
        history = self.context.get_history()

        if len(history) == 0:
            # First message - no context
            return result

        user_input = result.get('user_input', '')
        current_intent = result.get('intent')

        # Check if this is a follow-up on previous intent
        if len(history) > 0:
            last_turn = history[-1]
            last_intent = last_turn.get('intent')

            # If same intent repeated, add contextual reference
            if current_intent == last_intent and len(history) > 1:
                result = self._generate_contextualized_response(result, last_turn, history)

            # If related intent, reference the context
            if current_intent != last_intent and self._is_related_intent(current_intent, last_intent):
                result = self._add_context_reference(result, last_intent)

        logger.info(f"Applied context awareness. History length: {len(history)}")
        return result

    def _is_related_intent(self, current: IntentType, previous: IntentType) -> bool:
        """Check if current intent is related to previous intent"""
        related_pairs = [
            (IntentType.TASK_SHOW, IntentType.NOTE_SAVE),
            (IntentType.NOTE_SAVE, IntentType.TASK_SHOW),
            (IntentType.SUMMARY, IntentType.NOTE_SAVE),
            (IntentType.SEARCH, IntentType.TASK_SHOW),
        ]

        return (current, previous) in related_pairs or (previous, current) in related_pairs

    def _generate_contextualized_response(
        self,
        result: Dict[str, Any],
        last_turn: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate response that acknowledges and builds on previous context"""

        # Count how many times this intent has been asked
        intent_count = sum(1 for turn in history if turn.get('intent') == result.get('intent'))

        if intent_count > 1:
            # Multiple queries for same intent - provide additional details
            context_note = f"\n\n[Following up on your {result['intent'].value} request]"
            if intent_count > 2:
                context_note += " (I see you've asked about this before)"

            result['response'] = result.get('response', '') + context_note
            result['context_reference'] = intent_count

        return result

    def _add_context_reference(self, result: Dict[str, Any], last_intent: IntentType) -> Dict[str, Any]:
        """Add reference to previous intent in response"""

        reference = f"\n[Continuing from your previous {last_intent.value} request]"
        result['response'] = result.get('response', '') + reference
        result['related_to_previous'] = last_intent

        return result

    def _detect_follow_up_needs(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if clarification or follow-up is needed"""

        confidence = result.get('confidence', 0.5)
        user_input = result.get('user_input', '')

        # Check confidence level
        if confidence < 0.65:
            result['needs_clarification'] = True
            result['clarification_prompt'] = self._generate_clarification_prompt(
                result.get('intent'),
                user_input
            )
            logger.info(f"Low confidence ({confidence:.0%}), clarification needed")
            return result

        # Check for ambiguous patterns in input
        if self._is_ambiguous_input(user_input):
            result['ambiguous'] = True
            result['ambiguity_note'] = "Your request could mean multiple things"
            logger.info("Ambiguous input detected")
            return result

        result['needs_clarification'] = False
        return result

    def _generate_clarification_prompt(self, intent: IntentType, user_input: str) -> str:
        """Generate a clarification question based on detected intent"""

        clarifications = {
            IntentType.GREETING: "Did you want to ask me something?",
            IntentType.TASK_SHOW: "Did you want to see today's tasks or something specific?",
            IntentType.NOTE_SAVE: "What exactly would you like me to save?",
            IntentType.SUMMARY: "What would you like me to summarize?",
            IntentType.SEARCH: "What are you looking for?",
            IntentType.FALLBACK: "Could you rephrase that?",
        }

        return clarifications.get(intent, "Could you provide more details?")

    def _is_ambiguous_input(self, text: str) -> bool:
        """Check if input is ambiguous"""

        # Check for ambiguous patterns
        ambiguous_patterns = [
            r'\bthis\b',  # "this" without context
            r'\bthat\b',  # "that" without context
            r'\bit\b',    # "it" without context
        ]

        if len(text) < 5:
            return True  # Very short input is ambiguous

        return False

    def _apply_conditional_routing(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent conditional routing based on context and patterns"""

        user_input = result.get('user_input', '')
        current_intent = result.get('intent')
        history = self.context.get_history()

        # Rule 1: Detect follow-up patterns and adjust intent
        follow_up_type = self._detect_follow_up_pattern(user_input)
        if follow_up_type:
            result['follow_up_type'] = follow_up_type
            result['routing_note'] = f"Detected {follow_up_type} pattern"
            logger.info(f"Follow-up pattern detected: {follow_up_type}")

        # Rule 2: If multiple entities extracted, suggest grouping
        entities = self._count_extracted_entities(result)
        if entities > 1:
            result['multi_entity'] = True
            result['entity_count'] = entities
            logger.info(f"Multiple entities detected: {entities}")

        # Rule 3: Conditional response based on history
        if len(history) > 2:
            result = self._apply_history_based_routing(result, history)

        # Rule 4: Intent-specific conditional logic
        result = self._apply_intent_specific_routing(result, current_intent)

        return result

    def _detect_follow_up_pattern(self, text: str) -> Optional[str]:
        """Detect follow-up patterns in user input"""

        text_lower = text.lower()

        for pattern, follow_up_type in self.follow_up_patterns.items():
            if pattern in text_lower:
                return follow_up_type

        return None

    def _count_extracted_entities(self, result: Dict[str, Any]) -> int:
        """Count total extracted entities"""

        # Get entities from pipeline result (if available in conversation)
        history = self.context.get_history()
        if history:
            last = history[-1]
            entities = last.get('entities', {})
            return sum(len(v) for v in entities.values() if v)

        return 0

    def _apply_history_based_routing(self, result: Dict[str, Any], history: List[Dict]) -> Dict[str, Any]:
        """Apply routing based on conversation history patterns"""

        # Detect conversation flow patterns
        recent_intents = [turn.get('intent') for turn in history[-3:]]

        # Pattern: Task -> Note -> Task (likely task management session)
        if len(recent_intents) >= 3:
            if (recent_intents[0] == IntentType.TASK_SHOW and
                recent_intents[1] == IntentType.NOTE_SAVE and
                recent_intents[2] == IntentType.TASK_SHOW):
                result['conversation_pattern'] = 'task_management_session'
                result['routing_note'] = 'Detected task management workflow'

        # Pattern: Multiple same intents = user trying different angles
        if len(set(recent_intents)) == 1 and recent_intents[0] != IntentType.GREETING:
            result['retry_pattern'] = True
            result['routing_note'] = 'User is retrying the same intent'
            logger.info("Retry pattern detected")

        return result

    def _apply_intent_specific_routing(self, result: Dict[str, Any], intent: IntentType) -> Dict[str, Any]:
        """Apply conditional logic specific to detected intent"""

        if intent == IntentType.TASK_SHOW:
            # For task queries, check if time period was specified
            user_input = result.get('user_input', '').lower()
            time_periods = {
                'today': 'today',
                'tomorrow': 'tomorrow',
                'this week': 'this_week',
                'next week': 'next_week',
            }

            for period, key in time_periods.items():
                if period in user_input:
                    result['task_period'] = key
                    result['routing_note'] = f'Task query for {key}'
                    break

        elif intent == IntentType.NOTE_SAVE:
            # For note saving, check for note type
            user_input = result.get('user_input', '').lower()
            if 'meeting' in user_input:
                result['note_type'] = 'meeting'
            elif 'reminder' in user_input:
                result['note_type'] = 'reminder'
            elif 'todo' in user_input or 'todo' in user_input:
                result['note_type'] = 'todo'

        elif intent == IntentType.SUMMARY:
            # For summaries, check what to summarize
            user_input = result.get('user_input', '').lower()
            if 'email' in user_input:
                result['summary_target'] = 'email'
            elif 'message' in user_input:
                result['summary_target'] = 'message'
            elif 'document' in user_input:
                result['summary_target'] = 'document'

        return result

    def get_conversation_analysis(self) -> Dict[str, Any]:
        """Analyze conversation patterns and provide insights"""

        history = self.context.get_history()
        if not history:
            return {'analysis': 'No conversations yet'}

        # Analyze intent distribution
        intent_counts = {}
        for turn in history:
            intent = turn.get('intent', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        # Detect conversation patterns
        patterns = self._detect_conversation_patterns(history)

        return {
            'total_turns': len(history),
            'unique_intents': len(intent_counts),
            'intent_distribution': intent_counts,
            'conversation_patterns': patterns,
            'avg_confidence': sum(turn.get('confidence', 0.5) for turn in history) / len(history),
        }

    def _detect_conversation_patterns(self, history: List[Dict[str, Any]]) -> List[str]:
        """Detect high-level conversation patterns"""

        patterns = []

        if len(history) < 2:
            return patterns

        intents = [turn.get('intent') for turn in history]

        # Pattern: Greeting at start
        if intents[0] == IntentType.GREETING:
            patterns.append('starts_with_greeting')

        # Pattern: Multiple task queries
        task_queries = sum(1 for i in intents if i == IntentType.TASK_SHOW)
        if task_queries >= 2:
            patterns.append('task_focused')

        # Pattern: Mixed intents (diverse conversation)
        if len(set(intents)) >= 4:
            patterns.append('multi_intent_conversation')

        # Pattern: Repeated intents with fallback
        if IntentType.FALLBACK in intents:
            patterns.append('contains_unrecognized_intents')

        return patterns

    def get_agent_insights(self) -> Dict[str, Any]:
        """Get AI-agent specific insights about the conversation"""

        analysis = self.get_conversation_analysis()
        history = self.context.get_history()

        insights = {
            'is_active': len(history) > 0,
            'conversation_maturity': 'new' if len(history) < 3 else 'developing' if len(history) < 10 else 'mature',
            'user_intent_clarity': analysis.get('avg_confidence', 0),
            'conversation_focus': self._determine_conversation_focus(history),
        }

        return insights

    def _determine_conversation_focus(self, history: List[Dict[str, Any]]) -> str:
        """Determine the main focus of the conversation"""

        if not history:
            return 'unknown'

        intent_counts = {}
        for turn in history:
            intent = turn.get('intent', 'unknown')
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        most_common = max(intent_counts, key=intent_counts.get)
        return most_common if most_common != 'unknown' else 'varied'
