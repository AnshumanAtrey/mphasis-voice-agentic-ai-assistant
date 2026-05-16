# ⚡ Quick Start Guide

Get the Voice Agentic AI Assistant running in 5 minutes!

## Prerequisites

- Python 3.8+
- Microphone (optional, text input also supported)

## Installation

```bash
# Clone the repository
git clone https://github.com/AnshumanAtrey/mphasis-voice-agentic-ai-assistant.git
cd mphasis-voice-agentic-ai-assistant/voice_assistant

# No additional dependencies needed!
# (All services use mock implementations by default)
```

## Run the Application

### Option 1: Interactive CLI (Recommended)

```bash
python3 main.py
```

**Menu Options:**
```
1. Voice Input (requires microphone)
2. Text Input (for testing)
3. View Statistics
4. View History
5. View Agent Insights
6. View Conversation Analysis
7. Exit
```

### Option 2: Text-Based Testing

```bash
python3 main.py
# Select option 2 (Text Input)
# Type: "Show my tasks"
# Get instant response with intent analysis
```

### Option 3: Run Interactive Demo

```bash
python3 demo_error_handling.py
```

Shows error handling, security, and edge case handling with 9 different scenarios.

## Basic Usage Examples

### Python API

```python
from core.enhanced_agent import EnhancedVoiceAgent
from services import create_llm_service, create_speech_service, create_audio_service
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler
from pipeline.pipeline_stages import *

# Create services
llm_service = create_llm_service(use_mock=True)
speech_service = create_speech_service(use_mock=True)
audio_service = create_audio_service(use_mock=True)

# Create pipeline
entity_extractor = EntityExtractor()
intent_classifier = IntentClassifier()

pipeline_stages = {
    'voice_input': VoiceInputStage(audio_service),
    'speech_to_text': SpeechToTextStage(speech_service),
    'text_processor': TextProcessorStage(entity_extractor),
    'intent_classifier': IntentClassificationStage(intent_classifier),
    'llm_generator': LLMGeneratorStage(llm_service),
    'text_to_speech': TextToSpeechStage(audio_service),
}

pipeline_executor = PipelineExecutor(**pipeline_stages)
conversation_logger = ConversationLogger(CSVHandler())

# Create agent
agent = EnhancedVoiceAgent(
    pipeline_executor=pipeline_executor,
    llm_service=llm_service,
    conversation_logger=conversation_logger,
)

# Process input
result = agent.process_text_input("Show my tasks for today")

# Get response
print(result['response'])
# Output: "You have 3 tasks due today: finish project report, review code, update documentation."

# Get intent
print(result['intent'])
# Output: IntentType.TASK_SHOW

# Get confidence
print(f"Confidence: {result['confidence']:.0%}")
# Output: "Confidence: 50%"
```

## Common Tasks

### 1. Process Text and Get Response

```python
result = agent.process_text_input("Save this note: Important meeting tomorrow")

print(f"Intent: {result['intent']}")
print(f"Response: {result['response']}")
print(f"Success: {result['success']}")
```

### 2. Get Conversation History

```python
history = agent.get_conversation_history()

for turn in history:
    print(f"You: {turn['user']}")
    print(f"Assistant: {turn['response']}")
    print(f"Intent: {turn['intent']}\n")
```

### 3. View Conversation Analysis

```python
analysis = agent.get_conversation_analysis()

print(f"Total turns: {analysis['total_turns']}")
print(f"Intent distribution: {analysis['intent_distribution']}")
print(f"Detected patterns: {analysis['conversation_patterns']}")
print(f"Average confidence: {analysis['avg_confidence']:.0%}")
```

### 4. Get Agent Insights

```python
insights = agent.get_agent_insights()

print(f"Is Active: {insights['is_active']}")
print(f"Conversation Maturity: {insights['conversation_maturity']}")
print(f"User Intent Clarity: {insights['user_intent_clarity']:.0%}")
print(f"Conversation Focus: {insights['conversation_focus']}")
```

