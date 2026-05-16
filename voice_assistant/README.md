# Voice Assistant CLI

Core implementation of the Voice Agentic AI Assistant. This directory contains the main application logic and pipeline.

## 🚀 Live Demo

**Try it now:** [mphasis-voice-agentic-ai-assistant.streamlit.app](https://mphasis-voice-agentic-ai-assistant.streamlit.app)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit UI (recommended)
streamlit run ui/streamlit_app.py

# OR run the interactive CLI
python3 main.py
```

Choose from:
1. **Voice Input** - Speak into your microphone
2. **Text Input** - Type messages (recommended for testing)
3. **View Statistics** - See intent breakdown and conversation stats
4. **View History** - See all conversation turns
5. **View Agent Insights** - AI analysis of conversation quality
6. **View Conversation Analysis** - Detailed conversation patterns

## Project Structure

```
voice_assistant/
├── main.py                          # CLI entry point
├── core/                            # Agent orchestration
│   ├── agent.py                     # Base agent
│   ├── enhanced_agent.py            # Advanced agentic features
│   └── error_handler.py             # Error handling & recovery
├── pipeline/                        # Processing pipeline
│   ├── pipeline_stages.py           # 6 atomic pipeline stages
│   └── base.py                      # Base stage class
├── patterns/                        # Pattern recognition
│   ├── intent_classifier.py         # Intent classification (6 types)
│   ├── entity_extractor.py          # Entity extraction (11 types)
│   └── regex_library.py             # Regex patterns
├── services/                        # External service wrappers
│   ├── llm_service.py               # Gemini LLM integration
│   ├── speech_service.py            # Speech recognition
│   └── audio_service.py             # Audio I/O
├── storage/                         # Data persistence
│   ├── csv_handler.py               # CSV file handling
│   └── conversation_logger.py       # Conversation logging
├── intents/                         # Intent handlers
│   ├── base_intent.py               # Base handler class
│   └── [intent handlers]
├── config/                          # Configuration
│   ├── settings.py                  # Environment settings
│   └── constants.py                 # Constants & enums
├── tests/                           # Test suite
│   ├── test_enhanced_agent.py       # Enhanced agent tests
│   ├── test_error_handler.py        # Error handling tests
│   └── test_error_edge_cases.py     # Edge case tests
├── test_real_api.py                 # Real API integration tests
├── QUICK_START.md                   # 5-minute getting started guide
├── CONTRIBUTING.md                  # Development guide
└── USAGE_GUIDE.md                   # Detailed usage examples
```

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage examples and integrations
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and contribution guide
- **[../docs/guides/ARCHITECTURE.md](../docs/guides/ARCHITECTURE.md)** - System design
- **[../docs/guides/API_REFERENCE.md](../docs/guides/API_REFERENCE.md)** - Complete API docs
- **[../docs/guides/TEST_RESULTS.md](../docs/guides/TEST_RESULTS.md)** - Test results

For complete documentation index, see **[../docs/INDEX.md](../docs/INDEX.md)**

## Testing

```bash
# Run enhanced agent tests
python3 tests/test_enhanced_agent.py

# Run error handling tests  
python3 tests/test_error_handler.py

# Run edge case tests
python3 tests/test_error_edge_cases.py

# Run real API tests (requires GEMINI_API_KEY)
python3 test_real_api.py
```

All tests pass: **71+ test cases** with 100% success rate

## Key Features

### Agentic Behavior
- Context-aware responses
- Follow-up pattern detection (10+ patterns)
- Smart intent routing
- Auto clarification generation
- Conversation analytics

### Security & Reliability
- Input validation at all boundaries
- SQL/XSS injection prevention
- Graceful error recovery (7+ strategies)
- Zero unhandled exceptions
- Comprehensive logging

### Production Ready
- Multi-turn conversations with context
- 6 intent types with confidence scoring
- 11 entity types (emails, phones, dates, URLs, etc.)
- CSV-based conversation storage
- Real-time voice processing

## Configuration

Edit `config/settings.py` to customize:
- LLM model (currently: `gemini-2.5-flash`)
- Temperature and max tokens
- Speech recognition engine
- Text-to-speech settings
- Context window size

See **[../README.md](../README.md)** for full project documentation.
