# 📖 Usage Guide

Comprehensive guide to using the Voice Agentic AI Assistant.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Advanced Features](#advanced-features)
3. [Error Handling](#error-handling)
4. [Integration Guide](#integration-guide)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Basic Usage

### Creating an Agent

```python
from core.enhanced_agent import EnhancedVoiceAgent
from services import create_llm_service, create_speech_service, create_audio_service
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler
from pipeline.pipeline_stages import *

# Step 1: Create services
llm_service = create_llm_service(use_mock=True)
speech_service = create_speech_service(use_mock=True)
audio_service = create_audio_service(use_mock=True)

# Step 2: Create components
entity_extractor = EntityExtractor()
intent_classifier = IntentClassifier()

# Step 3: Create pipeline stages
pipeline_stages = {
    'voice_input': VoiceInputStage(audio_service),
    'speech_to_text': SpeechToTextStage(speech_service),
    'text_processor': TextProcessorStage(entity_extractor),
    'intent_classifier': IntentClassificationStage(intent_classifier),
    'llm_generator': LLMGeneratorStage(llm_service),
    'text_to_speech': TextToSpeechStage(audio_service),
}

# Step 4: Create executor
pipeline_executor = PipelineExecutor(**pipeline_stages)

# Step 5: Create logger
conversation_logger = ConversationLogger(CSVHandler())

# Step 6: Create agent
agent = EnhancedVoiceAgent(
    pipeline_executor=pipeline_executor,
    llm_service=llm_service,
    conversation_logger=conversation_logger,
)

# Ready to use!
result = agent.process_text_input("Your input here")
```

### Processing Text Input

```python
# Simple text processing
result = agent.process_text_input("Show my tasks")

# Check if successful
if result['success']:
    print(f"Intent: {result['intent']}")
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['confidence']:.0%}")
else:
    print(f"Error: {result['error']}")
```

### Processing Voice Input

```python
# Record voice for 5 seconds
result = agent.process_voice_input(duration=5.0)

# Same result structure as text input
if result['success']:
    print(f"Transcribed: {result['user_input']}")
    print(f"Response: {result['response']}")
```

## Advanced Features

### 1. Context-Aware Conversations

```python
# First turn
result1 = agent.process_text_input("Show my tasks")
print(result1['response'])
# Output: "You have 3 tasks..."

# Second turn (same topic)
result2 = agent.process_text_input("Show my tasks again")
print(result2.get('context_reference'))
# Output: 2 (recognizes this is the 2nd time asking)

# Agent adds context to response
print(result2['response'])
# Output: "[Following up on your task_show request] You have 3 tasks..."
```

### 2. Follow-Up Pattern Detection

```python
# Detect "also" pattern
result = agent.process_text_input("Show tasks and also save this note")

print(result.get('follow_up_type'))
# Output: "additional_intent"

# Detect "what about" pattern
result = agent.process_text_input("What about next week's tasks?")
print(result.get('follow_up_type'))
# Output: "follow_up_question"

# Detect "but" pattern
result = agent.process_text_input("But wait, I need something else")
print(result.get('follow_up_type'))
# Output: "correction"
```

### 3. Conversation Analysis

```python
# Add multiple turns to conversation
agent.process_text_input("Hello")
agent.process_text_input("Show my tasks")
agent.process_text_input("Save this note")
agent.process_text_input("Show tasks again")

# Get comprehensive analysis
analysis = agent.get_conversation_analysis()

print(f"Total turns: {analysis['total_turns']}")
# Output: 4

print(f"Unique intents: {analysis['unique_intents']}")
# Output: 3

print(f"Intent distribution:")
for intent, count in analysis['intent_distribution'].items():
    print(f"  {intent}: {count}")
# Output:
#   greeting: 1
#   task_show: 2
#   note_save: 1

print(f"Detected patterns: {analysis['conversation_patterns']}")
# Output: ['starts_with_greeting', 'task_focused']

print(f"Average confidence: {analysis['avg_confidence']:.0%}")
# Output: 60%
```

### 4. Agent Insights

```python
# Get AI agent insights about the conversation
insights = agent.get_agent_insights()

print(f"Is Active: {insights['is_active']}")
# Output: True

print(f"Conversation Maturity: {insights['conversation_maturity']}")
# Output: "developing" (after 4 turns)

print(f"User Intent Clarity: {insights['user_intent_clarity']:.0%}")
# Output: 60%

print(f"Conversation Focus: {insights['conversation_focus']}")
# Output: IntentType.TASK_SHOW (most common intent)
```

### 5. Entity Extraction

```python
from patterns import EntityExtractor

extractor = EntityExtractor()

text = """
Send email to john@example.com and call me at 555-123-4567.
Let's meet tomorrow at 2pm in San Francisco.
"""

entities = extractor.extract_all_entities(text)

print(f"Emails: {entities['emails']}")
# Output: ['john@example.com']

print(f"Phones: {entities['phones']}")
# Output: ['555-123-4567']

print(f"Locations: {entities['locations']}")
# Output: ['San Francisco']

# Extract specific types
emails = extractor.extract_emails(text)
print(f"Found emails: {emails}")
```

### 6. Intent Classification with Confidence

```python
from patterns import IntentClassifier

classifier = IntentClassifier()

# Test different inputs
test_inputs = [
    "Show me my tasks",
    "Hello!",
    "Save this thought",
    "Random gibberish xyz",
]

for text in test_inputs:
    intent, confidence = classifier.classify(text)
    print(f"'{text}'")
    print(f"  Intent: {intent}, Confidence: {confidence:.0%}\n")

# Output:
# 'Show me my tasks'
#   Intent: IntentType.TASK_SHOW, Confidence: 90%
#
# 'Hello!'
#   Intent: IntentType.GREETING, Confidence: 95%
#
# 'Save this thought'
#   Intent: IntentType.NOTE_SAVE, Confidence: 85%
#
# 'Random gibberish xyz'
#   Intent: IntentType.FALLBACK, Confidence: 40%
```

## Error Handling

### 1. Handling Low Confidence

```python
result = agent.process_text_input("it")

if result.get('needs_clarification'):
    print("Agent needs clarification:")
    print(result.get('clarification_prompt'))
    # Output: "I'm not confident about your request. Could you clarify?"

# Re-ask with more detail
result2 = agent.process_text_input("Show my tasks")
if result2['success']:
    print(f"Success: {result2['response']}")
```

### 2. Handling Invalid Input

```python
# Empty input
result = agent.process_text_input("")
if not result['success']:
    print(f"Error: {result['response']}")
    # Output: "I didn't hear anything. Could you please speak again?"

# Very long input
result = agent.process_text_input("a" * 2000)
if not result['success']:
    print(f"Error: {result['response']}")
    # Output: "That was quite long. Could you rephrase more concisely?"

# Security threat (SQL injection)
result = agent.process_text_input("'; DROP TABLE users; --")
if not result['success']:
    print(f"Error: {result['response']}")
    # Output: "I couldn't process that input. Please try a different phrasing."
```

### 3. Accessing Error Information

```python
from core.error_handler import ErrorHandler

handler = ErrorHandler()

# Log errors (happens automatically in pipeline)
try:
    # Some operation
    pass
except Exception as e:
    handler.log_error(e, ErrorSeverity.HIGH, "Custom context")

# Get error summary
summary = handler.get_error_summary()
print(f"Total errors: {summary['total']}")
print(f"By severity: {summary['by_severity']}")
```

## Integration Guide

### 1. As a Library in Your Project

```python
# your_app.py
from voice_assistant.core import EnhancedVoiceAgent

def create_voice_agent():
    # Create and configure agent
    agent = EnhancedVoiceAgent(...)
    return agent

def process_user_request(agent, user_input):
    result = agent.process_text_input(user_input)
    return {
        'response': result['response'],
        'intent': str(result['intent']),
        'confidence': result['confidence'],
    }

# Use in your application
agent = create_voice_agent()
response = process_user_request(agent, "Show my tasks")
```

### 2. Building a Web API

```python
from flask import Flask, request, jsonify
from voice_assistant.core import EnhancedVoiceAgent

app = Flask(__name__)
agent = EnhancedVoiceAgent(...)

@app.route('/api/process', methods=['POST'])
def process_input():
    data = request.json
    user_input = data.get('text')
    
    result = agent.process_text_input(user_input)
    
    return jsonify({
        'success': result['success'],
        'response': result['response'],
        'intent': str(result.get('intent')),
        'confidence': result.get('confidence'),
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Building a Chat Bot

```python
from voice_assistant.core import EnhancedVoiceAgent

class ChatBot:
    def __init__(self):
        self.agent = EnhancedVoiceAgent(...)
    
    def chat(self, user_message):
        result = self.agent.process_text_input(user_message)
        
        response = {
            'message': result['response'],
            'metadata': {
                'intent': result.get('intent'),
                'confidence': result.get('confidence'),
            }
        }
        
        return response
    
    def get_conversation_context(self):
        analysis = self.agent.get_conversation_analysis()
        insights = self.agent.get_agent_insights()
        
        return {
            'analysis': analysis,
            'insights': insights,
        }

# Usage
bot = ChatBot()
response = bot.chat("What are my tasks?")
print(response['message'])
```

## Best Practices

### 1. Error Handling

```python
# ✅ Good: Handle all cases
result = agent.process_text_input(user_input)
if result['success']:
    response = result['response']
else:
    response = result.get('response', 'An error occurred')

# ❌ Bad: Assume success
response = agent.process_text_input(user_input)['response']  # May fail
```

### 2. Input Validation

```python
# ✅ Good: Validate before processing
if not user_input or len(user_input) > 1000:
    print("Invalid input")
else:
    result = agent.process_text_input(user_input)

# ✅ Good: Check result structure
if 'confidence' in result and result['confidence'] < 0.65:
    print("Low confidence, ask for clarification")
```

### 3. Memory Management

```python
# ✅ Good: Create agent once, reuse
agent = create_agent()
for user_input in user_inputs:
    result = agent.process_text_input(user_input)

# ❌ Bad: Create new agent for each input
for user_input in user_inputs:
    agent = create_agent()  # Wasteful
    result = agent.process_text_input(user_input)
```

### 4. Logging

```python
# ✅ Good: Log important information
result = agent.process_text_input(user_input)
logger.info(f"Intent: {result['intent']}, Confidence: {result['confidence']}")

# ✅ Good: Use conversation history for analysis
history = agent.get_conversation_history()
logger.info(f"Conversation turns: {len(history)}")
```

## Troubleshooting

### Common Issues

**Q: My input is not being recognized**

A: Check the confidence score. If it's below 65%, the agent flags it for clarification.
```python
result = agent.process_text_input(your_input)
print(f"Confidence: {result['confidence']:.0%}")
if result.get('needs_clarification'):
    print(f"Clarification needed: {result['clarification_prompt']}")
```

**Q: How do I add custom intents?**

A: Create a new intent handler:
```python
from intents.base_intent import BaseIntent

class CustomIntent(BaseIntent):
    def handle(self, entities, context):
        return "Your custom response"
```

**Q: How do I use real LLM instead of mock?**

A: Replace the service creation:
```python
# Instead of:
llm_service = create_llm_service(use_mock=True)

# Use:
llm_service = create_llm_service(use_mock=False, api_key="your_key")
```

**Q: Can I persist conversations to a database?**

A: Yes, replace CSVHandler with a database handler:
```python
# See storage/ module for implementing DatabaseHandler
conversation_logger = ConversationLogger(DatabaseHandler())
```

## Performance Optimization

### 1. Cache Agent Instance

```python
# Create once at startup
agent = create_agent()

# Reuse for all requests
def handle_request(user_input):
    return agent.process_text_input(user_input)
```

### 2. Use Text Input for Testing

```python
# Faster (no audio processing)
result = agent.process_text_input("Test input")

# Instead of:
result = agent.process_voice_input(5.0)  # Records audio
```

### 3. Monitor Performance

```python
import time

start = time.time()
result = agent.process_text_input(user_input)
duration = time.time() - start

print(f"Processing time: {duration:.3f}s")
```

---

**Need more help?** Check [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation.

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
