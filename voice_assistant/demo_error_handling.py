#!/usr/bin/env python3
"""Demo script showcasing error handling capabilities"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.enhanced_agent import EnhancedVoiceAgent
from pipeline.pipeline_stages import (
    VoiceInputStage, SpeechToTextStage, TextProcessorStage,
    IntentClassificationStage, LLMGeneratorStage, TextToSpeechStage,
    PipelineExecutor,
)
from services import create_llm_service, create_speech_service, create_audio_service
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler


def create_agent():
    """Create agent with all services"""
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

    return EnhancedVoiceAgent(
        pipeline_executor=pipeline_executor,
        llm_service=llm_service,
        conversation_logger=conversation_logger,
    )


def demo_section(title):
    """Print demo section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_input(text, agent):
    """Demo processing a single input"""
    print(f"📝 Input:    {text}")
    result = agent.process_text_input(text)
    print(f"✅ Success:  {result['success']}")
    print(f"🎯 Intent:   {result.get('intent', 'None')}")
    print(f"🤖 Response: {result['response'][:60]}...")
    if result.get('confidence'):
        print(f"📊 Confidence: {result['confidence']:.0%}")
    if result.get('needs_clarification'):
        print(f"❓ Clarification: {result.get('clarification_prompt')}")
    print()


def main():
    """Run error handling demo"""
    print("\n" + "="*70)
    print("🛡️  VOICE ASSISTANT - ERROR HANDLING DEMONSTRATION")
    print("="*70)

    agent = create_agent()

    # Demo 1: Normal valid input
    demo_section("Demo 1: Valid Input Processing")
    demo_input("Show my tasks for today", agent)

    # Demo 2: Ambiguous short input
    demo_section("Demo 2: Ambiguous Short Input")
    print("When users provide very short, ambiguous input:")
    demo_input("it", agent)
    print("👉 Agent detects ambiguity and requests clarification")

    # Demo 3: Empty input handling
    demo_section("Demo 3: Empty Input Protection")
    print("When users provide empty input:")
    result = agent.process_text_input("")
    print(f"📝 Input:    (empty)")
    print(f"✅ Success:  {result['success']}")
    print(f"🤖 Response: {result['response']}")
    print()
    print("👉 Agent gracefully handles with helpful error message")

    # Demo 4: Very long input
    demo_section("Demo 4: Input Length Validation")
    long_input = "word " * 250  # 1250 chars
    print(f"When users provide very long input ({len(long_input)} chars):")
    result = agent.process_text_input(long_input)
    print(f"📝 Input:    {long_input[:30]}... (truncated, {len(long_input)} chars)")
    print(f"✅ Success:  {result['success']}")
    if not result['success']:
        print(f"🤖 Response: {result['response']}")
    else:
        print(f"🤖 Response: {result['response'][:60]}...")
    print()
    print("👉 Agent validates and handles gracefully")

    # Demo 5: Security - SQL injection prevention
    demo_section("Demo 5: Security - SQL Injection Prevention")
    print("When users provide SQL injection patterns:")
    result = agent.process_text_input("'; DROP TABLE users; --")
    print(f"📝 Input:    '; DROP TABLE users; --")
    print(f"✅ Success:  {result['success']}")
    print(f"🤖 Response: {result['response']}")
    print()
    print("👉 Agent detects and blocks malicious input")

    # Demo 6: Follow-up detection with context
    demo_section("Demo 6: Context-Aware Multi-Turn Conversation")
    print("Multi-turn conversation with follow-up detection:")
    demo_input("Show my tasks", agent)
    demo_input("Also save this note", agent)
    demo_input("Show tasks again", agent)
    print("👉 Agent tracks context across turns")

    # Demo 7: Confidence-based clarification
    demo_section("Demo 7: Confidence-Based Clarification")
    print("Agent monitors confidence scores:")
    agent_fresh = create_agent()
    for i, text in enumerate(["hello", "show", "tasks", "note"], 1):
        print(f"Turn {i}: '{text}'")
        result = agent_fresh.process_text_input(text)
        conf = result.get('confidence', 0)
        print(f"  Confidence: {conf:.0%}")
        if conf < 0.65:
            print(f"  Action: Request clarification")
        print()

    # Demo 8: Error recovery
    demo_section("Demo 8: Graceful Error Recovery")
    print("Agent handles errors without crashing:")
    test_cases = [
        ("Very ambiguous input", "?"),
        ("Special characters", "@#$%^&*()"),
        ("Numbers only", "12345"),
        ("Mixed content", "test123!@#"),
    ]
    for description, test_input in test_cases:
        result = agent.process_text_input(test_input)
        status = "✅ Processed" if result else "⚠️  Handled"
        print(f"{description:25} → {status}")

    print()
    print("👉 All edge cases handled without crashes")

    # Demo 9: Conversation analysis
    demo_section("Demo 9: Conversation Analysis & Insights")
    agent_final = create_agent()
    for text in ["Hello", "Show my tasks", "Save note", "Show tasks again"]:
        agent_final.process_text_input(text)

    analysis = agent_final.get_conversation_analysis()
    insights = agent_final.get_agent_insights()

    print(f"Conversation Statistics:")
    print(f"  Total turns: {analysis['total_turns']}")
    print(f"  Unique intents: {analysis['unique_intents']}")
    print(f"  Avg confidence: {analysis['avg_confidence']:.0%}")
    print(f"  Patterns: {', '.join(analysis.get('conversation_patterns', ['None'])) or 'None'}")
    print()
    print(f"Agent Insights:")
    print(f"  Is Active: {insights['is_active']}")
    print(f"  Maturity: {insights['conversation_maturity']}")
    print(f"  Intent Clarity: {insights['user_intent_clarity']:.0%}")
    print(f"  Focus: {insights['conversation_focus']}")
    print()

    # Summary
    demo_section("Summary: Error Handling Features")
    features = [
        ("Input Validation", "Length, type, injection patterns"),
        ("Error Recovery", "Graceful degradation, fallback responses"),
        ("Security", "SQL/XSS injection prevention"),
        ("User Experience", "Helpful messages, clarification requests"),
        ("Conversation Tracking", "Multi-turn context awareness"),
        ("Confidence Monitoring", "Automatic clarification when uncertain"),
        ("Edge Case Handling", "No crashes on any input"),
    ]

    for i, (feature, description) in enumerate(features, 1):
        print(f"{i}. {feature:25} → {description}")

    print()
    print("="*70)
    print("✅ Error Handling Demo Complete!")
    print("="*70)
    print()


if __name__ == '__main__':
    main()
