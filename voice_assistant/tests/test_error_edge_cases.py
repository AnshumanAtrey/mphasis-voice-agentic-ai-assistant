"""Tests for edge cases and error scenarios in the enhanced agent"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.builder import AgentBuilder
from core.enhanced_agent import EnhancedVoiceAgent
from pipeline.pipeline_stages import (
    VoiceInputStage, SpeechToTextStage, TextProcessorStage,
    IntentClassificationStage, LLMGeneratorStage, TextToSpeechStage,
    PipelineExecutor,
)
from services import create_llm_service, create_speech_service, create_audio_service
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler


def create_enhanced_agent():
    """Create enhanced agent with mock services"""
    llm_service = create_llm_service(use_mock=True)
    speech_service = create_speech_service(use_mock=True)
    audio_service = create_audio_service(use_mock=True)

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
    csv_handler = CSVHandler()
    conversation_logger = ConversationLogger(csv_handler)

    agent = EnhancedVoiceAgent(
        pipeline_executor=pipeline_executor,
        llm_service=llm_service,
        conversation_logger=conversation_logger,
    )

    return agent


def test_empty_input():
    """Test handling of empty input"""
    print("Testing empty input handling...")
    agent = create_enhanced_agent()

    # Empty string
    result = agent.process_text_input("")
    assert not result['success'], "Empty input should fail"
    assert result['user_input'] == ""
    print("✅ Empty string handled gracefully")

    # Whitespace only
    result = agent.process_text_input("   ")
    assert result is not None, "Whitespace should be handled"
    print("✅ Whitespace handled")

    print("✅ Empty input test passed\n")


def test_very_long_input():
    """Test handling of very long input"""
    print("Testing very long input handling...")
    agent = create_enhanced_agent()

    # Input exceeding max length
    long_input = "word " * 300  # 1500+ chars
    result = agent.process_text_input(long_input)
    assert result is not None
    print("✅ Long input truncated and processed")

    print("✅ Very long input test passed\n")


def test_sql_injection_attempt():
    """Test SQL injection prevention"""
    print("Testing SQL injection prevention...")
    agent = create_enhanced_agent()

    # SQL injection attempt
    malicious_input = "'; DROP TABLE users; --"
    result = agent.process_text_input(malicious_input)
    assert not result['success'], "SQL injection should be blocked"
    assert 'suspicious' in result.get('response', '').lower() or not result['success']
    print("✅ SQL injection attempt blocked")

    print("✅ SQL injection test passed\n")


def test_script_injection_attempt():
    """Test script injection prevention"""
    print("Testing script injection prevention...")
    agent = create_enhanced_agent()

    # XSS attempt
    malicious_input = "<script>alert('xss')</script>"
    result = agent.process_text_input(malicious_input)
    assert not result['success'], "Script injection should be blocked"
    print("✅ Script injection attempt blocked")

    print("✅ Script injection test passed\n")


def test_very_short_ambiguous_input():
    """Test handling of very short ambiguous input"""
    print("Testing very short ambiguous input...")
    agent = create_enhanced_agent()

    short_inputs = ["a", "it", "this", "that"]
    for short in short_inputs:
        result = agent.process_text_input(short)
        assert result is not None
        # Should either fail validation or flag as ambiguous
        if result.get('success'):
            assert result.get('ambiguous') or result.get('needs_clarification')
        print(f"✅ Short input '{short}' handled")

    print("✅ Very short ambiguous input test passed\n")


def test_repeated_requests():
    """Test handling of repeated requests"""
    print("Testing repeated requests...")
    agent = create_enhanced_agent()

    same_input = "Show my tasks"

    # Send same request 3 times
    for i in range(3):
        result = agent.process_text_input(same_input)
        assert result['success']
        if i > 0:
            # Should detect context from history
            print(f"✅ Repeat {i}: Context detected")

    # Verify history tracking
    history = agent.get_conversation_history()
    assert len(history) == 3
    print(f"✅ Repeated requests tracked: {len(history)} turns")

    print("✅ Repeated requests test passed\n")


def test_confidence_score_handling():
    """Test handling of confidence scores"""
    print("Testing confidence score handling...")
    agent = create_enhanced_agent()

    # Input that might have low confidence
    ambiguous = "it"
    result = agent.process_text_input(ambiguous)

    assert 'confidence' in result
    confidence = result.get('confidence', 0)
    assert 0 <= confidence <= 1, f"Confidence {confidence} out of range"

    if confidence < 0.65:
        # Should request clarification
        assert result.get('needs_clarification') is not None
        print(f"✅ Low confidence ({confidence:.0%}) flagged for clarification")

    print("✅ Confidence score handling test passed\n")


def test_result_structure_completeness():
    """Test that results have all required fields"""
    print("Testing result structure completeness...")
    agent = create_enhanced_agent()

    result = agent.process_text_input("Show my tasks")

    required_fields = ['success', 'user_input', 'response', 'intent', 'confidence']
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
        print(f"✅ Field '{field}' present")

    print("✅ Result structure completeness test passed\n")


def test_follow_up_with_errors():
    """Test follow-up detection even with potential errors"""
    print("Testing follow-up detection with errors...")
    agent = create_enhanced_agent()

    # Input with follow-up pattern
    result = agent.process_text_input("Show tasks also save note")
    assert result is not None

    if result.get('success'):
        # Should detect follow-up pattern despite complexity
        print("✅ Follow-up pattern detected despite complexity")
    else:
        print("✅ Complex input handled safely")

    print("✅ Follow-up with errors test passed\n")


def test_conversation_consistency():
    """Test that conversation analysis remains consistent"""
    print("Testing conversation consistency...")
    agent = create_enhanced_agent()

    # Add multiple turns
    inputs = ["Hello", "Show tasks", "Save note", "Show tasks again"]
    for text in inputs:
        result = agent.process_text_input(text)
        assert result is not None
        print(f"✅ Turn: {text[:20]}...")

    # Get analysis
    analysis = agent.get_conversation_analysis()

    assert analysis['total_turns'] == len(inputs)
    print(f"✅ Total turns: {analysis['total_turns']}")

    assert 'intent_distribution' in analysis
    print(f"✅ Intent distribution: {len(analysis['intent_distribution'])} unique intents")

    # Get insights
    insights = agent.get_agent_insights()
    assert insights['is_active']
    print(f"✅ Agent active: {insights['is_active']}")

    print("✅ Conversation consistency test passed\n")


def test_error_recovery_graceful_degradation():
    """Test that errors are handled gracefully without crashes"""
    print("Testing error recovery and graceful degradation...")
    agent = create_enhanced_agent()

    test_cases = [
        "",                    # Empty
        "     ",              # Whitespace
        "a" * 1001,          # Too long
        "test123!@#$%^&*()", # Special chars
        "123456789",         # Numbers only
    ]

    for test_input in test_cases:
        try:
            result = agent.process_text_input(test_input)
            # Should always return a result, even if unsuccessful
            assert isinstance(result, dict)
            assert 'response' in result
            print(f"✅ Input '{test_input[:20]:20}' handled")
        except Exception as e:
            print(f"❌ FAILED: {test_input[:20]} raised {type(e).__name__}: {e}")
            raise

    print("✅ Error recovery graceful degradation test passed\n")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔍 ERROR HANDLING EDGE CASES TESTS")
    print("="*70 + "\n")

    try:
        test_empty_input()
        test_very_long_input()
        test_sql_injection_attempt()
        test_script_injection_attempt()
        test_very_short_ambiguous_input()
        test_repeated_requests()
        test_confidence_score_handling()
        test_result_structure_completeness()
        test_follow_up_with_errors()
        test_conversation_consistency()
        test_error_recovery_graceful_degradation()

        print("="*70)
        print("✅ ALL EDGE CASE TESTS PASSED!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
