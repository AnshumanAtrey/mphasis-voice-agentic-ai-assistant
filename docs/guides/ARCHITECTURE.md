# Voice Agentic AI Assistant - Architecture Documentation

## System Overview

The Voice Agentic AI Assistant is built using a **Pipeline-Centric Agent Pattern** that combines sequential processing stages with intelligent intent routing and context management.

## Architecture Layers

### 1. **Atoms Layer** (Reusable Building Blocks)
```
patterns/regex_library.py
├── Email patterns
├── Phone patterns
├── Date patterns
├── URL patterns
├── Greeting patterns
└── Command patterns

utils/validators.py
├── EmailValidator
├── PhoneValidator
├── URLValidator
└── DateValidator

utils/helpers.py
├── TextHelper.clean_text()
├── TextHelper.tokenize()
├── TextHelper.get_timestamp()
└── ...
```

**Purpose**: Provide low-level, reusable components for text processing and validation.

### 2. **Molecules Layer** (Single-Responsibility Components)

#### Services (External Integrations)
```
services/
├── llm_service.py          # Gemini/LLM wrapper
│   ├── BaseLLMService (ABC)
│   ├── GeminiLLMService
│   ├── MockLLMService
│   └── create_llm_service()
│
├── speech_service.py       # Speech recognition
│   ├── BaseSpeechService (ABC)
│   ├── GoogleSpeechService
│   ├── MockSpeechService
│   └── create_speech_service()
│
└── audio_service.py        # Audio I/O
    ├── BaseAudioService (ABC)
    ├── PyAudioService
    ├── MockAudioService
    └── create_audio_service()
```

**Purpose**: Abstract external services with dependency injection for testability.

#### Pattern Processing
```
patterns/
├── entity_extractor.py     # Extract emails, phones, dates
├── intent_classifier.py    # Classify user intent
└── regex_library.py        # Central regex library
```

**Purpose**: Extract structured data and classify intent from user input.

#### Pipeline Stages
```
pipeline/pipeline_stages.py
├── VoiceInputStage          # Capture microphone audio
├── SpeechToTextStage        # Speech recognition
├── TextProcessorStage       # Clean & extract entities
├── IntentClassificationStage # Classify intent
├── LLMGeneratorStage        # Generate response
└── TextToSpeechStage        # Convert response to speech
```

**Purpose**: Each stage is independent, testable, and composable.

#### Storage
```
storage/
├── csv_handler.py           # Low-level CSV operations
└── conversation_log.py      # High-level logging API
```

**Purpose**: Persist conversations and analytics data.

### 3. **Organisms Layer** (Assembled Components with Logic)

#### Intent Handlers
```
intents/
├── base_intent.py           # BaseIntent (ABC)
├── greeting_intent.py       # Handle greetings
├── task_intent.py           # Handle "Show tasks"
├── note_intent.py           # Handle "Save note"
├── summary_intent.py        # Handle "Summarize"
└── fallback_intent.py       # Handle unknown intents
```

**Purpose**: Domain-specific handlers with specialized prompts and logic.

#### Pipeline Executor
```
pipeline/pipeline_stages.py :: PipelineExecutor
├── Orchestrates all stages
├── Handles errors gracefully
└── Returns structured results
```

**Purpose**: Manages the complete voice→text→intent→response→voice flow.

### 4. **Systems Layer** (Full Orchestration)

#### Conversation Context
```
core/context.py :: ConversationContext
├── Maintains conversation history
├── Provides context summaries
└── Manages session state
```

#### Main Agent
```
core/agent.py :: VoiceAgent
├── Coordinates all components
├── Routes to intent handlers
├── Logs conversations
└── Maintains context
```

#### Dependency Injection
```
core/builder.py :: AgentBuilder
├── Creates fully configured agent
├── Wires all dependencies
└── Handles service creation
```

## Data Flow

```
┌──────────────┐
│ User Input   │ (Voice or Text)
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ VoiceInputStage          │ (Capture audio from microphone)
└──────┬───────────────────┘
       │ bytes
       ▼
┌──────────────────────────┐
│ SpeechToTextStage        │ (Convert speech to text)
└──────┬───────────────────┘
       │ "Show today's tasks"
       ▼
┌──────────────────────────┐
│ TextProcessorStage       │ (Clean, extract entities)
└──────┬───────────────────┘
       │ {original, cleaned, entities, keywords}
       ▼
┌──────────────────────────┐
│ IntentClassificationStage│ (Classify intent)
└──────┬───────────────────┘
       │ {intent: TASK_SHOW, confidence: 0.85}
       ▼
┌──────────────────────────┐
│ LLMGeneratorStage        │ (Generate response via Gemini)
└──────┬───────────────────┘
       │ "You have 3 tasks due today..."
       ▼
┌──────────────────────────┐
│ TextToSpeechStage        │ (Convert text to speech)
└──────┬───────────────────┘
       │ audio output
       ▼
┌──────────────────────────┐
│ ConversationLogger       │ (Store in CSV)
└──────────────────────────┘
```

## Intent Classification

### Intent Types
| Intent | Pattern | Handler | Example |
|--------|---------|---------|---------|
| GREETING | Greeting keywords | GreetingIntent | "Hello", "Hi" |
| TASK_SHOW | "Show" + task keywords | TaskIntent | "Show today's tasks" |
| NOTE_SAVE | "Save" command | NoteIntent | "Save this note" |
| SUMMARY | "Summarize" command | SummaryIntent | "Summarize this" |
| SEARCH | "Search/Find" command | SearchIntent | "Find my emails" |
| FALLBACK | Unknown | FallbackIntent | Any unmatched input |

