"""Tests for error handling and validation"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.error_handler import (
    InputValidator, ErrorHandler, FallbackResponseGenerator,
    EdgeCaseHandler, ErrorSeverity, InputValidationError
)


def test_input_validator_text():
    """Test text input validation"""
    print("Testing text input validation...")

    # Valid input
    result = InputValidator.validate_text_input("Hello world")
    assert result['valid'], f"Valid input rejected: {result['errors']}"
    assert result['cleaned'] == "Hello world"
    print("✅ Valid text input accepted")

    # Empty input
    result = InputValidator.validate_text_input("")
    assert not result['valid'], "Empty input should be invalid"
    assert len(result['errors']) > 0
    print("✅ Empty input rejected")

    # Too long
    result = InputValidator.validate_text_input("a" * 1001)
    assert not result['valid'], "Too long input should be invalid"
    print("✅ Long input rejected")

    # Too short
    result = InputValidator.validate_text_input("")
    assert not result['valid'], "Too short input should be invalid"
    print("✅ Short input rejected")

    # SQL injection pattern
    result = InputValidator.validate_text_input("'; DROP TABLE users; --")
    assert not result['valid'], "SQL injection should be detected"
    print("✅ SQL injection detected")

    # Script injection
    result = InputValidator.validate_text_input("<script>alert('xss')</script>")
    assert not result['valid'], "Script injection should be detected"
    print("✅ Script injection detected")

    print("✅ Text validation test passed\n")


def test_audio_duration_validation():
    """Test audio duration validation"""
    print("Testing audio duration validation...")

    # Valid duration
    result = InputValidator.validate_audio_duration(5.0)
    assert result['valid'], f"Valid duration rejected: {result['errors']}"
    print("✅ Valid duration accepted")

    # Too short
    result = InputValidator.validate_audio_duration(0.1)
    assert not result['valid'], "Too short duration should be invalid"
    print("✅ Too short duration rejected")

    # Too long
    result = InputValidator.validate_audio_duration(400)
    assert not result['valid'], "Too long duration should be invalid"
    print("✅ Too long duration rejected")

    # Negative
    result = InputValidator.validate_audio_duration(-5)
    assert not result['valid'], "Negative duration should be invalid"
    print("✅ Negative duration rejected")

    # Invalid type
    result = InputValidator.validate_audio_duration("not a number")
    assert not result['valid'], "Non-numeric duration should be invalid"
    print("✅ Non-numeric duration rejected")

    print("✅ Audio duration validation test passed\n")


def test_confidence_validation():
    """Test confidence score validation"""
    print("Testing confidence score validation...")

    # Valid scores
    for score in [0.0, 0.5, 1.0]:
        result = InputValidator.validate_confidence_score(score)
        assert result['valid'], f"Valid score {score} rejected"
    print("✅ Valid confidence scores accepted")

    # Invalid scores
    for score in [-0.1, 1.5, 2.0]:
        result = InputValidator.validate_confidence_score(score)
        assert not result['valid'], f"Invalid score {score} accepted"
    print("✅ Invalid confidence scores rejected")

    # Non-numeric
    result = InputValidator.validate_confidence_score("high")
    assert not result['valid'], "Non-numeric score should be invalid"
    print("✅ Non-numeric score rejected")

    print("✅ Confidence validation test passed\n")


def test_error_handler():
    """Test error handler"""
    print("Testing error handler...")

    handler = ErrorHandler()

    # Log an error
    error = ValueError("Test error")
    record = handler.log_error(error, ErrorSeverity.MEDIUM, "Test context")

    assert record['type'] == 'ValueError'
    assert 'Test error' in record['message']
    assert record['severity'] == 'medium'
    print("✅ Error logged correctly")

    # Check history
    summary = handler.get_error_summary()
    assert summary['total'] == 1
    print("✅ Error history tracked")

    print("✅ Error handler test passed\n")


def test_fallback_responses():
    """Test fallback response generation"""
    print("Testing fallback response generation...")

    # Input error response
    response = FallbackResponseGenerator.generate_input_error_response(['empty'])
    assert len(response) > 0
    assert 'hear' in response.lower() or 'input' in response.lower()
    print("✅ Input error response generated")

    # Processing error response
    response = FallbackResponseGenerator.generate_processing_error_response('intent')
    assert len(response) > 0
    print("✅ Processing error response generated")

    # Low confidence response
    response = FallbackResponseGenerator.generate_confidence_response(0.4)
    assert len(response) > 0
    print("✅ Low confidence response generated")

    # Generic recovery
    response = FallbackResponseGenerator.generate_generic_recovery_response()
    assert len(response) > 0
    print("✅ Generic recovery response generated")

    print("✅ Fallback response test passed\n")


def test_edge_case_handler():
    """Test edge case handling"""
    print("Testing edge case handler...")

    # Empty result
    result = EdgeCaseHandler.handle_empty_result("test input")
    assert not result['success']
    assert result['user_input'] == "test input"
    assert len(result['response']) > 0
    print("✅ Empty result handled")

    # None intent
    result = EdgeCaseHandler.handle_none_intent("test input")
    assert not result['success']
    assert result['intent'] is None
    print("✅ None intent handled")

    # Missing confidence
    result = {'confidence': None}
    result = EdgeCaseHandler.handle_missing_confidence(result)
    assert result['confidence'] == 0.5
    assert result['confidence_warning'] is True
    print("✅ Missing confidence handled")

    # Null entities
    result = {}
    result = EdgeCaseHandler.handle_null_entities(result)
    assert 'entities' in result
    assert result['entities'] == {}
    print("✅ Null entities handled")

    # Validate result structure
    incomplete_result = {'success': True}
    complete_result = EdgeCaseHandler.validate_result_structure(incomplete_result)
    assert 'intent' in complete_result
    assert 'response' in complete_result
    assert 'confidence' in complete_result
    print("✅ Result structure validated")

    print("✅ Edge case handler test passed\n")


def test_malformed_response_recovery():
    """Test recovery from malformed responses"""
    print("Testing malformed response recovery...")

    result = EdgeCaseHandler.handle_malformed_response("test", Exception("test error"))
    assert not result['success']
    assert result['user_input'] == "test"
    assert len(result['response']) > 0
    print("✅ Malformed response handled")

    print("✅ Malformed response recovery test passed\n")


def test_timeout_recovery():
    """Test recovery from timeouts"""
    print("Testing timeout recovery...")

    result = EdgeCaseHandler.handle_service_timeout("test", 5.0)
    assert not result['success']
    assert result['timeout'] is True
    assert len(result['response']) > 0
    print("✅ Timeout handled")

    print("✅ Timeout recovery test passed\n")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🛡️  ERROR HANDLING AND VALIDATION TESTS")
    print("="*70 + "\n")

    try:
        test_input_validator_text()
        test_audio_duration_validation()
        test_confidence_validation()
        test_error_handler()
        test_fallback_responses()
        test_edge_case_handler()
        test_malformed_response_recovery()
        test_timeout_recovery()

        print("="*70)
        print("✅ ALL ERROR HANDLING TESTS PASSED!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
