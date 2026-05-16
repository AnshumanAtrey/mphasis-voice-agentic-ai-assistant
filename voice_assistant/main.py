#!/usr/bin/env python3
"""Main entry point for Voice Agentic AI Assistant"""

import sys
from pathlib import Path

# Add project root to path
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
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_enhanced_agent():
    """Create EnhancedVoiceAgent with all dependencies"""
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

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🎤 Voice Agentic AI Assistant - Enhanced")
    print("="*60 + "\n")

    # Build enhanced agent with mock services (no API keys needed for testing)
    agent = create_enhanced_agent()

    print("Options:")
    print("1. Voice Input (requires microphone)")
    print("2. Text Input (for testing)")
    print("3. View Statistics")
    print("4. View History")
    print("5. View Agent Insights")
    print("6. View Conversation Analysis")
    print("7. Exit")
    print()

    while True:
        choice = input("Select option (1-7): ").strip()

        if choice == '1':
            print("\n🎤 Recording for 5 seconds...")
            result = agent.process_voice_input(duration=5.0)
            print_result(result)

        elif choice == '2':
            text = input("\nEnter your message: ").strip()
            if text:
                result = agent.process_text_input(text)
                print_result(result)

        elif choice == '3':
            stats = agent.get_statistics()
            print("\n📊 Statistics:")
            print(f"Total conversations: {stats.get('total', 0)}")
            if 'intents' in stats:
                print("Intent breakdown:")
                for intent, count in stats['intents'].items():
                    print(f"  - {intent}: {count}")

        elif choice == '4':
            history = agent.get_conversation_history()
            if history:
                print("\n📝 Conversation History:")
                for i, turn in enumerate(history, 1):
                    print(f"\n{i}. Intent: {turn.get('intent')}")
                    print(f"   You: {turn.get('user')}")
                    print(f"   Assistant: {turn.get('response')}")
            else:
                print("\nNo conversation history yet.")

        elif choice == '5':
            insights = agent.get_agent_insights()
            print("\n🧠 Agent Insights:")
            print(f"  Is Active: {insights.get('is_active')}")
            print(f"  Conversation Maturity: {insights.get('conversation_maturity')}")
            print(f"  User Intent Clarity: {insights.get('user_intent_clarity'):.0%}")
            print(f"  Conversation Focus: {insights.get('conversation_focus')}")

        elif choice == '6':
            analysis = agent.get_conversation_analysis()
            print("\n📈 Conversation Analysis:")
            print(f"  Total Turns: {analysis.get('total_turns', 0)}")
            print(f"  Unique Intents: {analysis.get('unique_intents', 0)}")
            if 'intent_distribution' in analysis:
                print("  Intent Distribution:")
                for intent, count in analysis['intent_distribution'].items():
                    print(f"    - {intent}: {count}")
            if 'conversation_patterns' in analysis:
                patterns = analysis['conversation_patterns']
                if patterns:
                    print(f"  Detected Patterns: {', '.join(patterns)}")
            print(f"  Average Confidence: {analysis.get('avg_confidence', 0):.0%}")

        elif choice == '7':
            print("\n👋 Goodbye!\n")
            break

        else:
            print("Invalid option. Please try again.")

        print()

def print_result(result: dict):
    """Pretty print result"""
    print()
    if result.get('success'):
        print(f"✅ Intent: {result.get('intent')}")
        print(f"📥 You: {result.get('user_input')}")
        print(f"📤 Assistant: {result.get('response')}")
    else:
        print(f"❌ Error: {result.get('response')}")
        if 'error' in result:
            print(f"   Details: {result.get('error')}")

if __name__ == '__main__':
    main()
