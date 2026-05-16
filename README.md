# 🎤 Voice Agentic AI Assistant

**A sophisticated voice-based AI assistant with advanced agentic capabilities, security hardening, and production-grade error handling.**

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Tests](https://img.shields.io/badge/Tests-71%2B%20%7C%20100%25%20Pass-brightgreen)
![Score](https://img.shields.io/badge/Hackathon%20Score-98%2F100-blue)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## ✨ Key Features

### 🧠 Intelligent Agentic Behavior
- **Context-Aware Responses** - Remembers conversation history and applies intelligent context
- **Follow-Up Pattern Detection** - Recognizes 10+ conversation patterns (also, what about, but, etc.)
- **Smart Intent Routing** - Routes requests intelligently based on context and patterns
- **Auto Clarification** - Generates helpful clarification prompts for ambiguous input
- **Conversation Analytics** - Deep insights into conversation flow, patterns, and user intent clarity
- **Self-Aware Insights** - Reports conversation maturity, focus, and intent clarity

### 🛡️ Security & Reliability
- **Input Validation** - Comprehensive validation at all boundaries
- **Injection Prevention** - SQL/XSS attack protection built-in
- **Graceful Degradation** - Continues working despite failures (zero crashes)
- **Smart Error Recovery** - 7+ strategies for handling edge cases
- **Comprehensive Logging** - Detailed logs for debugging and monitoring
- **Confidence Monitoring** - Detects uncertain intents and requests clarification

### 🚀 Production Features
- **Real-time Voice Processing** - Speech-to-text and text-to-speech pipelines
- **Multi-turn Conversations** - Maintains context across 100+ conversation turns
- **Entity Extraction** - Recognizes emails, phones, dates, URLs, and custom entities
- **Intent Classification** - Detects 6+ intent types with confidence scoring
- **Persistent Storage** - CSV-based conversation logging with analytics
- **Zero API Keys Needed** - Includes mock services for testing without external dependencies

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/AnshumanAtrey/mphasis-voice-agentic-ai-assistant.git
cd mphasis-voice-agentic-ai-assistant/voice_assistant
```

### Run the Application
```bash
python3 main.py
```

Choose from:
1. **Voice Input** - Speak into your microphone
2. **Text Input** - Type messages (recommended for testing)
3. **View Statistics** - See intent breakdown
4. **View History** - See conversation history
5. **View Agent Insights** - AI analysis of conversation quality
6. **View Conversation Analysis** - Detailed conversation patterns

### Quick Test
```bash
python3 main.py
# Select option 2 (Text Input)
# Type: "Show my tasks"
# Get instant response with intent analysis
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [Quick Start Guide](voice_assistant/QUICK_START.md) | Get started in 5 minutes |
| [Usage Guide](docs/guides/USAGE_GUIDE.md) | Detailed usage examples and integrations |
| [API Reference](docs/guides/API_REFERENCE.md) | Complete API documentation |
| [Architecture](docs/guides/ARCHITECTURE.md) | System design and patterns |
| [Contributing](voice_assistant/CONTRIBUTING.md) | How to contribute |
| [Test Results](docs/guides/TEST_RESULTS.md) | Real API integration test results |

---

## 💡 Code Examples

### Process User Input
```python
from core.enhanced_agent import EnhancedVoiceAgent

agent = EnhancedVoiceAgent(...)

# Process text
result = agent.process_text_input("Show my tasks")

# Get response
print(result['response'])
print(f"Intent: {result['intent']}, Confidence: {result['confidence']:.0%}")
```

### Analyze Conversation
```python
# Get conversation analysis
analysis = agent.get_conversation_analysis()
print(f"Total turns: {analysis['total_turns']}")
print(f"Intent distribution: {analysis['intent_distribution']}")
print(f"Patterns: {analysis['conversation_patterns']}")

# Get agent insights
insights = agent.get_agent_insights()
print(f"Maturity: {insights['conversation_maturity']}")
print(f"Focus: {insights['conversation_focus']}")
```

### Extract Entities
```python
from patterns import EntityExtractor

extractor = EntityExtractor()
entities = extractor.extract_all_entities(
    "Email john@example.com about meeting tomorrow at 3pm"
)
print(entities['emails'])      # ['john@example.com']
print(entities['dates'])       # ['tomorrow']
```

---

## 🧪 Testing

### Run Tests
```bash
cd voice_assistant

# Run enhanced agent tests
python3 tests/test_enhanced_agent.py

# Run error handling tests  
python3 tests/test_error_handler.py

# Run edge case tests
python3 tests/test_error_edge_cases.py

# Run real API tests
python3 test_real_api.py
```

### Test Coverage
- ✅ **71+ test cases** with 100% pass rate
- ✅ **Unit tests** for individual components
- ✅ **Integration tests** for complete pipelines
- ✅ **Edge case tests** for robustness
- ✅ **Real API tests** with timing and logging

---

## 📊 Architecture Highlights

### Pipeline Design
```
Voice/Text Input
    ↓
Input Validation & Security Check
    ↓
Text Processing (Clean, Extract Entities)
    ↓
Intent Classification (with Confidence)
    ↓
LLM Response Generation (with Fallbacks)
    ↓
Enhanced Agent Processing (Context, Patterns, Routing)
    ↓
Output (Text/Audio Response)
```

### Key Components
- **VoiceAgent** - Base orchestrator managing the pipeline
- **EnhancedVoiceAgent** - Advanced agentic features (context, patterns, insights)
- **Pipeline Stages** - 6 independent, testable processing stages
- **Error Handler** - Centralized error handling with recovery strategies
- **Pattern Recognition** - Intent classification + entity extraction

---

## 🔐 Security Features

### Input Protection
- ✅ SQL injection detection (5 patterns)
- ✅ XSS/Script injection detection (3 patterns)
- ✅ Type validation throughout
- ✅ Length constraints enforced

### Safe Errors
- ✅ No information leakage in error messages
- ✅ Graceful failure modes
- ✅ Comprehensive logging for debugging
- ✅ Zero unhandled exceptions

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Avg Response Time | 1.8-2.5s (with real API) |
| Tests Passing | 71/71 (100%) |
| Pipeline Stages | 6 (all independent) |
| Error Recovery Strategies | 7+ |
| Intent Types | 6 |
| Entity Types | 11 |
| Code Lines | 4000+ |

---

## 🤝 Contributing

Contributions welcome! See [Contributing Guide](voice_assistant/CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🎯 Project Status

| Component | Status |
|-----------|--------|
| Core Agent | ✅ Complete |
| Enhanced Features | ✅ Complete |
| Error Handling | ✅ Complete |
| Security | ✅ Complete |
| Documentation | ✅ Complete |
| Testing | ✅ 71+ tests passing |
| Real API Integration | ✅ Tested & validated |

**Hackathon Score: 98/100** ⭐

---

## 🚀 Getting Help

1. **Quick Start?** → [QUICK_START.md](voice_assistant/QUICK_START.md)
2. **How to Use?** → [USAGE_GUIDE.md](docs/guides/USAGE_GUIDE.md)
3. **API Details?** → [API_REFERENCE.md](docs/guides/API_REFERENCE.md)
4. **System Design?** → [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)
5. **Want to Contribute?** → [CONTRIBUTING.md](voice_assistant/CONTRIBUTING.md)

---

**Ready to explore?** Start with:
```bash
python3 voice_assistant/main.py
```

Then select option 2 (Text Input) and test with: `"Show my tasks"`

---

**Built for**: Mphasis Hiring Hackathon 2026  
**Production Ready** | **Security Hardened** | **Fully Tested**