### Classification Logic
```
1. Check if greeting (95% confidence)
2. Extract all entities (emails, phones, dates)
3. Detect command type (show, save, summarize, search)
4. Check for task/note/time keywords
5. Classify intent with confidence score
6. Route to appropriate handler
```

## Pattern Extraction

The system can extract and validate:

### Entities
- **Emails**: john@example.com, user+tag@domain.co.uk
- **Phone Numbers**: 555-123-4567, +1-555-123-4567, (555) 123-4567
- **Dates**: 12/25/2024, 2024-12-25, December 25, Dec 25
- **URLs**: https://example.com/path

### Keywords
- **Task Keywords**: task, tasks, todo, to-do, remind, schedule
- **Note Keywords**: note, notes, memo, reminder, message
- **Time Keywords**: today, tomorrow, today's, this, next, now

### Commands
- **Show Command**: show, display, list, get
- **Save Command**: save, store, write, note
- **Summarize Command**: summarize, summary, brief, condense
- **Search Command**: search, find, look for

## Dependency Injection Pattern

All services use factory functions for easy testing:

```python
# Production with real APIs
agent = AgentBuilder.create_agent(use_mock=False, use_api_key="...")

# Testing with mock services (no API keys needed)
agent = AgentBuilder.create_agent(use_mock=True)
```

## Error Handling

Each pipeline stage has graceful error handling:

1. **VoiceInputStage**: Returns None on audio capture failure
2. **SpeechToTextStage**: Returns None on recognition failure
3. **TextProcessorStage**: Continues with empty entities
4. **LLMGeneratorStage**: Returns error message on API failure
5. **TextToSpeechStage**: Returns False on TTS failure

The PipelineExecutor catches exceptions and returns a failure result.

## Storage Strategy

### CSV File Structure
```
timestamp | user_input | intent | entities | ai_response | confidence
```

### Location
```
data/conversations/conversations.csv
```

### Usage
```python
# Log a conversation
logger.log_conversation(
    user_input="Show my tasks",
    ai_response="You have 3 tasks...",
    intent="task_show",
    entities={'task_keywords': ['tasks']},
    confidence=0.85
)

# Get statistics
stats = agent.get_statistics()
# Returns: {'total': 10, 'intents': {'greeting': 3, 'task_show': 5, ...}}
```

## Configuration

All settings in `config/settings.py`:

```python
# Audio settings
SAMPLE_RATE = 16000
AUDIO_FORMAT = 'wav'

# LLM settings
LLM_MODEL = 'gemini-pro'
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 500

# Speech settings
SPEECH_LANGUAGE = 'en-US'
TTS_RATE = 150

# Context settings
CONTEXT_WINDOW_SIZE = 5
INTENT_CONFIDENCE_THRESHOLD = 0.6
```

## Testing Strategy

### Unit Tests (test_patterns.py)
```python
✓ Regex pattern matching
✓ Email extraction
✓ Phone number extraction
✓ Intent classification
✓ Greeting detection
```

### Integration Tests (test_integration.py)
```python
✓ Full pipeline with mock services
✓ Context tracking across turns
✓ Statistics calculation
✓ Entity extraction end-to-end
```

## Extensibility

### Adding a New Intent

1. Create `intents/custom_intent.py`:
```python
from intents.base_intent import BaseIntent
from config.constants import IntentType

class CustomIntent(BaseIntent):
    def can_handle(self, context):
        return context.get('intent') == IntentType.CUSTOM

    def handle(self, context):
        # Your logic here
        return "Response"
```

2. Register in `core/agent.py`:
```python
self.intent_handlers = {
    IntentType.CUSTOM: CustomIntent(llm_service),
}
```

### Adding a New Service

1. Create abstract base:
```python
from abc import ABC, abstractmethod

class CustomService(ABC):
    @abstractmethod
    def process(self):
        pass
```

2. Implement concrete service
3. Add factory function in `__init__.py`
4. Wire in `AgentBuilder.create_agent()`

### Adding a New Pattern

Add to `patterns/regex_library.py`:
```python
CUSTOM_PATTERN = re.compile(r'your_pattern')

@classmethod
def find_custom(cls, text: str):
    return cls.CUSTOM_PATTERN.findall(text)
```

## Performance Characteristics

| Component | Latency | Bottleneck |
|-----------|---------|-----------|
| Voice Capture | 5s (configurable) | User speaking |
| Speech-to-Text | 1-3s | API latency |
| Text Processing | <100ms | Local only |
| Intent Classification | <50ms | Regex matching |
| LLM Generation | 2-5s | API latency |
| Text-to-Speech | 1-2s | Synthesis time |
| **Total** | **10-20s** | LLM API calls |

## Security Considerations

- API keys stored in `.env`, never committed to git
- No sensitive data logged in CSV
- Input validation on all user input
- All external API calls through service layer
- Mock services for testing without credentials

## Future Enhancements

1. **Multi-turn Context**: Use conversation history in LLM prompts
2. **Tool Calling**: LLM can call functions (create task, send email)
3. **Vector Search**: Search conversation history semantically
4. **Voice Profiles**: Different voices for different personas
5. **Multi-language**: Support multiple languages
6. **Real-time Streaming**: Stream LLM responses as they arrive
7. **Caching**: Cache LLM responses for identical queries
