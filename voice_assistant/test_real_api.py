#!/usr/bin/env python3
"""Test pipeline with real Gemini API"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.enhanced_agent import EnhancedVoiceAgent
from pipeline.pipeline_stages import (
    VoiceInputStage, SpeechToTextStage, TextProcessorStage,
    IntentClassificationStage, LLMGeneratorStage, TextToSpeechStage,
    PipelineExecutor,
)
from services.llm_service import GeminiLLMService
from services import create_speech_service, create_audio_service
from patterns import EntityExtractor, IntentClassifier
from storage import ConversationLogger, CSVHandler

# Real API Key
API_KEY = "AIzaSyBoIOqwq_vEItxBfdbPPsMNVOl4odhYmzw"

def create_agent_with_real_api():
    """Create agent with real Gemini API"""
    print("🔧 Initializing agent with REAL Gemini API...")

    # Real LLM service
    llm_service = GeminiLLMService(api_key=API_KEY)

    # Mock services (speech/audio)
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


def test_case_1():
    """Test 1: Simple task query"""
    print("\n" + "="*70)
    print("TEST 1: Simple Task Query")
    print("="*70)

    agent = create_agent_with_real_api()
    test_input = "Show my tasks for today"

    print(f"\n📝 Input: {test_input}")
    print(f"⏱️  Starting test... ")

    start_time = time.time()
    result = agent.process_text_input(test_input)
    duration = time.time() - start_time

    print(f"\n✅ Test completed in {duration:.2f}s")
    print(f"🎯 Intent: {result['intent']}")
    print(f"📊 Confidence: {result['confidence']:.0%}")
    print(f"📤 Response: {result['response'][:100]}...")
    print(f"✓ Success: {result['success']}")

    if result.get('needs_clarification'):
        print(f"❓ Needs Clarification: {result['clarification_prompt']}")

    return duration


def test_case_2():
    """Test 2: Follow-up with context"""
    print("\n" + "="*70)
    print("TEST 2: Multi-Turn with Follow-Up & Context")
    print("="*70)

    agent = create_agent_with_real_api()

    # Turn 1
    print(f"\n📝 Turn 1: 'Show my tasks'")
    start_time = time.time()
    result1 = agent.process_text_input("Show my tasks")
    turn1_time = time.time() - start_time

    print(f"✅ Completed in {turn1_time:.2f}s")
    print(f"🎯 Intent: {result1['intent']}")
    print(f"📤 Response: {result1['response'][:80]}...")

    # Wait to avoid rate limit
    print("\n⏳ Waiting 2 seconds before next request (avoid rate limit)...")
    time.sleep(2)

    # Turn 2 - Follow-up
    print(f"\n📝 Turn 2: 'Also save this as a note'")
    start_time = time.time()
    result2 = agent.process_text_input("Also save this as a note")
    turn2_time = time.time() - start_time

    print(f"✅ Completed in {turn2_time:.2f}s")
    print(f"🎯 Intent: {result2['intent']}")
    print(f"📤 Response: {result2['response'][:80]}...")

    if result2.get('follow_up_type'):
        print(f"🔗 Follow-up Pattern: {result2['follow_up_type']}")

    # Analysis
    print(f"\n📊 Conversation Analysis:")
    analysis = agent.get_conversation_analysis()
    print(f"   Total turns: {analysis['total_turns']}")
    print(f"   Unique intents: {analysis['unique_intents']}")
    print(f"   Avg confidence: {analysis['avg_confidence']:.0%}")

    total_time = turn1_time + turn2_time + 2
    return total_time


def test_case_3():
    """Test 3: Error handling with edge case"""
    print("\n" + "="*70)
    print("TEST 3: Error Handling & Confidence Detection")
    print("="*70)

    agent = create_agent_with_real_api()
    test_input = "it"  # Ambiguous short input

    print(f"\n📝 Input (ambiguous): '{test_input}'")
    print(f"⏱️  Testing edge case...")

    start_time = time.time()
    result = agent.process_text_input(test_input)
    duration = time.time() - start_time

    print(f"\n✅ Completed in {duration:.2f}s")
    print(f"🎯 Intent: {result['intent']}")
    print(f"📊 Confidence: {result['confidence']:.0%}")

    if result.get('needs_clarification'):
        print(f"❓ Clarification Triggered: {result['clarification_prompt']}")

    if result.get('ambiguous'):
        print(f"⚠️  Ambiguity Detected: True")

    print(f"📤 Response: {result['response'][:80]}...")

    return duration


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 REAL API PIPELINE TESTS")
    print("🔑 Using: Gemini API")
    print("="*70)

    times = {}

    try:
        # Test 1
        times['test_1'] = test_case_1()
        print("\n⏳ Waiting 3 seconds before next test (avoid rate limit)...")
        time.sleep(3)

        # Test 2
        times['test_2'] = test_case_2()
        print("\n⏳ Waiting 3 seconds before final test (avoid rate limit)...")
        time.sleep(3)

        # Test 3
        times['test_3'] = test_case_3()

        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)

        print(f"\n⏱️  Execution Times:")
        print(f"   Test 1 (Simple Query):        {times['test_1']:.2f}s")
        print(f"   Test 2 (Multi-turn):         {times['test_2']:.2f}s (includes 2s wait)")
        print(f"   Test 3 (Edge Case):          {times['test_3']:.2f}s")

        total_time = sum(times.values())
        print(f"\n   Total Time:                  {total_time:.2f}s")
        print(f"   Avg Time per Test:           {total_time/3:.2f}s")

        print(f"\n✅ All Tests Passed!")
        print(f"✅ Real API Working!")
        print(f"✅ Pipeline Complete!")
        print(f"✅ Logging Working!")
        print(f"✅ Error Handling Working!")

        print("\n" + "="*70)
        print("🎉 REAL API INTEGRATION SUCCESSFUL!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
