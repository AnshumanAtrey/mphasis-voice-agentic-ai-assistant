# 🤝 Contributing Guide

Thank you for your interest in contributing to the Voice Agentic AI Assistant! This guide will help you get started.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/mphasis-voice-agentic-ai-assistant.git
cd mphasis-voice-agentic-ai-assistant
```

### 2. Set Up Development Environment

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# No additional packages needed - uses only Python stdlib
```

### 3. Run Tests Locally

```bash
cd voice_assistant

# Run all tests
python3 tests/test_enhanced_agent.py
python3 tests/test_error_handler.py
python3 tests/test_error_edge_cases.py

# All should pass before making changes
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Follow the code style and patterns established in the project:

- Use descriptive variable names
- Add docstrings to functions/classes
- Keep functions small and focused
- Add type hints where applicable

### 3. Add Tests

For any new feature or fix, add corresponding tests:

```python
# Add to appropriate test file
def test_your_feature():
    """Test description"""
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
    print("✅ Your feature test passed")
```

### 4. Run Tests

```bash
# Make sure all tests pass
python3 tests/test_enhanced_agent.py
python3 tests/test_error_handler.py
python3 tests/test_error_edge_cases.py

# Expected output: ✅ ALL TESTS PASSED
```

### 5. Commit Changes

```bash
# Stage your changes
git add .

# Commit with clear message
git commit -m "feature: Add new functionality

- Add feature X
- Improve Y
- Fix bug Z

Tests: All 71 tests passing"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub with:
# - Clear title
# - Description of changes
# - Reference to related issues
```

## Code Style Guide

### Naming Conventions

```python
# Classes: PascalCase
class EnhancedVoiceAgent:
    pass

# Functions/variables: snake_case
def process_text_input(text):
    user_input = text
    return user_input

# Constants: UPPER_SNAKE_CASE
MAX_INPUT_LENGTH = 1000
DEFAULT_CONFIDENCE = 0.5

# Private members: _leading_underscore
def _internal_helper():
    pass
```

### Documentation

```python
def process_text_input(text: str) -> Dict[str, Any]:
    """
    Process text input and generate response.
    
    Args:
        text: User input text
    
    Returns:
        Dictionary with keys:
        - success: bool
        - response: str
        - intent: IntentType
        - confidence: float
    
    Raises:
        ValueError: If input is invalid
    """
    # Implementation
    pass
```

### Type Hints

```python
# Use type hints for clarity
def classify(text: str) -> Tuple[IntentType, float]:
    pass

def process_input(data: Dict[str, Any]) -> Optional[str]:
    pass

def log_errors(errors: List[str]) -> None:
    pass
```

## Areas to Contribute

### 1. New Intent Handlers

Create new intent handlers in `intents/`:

```python
# intents/custom_intent.py
from intents.base_intent import BaseIntent

class CustomIntent(BaseIntent):
    def handle(self, entities: Dict, context: ConversationContext) -> str:
        """Handle custom intent"""
        # Your implementation
        return response
```

Then:
1. Add to `IntentType` enum in `config/constants.py`
2. Add detection pattern to `patterns/intent_classifier.py`
3. Add tests in `tests/test_patterns.py`

### 2. New Entity Types

Add to entity extraction:

```python
# In patterns/regex_library.py
CUSTOM_ENTITY = r'pattern_here'

# In patterns/entity_extractor.py
def extract_custom_entities(text: str) -> List[str]:
    return regex.findall(CUSTOM_ENTITY, text)
```

Then add tests.

### 3. Error Handling Improvements

Enhance error handling in `core/error_handler.py`:

```python
# Add new validator
class InputValidator:
    @staticmethod
    def validate_custom_format(data):
        # Your validation logic
        return {'valid': bool, 'errors': list}
```

### 4. Performance Optimizations

- Profile code to identify bottlenecks
- Optimize regex patterns
- Improve pipeline stage efficiency
- Cache frequently computed values

### 5. Documentation

- Improve README clarity
- Add more examples
- Document architecture decisions
- Create troubleshooting guides

## Testing Requirements

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange - Set up test data
    test_input = "test data"
    expected = "expected output"
    
    # Act - Call the function
    result = function_under_test(test_input)
    
    # Assert - Verify result
    assert result == expected
    print("✅ Test passed")
```

### Coverage Guidelines

- **New Feature**: Add 3+ tests (happy path, edge cases, error cases)
- **Bug Fix**: Add test that reproduces bug, then fix
- **Refactor**: Keep existing tests passing

### Running Specific Tests

```bash
# Run one test file
python3 tests/test_enhanced_agent.py

# Run specific test function (manual)
# Edit test file to run only that function, then:
python3 tests/test_error_handler.py
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Code follows style guide
3. ✅ Docstrings added
4. ✅ No breaking changes
5. ✅ Commit messages are clear

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Enhancement
- [ ] Documentation

## Testing
- [ ] Added tests
- [ ] All tests pass
- [ ] Tested locally

## Checklist
- [ ] Code style followed
- [ ] Docstrings added
- [ ] No breaking changes
```

## Common Contribution Types

### 1. Adding a New Intent

```
1. Create intents/your_intent.py
2. Add IntentType enum value
3. Add regex pattern to regex_library.py
4. Update intent_classifier.py
5. Add tests
6. Document in USAGE_GUIDE.md
```

### 2. Fixing a Bug

```
1. Create test that reproduces bug
2. Verify test fails
3. Fix the bug
4. Verify test passes
5. Run all tests
6. Commit with clear message
```

### 3. Performance Improvement

```
1. Document baseline performance
2. Make changes
3. Benchmark improvements
4. Add tests if applicable
5. Document in PR
```

### 4. Documentation

```
1. Update relevant .md files
2. Add code examples
3. Ensure clarity
4. Run spell check
5. Review before submitting
```

## Questions?

### Finding Help

- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review [USAGE_GUIDE.md](USAGE_GUIDE.md) for examples
- Look at existing tests for patterns
- Check issue tracker for discussions

### Communication

- Open an issue to discuss major changes
- Provide context and rationale
- Link related issues/PRs
- Be respectful and collaborative

## Development Tips

### Local Testing Workflow

```bash
# 1. Make changes
# 2. Run tests
python3 tests/test_*.py

# 3. Check specific functionality
python3 -c "
from core.enhanced_agent import EnhancedVoiceAgent
# Quick test here
"

# 4. Run the app
python3 main.py

# 5. Commit when satisfied
git add .
git commit -m 'description'
```

### Debugging Tips

```python
# Add debugging
import sys
print(f"DEBUG: {variable}", file=sys.stderr)

# Run with logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test specific component
from patterns import IntentClassifier
classifier = IntentClassifier()
intent, conf = classifier.classify("test")
print(f"Intent: {intent}, Confidence: {conf}")
```

### Performance Profiling

```python
import time

start = time.time()
# Code to profile
duration = time.time() - start
print(f"Duration: {duration:.3f}s")
```

## Code Review Guidelines

When your PR is reviewed:

- Be open to feedback
- Ask clarifying questions
- Make requested changes
- Re-test after changes
- Communicate clearly

## Recognition

Contributors are recognized in:
- Git commit history
- Project documentation
- GitHub contributors list

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make the Voice Agentic AI Assistant better for everyone. Thank you for participating! 🎉

---

**Questions about contributing?**
- Review this guide thoroughly
- Check existing PRs for examples
- Open an issue to discuss
- Be respectful and collaborative

**Happy contributing!** ✨
