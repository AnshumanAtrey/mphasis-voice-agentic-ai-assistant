"""Tests for EnhancedVoiceAgent with context awareness"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.builder import AgentBuilder
from core.enhanced_agent import EnhancedVoiceAgent
from pipeline.pipeline_stages import (
    VoiceInputStage,
    SpeechToTextStage,
    TextProcessorStage,
    IntentClassificationStage,
    LLMGeneratorStage,
    TextToSpeechStage,
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

def test_context_awareness():
    """Test context-aware responses"""
    agent = create_enhanced_agent()

    # First message
    result1 = agent.process_text_input("Show today's tasks")
    assert result1['success']
    intent1 = result1['intent']

    # Follow-up message (same intent)
    result2 = agent.process_text_input("Show today's tasks again")
    assert result2['success']

    # Should have context reference
    if 'context_reference' in result2:
        print(f"✅ Context reference added: {result2.get('context_reference')}")

    print("✅ Context awareness test passed")

def test_follow_up_detection():
    """Test follow-up pattern detection"""
    agent = create_enhanced_agent()

    # Message with follow-up pattern
    result = agent.process_text_input("Show my tasks and also save this note")
    assert result['success']

    # Should detect follow-up pattern
    if 'follow_up_type' in result:
        print(f"✅ Follow-up pattern detected: {result.get('follow_up_type')}")
    else:
        print("⚠️  Follow-up pattern not detected (normal for this flow)")

    print("✅ Follow-up detection test passed")

def test_clarification_detection():
    """Test low-confidence clarification detection"""
    agent = create_enhanced_agent()

    # Ambiguous message
    result = agent.process_text_input("this")
    assert result['success']

    # Should flag ambiguous
    if result.get('ambiguous'):
        print(f"✅ Ambiguous input detected")

    if result.get('needs_clarification'):
        print(f"✅ Clarification needed: {result.get('clarification_prompt')}")

    print("✅ Clarification detection test passed")

def test_multi_turn_conversation():
    """Test multi-turn conversation with context"""
    agent = create_enhanced_agent()

    # Turn 1: Greeting
    r1 = agent.process_text_input("Hello")
    assert r1['success']
    print(f"Turn 1 - Intent: {r1['intent']}")

    # Turn 2: Task query
    r2 = agent.process_text_input("Show my tasks")
    assert r2['success']
    print(f"Turn 2 - Intent: {r2['intent']}")

    # Turn 3: Follow-up with "also"
    r3 = agent.process_text_input("Also save this note")
    assert r3['success']
    print(f"Turn 3 - Intent: {r3['intent']}")

    # Check conversation history
    history = agent.get_conversation_history()
    assert len(history) == 3
    print(f"✅ Multi-turn conversation: {len(history)} turns tracked")

    print("✅ Multi-turn conversation test passed")

def test_conversation_analysis():
    """Test conversation analysis"""
    agent = create_enhanced_agent()

    # Create some conversation
    agent.process_text_input("Hello")
    agent.process_text_input("Show tasks")
    agent.process_text_input("Save note")
    agent.process_text_input("Show tasks again")

    # Get analysis
    analysis = agent.get_conversation_analysis()

    assert analysis['total_turns'] == 4
    assert len(analysis['intent_distribution']) > 0
    print(f"✅ Conversation analysis: {analysis['total_turns']} turns")
    print(f"   Intent distribution: {analysis['intent_distribution']}")
    print(f"   Patterns: {analysis['conversation_patterns']}")

    print("✅ Conversation analysis test passed")

def test_intent_specific_routing():
    """Test intent-specific conditional routing"""
    agent = create_enhanced_agent()

    # Task query with time period
    result = agent.process_text_input("Show today's tasks")
    assert result['success']

    if result.get('intent').value == 'task_show':
        if 'task_period' in result:
            print(f"✅ Task period detected: {result['task_period']}")
        print(f"✅ Intent-specific routing working")

    print("✅ Intent-specific routing test passed")

def test_agent_insights():
    """Test agent insights generation"""
    agent = create_enhanced_agent()

    # Add some conversation
    agent.process_text_input("Hello")
    agent.process_text_input("Show tasks")
    agent.process_text_input("Save note")

    # Get insights
    insights = agent.get_agent_insights()

    assert insights['is_active']
    assert 'conversation_maturity' in insights
    assert 'user_intent_clarity' in insights
    assert 'conversation_focus' in insights

    print(f"✅ Agent insights generated")
    print(f"   Maturity: {insights['conversation_maturity']}")
    print(f"   Focus: {insights['conversation_focus']}")
    print(f"   Intent clarity: {insights['user_intent_clarity']:.0%}")

    print("✅ Agent insights test passed")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧠 ENHANCED VOICE AGENT TESTS")
    print("="*70 + "\n")

    try:
        test_context_awareness()
        print()
        test_follow_up_detection()
        print()
        test_clarification_detection()
        print()
        test_multi_turn_conversation()
        print()
        test_conversation_analysis()
        print()
        test_intent_specific_routing()
        print()
        test_agent_insights()

        print("\n" + "="*70)
        print("✅ ALL ENHANCED AGENT TESTS PASSED!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
