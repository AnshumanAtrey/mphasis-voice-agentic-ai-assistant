# 🔧 API Reference

Complete API documentation for the Voice Agentic AI Assistant.

## Table of Contents

1. [Core Agent API](#core-agent-api)
2. [Enhanced Agent API](#enhanced-agent-api)
3. [Pattern Recognition API](#pattern-recognition-api)
4. [Error Handling API](#error-handling-api)
5. [Service APIs](#service-apis)
6. [Storage API](#storage-api)
7. [Data Types](#data-types)

## Core Agent API

### VoiceAgent

Main agent for processing voice and text input.

#### `__init__(pipeline_executor, llm_service, conversation_logger=None)`

Initialize a VoiceAgent.

**Parameters:**
- `pipeline_executor` (PipelineExecutor): Pipeline for processing
- `llm_service` (BaseLLMService): LLM service for response generation
- `conversation_logger` (ConversationLogger, optional): Logger for conversations

**Example:**
```python
agent = VoiceAgent(pipeline_executor, llm_service, conversation_logger)
```

#### `process_voice_input(duration=5.0) -> Dict[str, Any]`

Process voice input from microphone.

**Parameters:**
- `duration` (float, default=5.0): Recording duration in seconds (0.5-300)

**Returns:**
```python
{
    'success': bool,
    'user_input': str,          # Transcribed text
    'intent': IntentType,
    'response': str,
    'confidence': float,        # 0.0-1.0
    'entities': Dict[str, List],
    'error': str                # Only if success=False
}
```

**Example:**
```python
result = agent.process_voice_input(duration=5.0)
if result['success']:
    print(f"You said: {result['user_input']}")
    print(f"Response: {result['response']}")
```

#### `process_text_input(text: str) -> Dict[str, Any]`

Process text input.

**Parameters:**
- `text` (str): Text to process

**Returns:** Same as `process_voice_input()`

**Example:**
```python
result = agent.process_text_input("Show my tasks")
print(result['response'])
```

#### `get_statistics() -> Dict[str, Any]`

Get conversation statistics.

**Returns:**
```python
{
    'total': int,                    # Total conversations
    'intents': Dict[str, int]       # Intent counts
}
```

**Example:**
```python
stats = agent.get_statistics()
print(f"Total conversations: {stats['total']}")
print(f"Intent breakdown: {stats['intents']}")
```

#### `get_conversation_history() -> List[Dict[str, Any]]`

Get conversation history.

**Returns:**
```python
[
    {
        'intent': IntentType,
        'user': str,               # User input
        'response': str,           # Agent response
        'timestamp': str,
        'confidence': float
    },
    ...
]
```

**Example:**
```python
history = agent.get_conversation_history()
for turn in history:
    print(f"User: {turn['user']}")
    print(f"Agent: {turn['response']}\n")
```

---

## Enhanced Agent API

### EnhancedVoiceAgent

Extended VoiceAgent with agentic capabilities.

**Extends:** VoiceAgent

#### Additional Methods

#### `get_conversation_analysis() -> Dict[str, Any]`

Analyze conversation patterns.

**Returns:**
```python
{
    'total_turns': int,
    'unique_intents': int,
    'intent_distribution': Dict[str, int],
    'conversation_patterns': List[str],
    'avg_confidence': float
}
```

**Patterns:**
- `'starts_with_greeting'` - Conversation starts with greeting
- `'task_focused'` - Multiple task-related queries
- `'multi_intent_conversation'` - 4+ different intents
- `'contains_unrecognized_intents'` - Fallback intents present

**Example:**
```python
analysis = agent.get_conversation_analysis()
print(f"Unique intents: {analysis['unique_intents']}")
print(f"Patterns: {analysis['conversation_patterns']}")
```

#### `get_agent_insights() -> Dict[str, Any]`

Get AI agent insights about conversation.

**Returns:**
```python
{
    'is_active': bool,
    'conversation_maturity': str,       # 'new', 'developing', 'mature'
    'user_intent_clarity': float,       # 0.0-1.0
    'conversation_focus': str           # Most common intent
}
```

**Maturity Levels:**
- `'new'`: Less than 3 turns
- `'developing'`: 3-10 turns
- `'mature'`: More than 10 turns

**Example:**
```python
insights = agent.get_agent_insights()
print(f"Maturity: {insights['conversation_maturity']}")
print(f"Focus: {insights['conversation_focus']}")
```

---

## Pattern Recognition API

### EntityExtractor

Extract entities from text.

#### `extract_all_entities(text: str) -> Dict[str, List[str]]`

Extract all entity types.

**Parameters:**
- `text` (str): Text to analyze

**Returns:**
```python
{
    'emails': List[str],
    'phones': List[str],
    'dates': List[str],
    'urls': List[str],
    'persons': List[str],
    'locations': List[str],
    'organizations': List[str],
    'tasks': List[str],
    'notes': List[str],
    'summaries': List[str],
    'searches': List[str]
}
```

**Example:**
```python
extractor = EntityExtractor()
entities = extractor.extract_all_entities(
    "Email john@example.com about meeting tomorrow"
)
print(entities['emails'])  # ['john@example.com']
print(entities['dates'])   # ['tomorrow']
```

#### Specific Entity Methods

```python
extractor.extract_emails(text: str) -> List[str]
extractor.extract_phones(text: str) -> List[str]
extractor.extract_dates(text: str) -> List[str]
extractor.extract_urls(text: str) -> List[str]
extractor.extract_keywords(text: str) -> List[str]
```

**Example:**
```python
emails = extractor.extract_emails("Contact john@example.com or jane@test.com")
# Returns: ['john@example.com', 'jane@test.com']
```

### IntentClassifier

Classify user intent.

#### `classify(text: str) -> Tuple[IntentType, float]`

Classify intent with confidence.

**Parameters:**
- `text` (str): Text to classify

**Returns:**
- `IntentType`: Detected intent
- `float`: Confidence score (0.0-1.0)

**Intents:**
- `GREETING` - Hello, Hi, Hey
- `TASK_SHOW` - Show tasks, List tasks
- `NOTE_SAVE` - Save note, Remember
- `SUMMARY` - Summarize, Sum up
- `SEARCH` - Find, Search
- `FALLBACK` - Unrecognized

**Example:**
```python
classifier = IntentClassifier()
intent, confidence = classifier.classify("Show my tasks")
print(f"Intent: {intent}, Confidence: {confidence:.0%}")
# Output: Intent: IntentType.TASK_SHOW, Confidence: 90%
```

---

## Error Handling API

### InputValidator

Validate input data.

#### `validate_text_input(text: str, min_length=1, max_length=1000) -> Dict`

Validate text input.

**Returns:**
```python
{
    'valid': bool,
    'errors': List[str],
    'cleaned': str
}
```

**Checks:**
- Length constraints
- Type validation
- SQL injection patterns
- XSS patterns

**Example:**
```python
from core.error_handler import InputValidator

result = InputValidator.validate_text_input("Hello")
if result['valid']:
    print(f"Cleaned: {result['cleaned']}")
else:
    print(f"Errors: {result['errors']}")
```

#### `validate_audio_duration(duration: float) -> Dict`

Validate audio duration.

**Returns:**
```python
{
    'valid': bool,
    'errors': List[str],
    'duration': float  # Clamped to valid range
}
```

#### `validate_confidence_score(score: float) -> Dict`

Validate confidence score.

**Returns:**
```python
{
    'valid': bool,
    'errors': List[str],
    'score': float  # Clamped to 0-1 range
}
```

#### `validate_intent(intent: IntentType) -> Dict`

Validate intent object.

### ErrorHandler

Centralized error logging.

#### `log_error(error: Exception, severity: ErrorSeverity, context: str) -> Dict`

Log an error.

**Parameters:**
- `error` (Exception): Exception to log
- `severity` (ErrorSeverity): Severity level (LOW, MEDIUM, HIGH, CRITICAL)
- `context` (str): Context information

**Returns:**
```python
{
    'type': str,            # Exception class name
    'message': str,         # Exception message
    'severity': str,        # Severity level
    'context': str,         # Context information
    'recoverable': bool
}
```

**Example:**
```python
from core.error_handler import ErrorHandler, ErrorSeverity

handler = ErrorHandler()
try:
    # Some operation
    pass
except Exception as e:
    record = handler.log_error(e, ErrorSeverity.HIGH, "Processing failed")
```

#### `get_error_summary() -> Dict`

Get error summary.

**Returns:**
```python
{
    'total': int,
    'by_severity': Dict[str, int],
    'recent': List[Dict]  # Last 10 errors
}
```

### FallbackResponseGenerator

Generate fallback responses.

#### Static Methods

```python
FallbackResponseGenerator.generate_input_error_response(errors: List[str]) -> str
FallbackResponseGenerator.generate_processing_error_response(error_type: str) -> str
FallbackResponseGenerator.generate_confidence_response(confidence: float) -> str
FallbackResponseGenerator.generate_generic_recovery_response() -> str
```

**Example:**
```python
from core.error_handler import FallbackResponseGenerator

response = FallbackResponseGenerator.generate_confidence_response(0.4)
# Returns: "I'm not confident about your request. Could you clarify?"
```

---

## Service APIs

### LLMService

Generate responses using LLM.

#### `generate_response(prompt: str) -> str`

Generate a response.

**Parameters:**
- `prompt` (str): Input prompt

**Returns:**
- `str`: Generated response

**Example:**
```python
llm_service = create_llm_service(use_mock=True)
response = llm_service.generate_response("What is Python?")
```

### SpeechService

Recognize speech.

#### `recognize(audio_data: bytes) -> str`

Recognize speech from audio.

**Parameters:**
- `audio_data` (bytes): Audio data

**Returns:**
- `str`: Recognized text

### AudioService

Handle audio I/O.

#### `capture_audio(duration: float) -> bytes`

Capture audio from microphone.

**Parameters:**
- `duration` (float): Recording duration

**Returns:**
- `bytes`: Audio data

#### `play_audio(text: str) -> bool`

Play audio.

**Parameters:**
- `text` (str): Text to speak

**Returns:**
- `bool`: Success status

---

## Storage API

### ConversationLogger

Log conversations.

#### `log_conversation(turn: Dict) -> None`

Log a conversation turn.

**Parameters:**
```python
{
    'intent': IntentType,
    'user': str,
    'response': str,
    'timestamp': str,
    'confidence': float
}
```

### CSVHandler

Handle CSV operations.

#### `write_row(filename: str, data: Dict) -> None`

Write row to CSV.

#### `read_rows(filename: str) -> List[Dict]`

Read rows from CSV.

#### `append_to_file(filename: str, data: Dict) -> None`

Append row to CSV.

---

## Data Types

### IntentType (Enum)

```python
from config.constants import IntentType

IntentType.GREETING      # Hello, Hi
IntentType.TASK_SHOW     # Show tasks
IntentType.NOTE_SAVE     # Save note
IntentType.SUMMARY       # Summarize
IntentType.SEARCH        # Find, Search
IntentType.FALLBACK      # Unrecognized
```

### EntityType (Enum)

```python
from config.constants import EntityType

EntityType.EMAIL
EntityType.PHONE
EntityType.DATE
EntityType.URL
EntityType.PERSON
EntityType.LOCATION
EntityType.ORGANIZATION
EntityType.TASK
EntityType.NOTE
EntityType.SUMMARY
EntityType.SEARCH
```

### ErrorSeverity (Enum)

```python
from core.error_handler import ErrorSeverity

ErrorSeverity.LOW       # Input validation failures
ErrorSeverity.MEDIUM    # Processing failures
ErrorSeverity.HIGH      # Service failures
ErrorSeverity.CRITICAL  # Unrecoverable errors
```

---

## Complete Example

```python
from core.enhanced_agent import EnhancedVoiceAgent
from services import create_llm_service, create_speech_service, create_audio_service
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler
from pipeline.pipeline_stages import *

# Create agent
llm = create_llm_service(use_mock=True)
speech = create_speech_service(use_mock=True)
audio = create_audio_service(use_mock=True)

pipeline_stages = {
    'voice_input': VoiceInputStage(audio),
    'speech_to_text': SpeechToTextStage(speech),
    'text_processor': TextProcessorStage(EntityExtractor()),
    'intent_classifier': IntentClassificationStage(IntentClassifier()),
    'llm_generator': LLMGeneratorStage(llm),
    'text_to_speech': TextToSpeechStage(audio),
}

agent = EnhancedVoiceAgent(
    PipelineExecutor(**pipeline_stages),
    llm,
    ConversationLogger(CSVHandler())
)

# Process input
result = agent.process_text_input("Show my tasks for today")

# Get response
print(f"Intent: {result['intent']}")
print(f"Response: {result['response']}")
print(f"Confidence: {result['confidence']:.0%}")

# Analyze conversation
analysis = agent.get_conversation_analysis()
insights = agent.get_agent_insights()

print(f"Turns: {analysis['total_turns']}")
print(f"Maturity: {insights['conversation_maturity']}")
```

---

**For more examples, see [QUICK_START.md](QUICK_START.md) and [USAGE_GUIDE.md](USAGE_GUIDE.md)**