### 5. Extract Entities from Text

```python
from patterns import EntityExtractor

extractor = EntityExtractor()
text = "Email me at john@example.com and call 555-1234 tomorrow at 3pm"

entities = extractor.extract_all_entities(text)
print(entities)
# Output: {
#   'emails': ['john@example.com'],
#   'phones': ['555-1234'],
#   'dates': ['tomorrow'],
#   'times': ['3pm']
# }
```

### 6. Classify Intent

```python
from patterns import IntentClassifier

classifier = IntentClassifier()
text = "Show me today's tasks"

intent, confidence = classifier.classify(text)
print(f"Intent: {intent}, Confidence: {confidence:.0%}")
# Output: Intent: IntentType.TASK_SHOW, Confidence: 90%
```

## Running Tests

```bash
# Run all tests
python3 tests/test_enhanced_agent.py
python3 tests/test_error_handler.py
python3 tests/test_error_edge_cases.py

# Expected output: ✅ ALL TESTS PASSED
```

## Features Showcase

### 🧠 Smart Follow-Up Detection

```python
agent.process_text_input("Show my tasks")
# Intent: TASK_SHOW

agent.process_text_input("Also save this note")
# Detects "also" as follow-up pattern
# Automatically routes to NOTE_SAVE
```

### 🎯 Confidence-Based Clarification

```python
result = agent.process_text_input("it")
# Confidence: 50% (low)
# Response includes: "Could you clarify?"
# needs_clarification: True
```

### 🛡️ Security Features

```python
# SQL Injection Prevention
result = agent.process_text_input("'; DROP TABLE users; --")
# Result: blocked, helpful error message

# XSS Prevention
result = agent.process_text_input("<script>alert('xss')</script>")
# Result: blocked, helpful error message
```

### 📊 Context Awareness

```python
# Turn 1
agent.process_text_input("Show my tasks")
# Response: "You have 3 tasks..."

# Turn 2
agent.process_text_input("Show my tasks again")
# Agent recognizes repetition, adds context
# Response: "[Following up on your task_show request] You have 3 tasks..."
```

## Troubleshooting

### Issue: "No module named 'services'"

**Solution**: Make sure you're running from the `voice_assistant` directory or adjust your Python path:
```bash
cd voice_assistant
python3 main.py
```

### Issue: "Microphone not available"

**Solution**: Use text input instead (Option 2 in menu) or check microphone permissions.

### Issue: Tests fail with import errors

**Solution**: Ensure you're in the voice_assistant directory:
```bash
cd voice_assistant
python3 tests/test_enhanced_agent.py
```

## File Organization

```
voice_assistant/
├── main.py              # CLI application (start here!)
├── core/               # Core agent logic
├── pipeline/           # Processing pipeline
├── patterns/           # Intent & entity recognition
├── services/           # External service adapters
├── storage/            # Data persistence
├── intents/            # Intent handlers
├── tests/              # Test suite
└── demo_error_handling.py  # Interactive demo
```

## Next Steps

1. **Explore Features**: Run `main.py` and try different input types
2. **Review Documentation**: Check `ARCHITECTURE.md` and `USAGE_GUIDE.md`
3. **Run Tests**: Execute test files to see all capabilities
4. **Modify Code**: Customize intents, add entities, adjust responses
5. **Integrate**: Use the Python API in your own applications

## Performance Tips

1. **Use Text Input for Testing**: Faster than voice (no audio processing)
2. **Cache Agent Instance**: Create once, reuse for multiple inputs
3. **Review Conversation History**: Use `get_conversation_history()` to analyze patterns
4. **Check Agent Insights**: Use `get_agent_insights()` for conversation metrics

## API Documentation

For detailed API reference, see [API_REFERENCE.md](API_REFERENCE.md)

## Support & Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

**Ready to explore?** Run `python3 main.py` now! 🚀

**Questions?** Check the other documentation files or review the test cases for more examples.
