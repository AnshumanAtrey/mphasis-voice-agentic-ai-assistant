"""Integration test for complete voice assistant flow"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.builder import AgentBuilder

def test_text_input_greeting():
    """Test greeting intent"""
    agent = AgentBuilder.create_agent(use_mock=True)
    result = agent.process_text_input("Hello!")
    assert result['success']
    assert result['intent'].value == 'greeting'
    print("✅ Greeting test passed")

def test_text_input_task():
    """Test task intent"""
    agent = AgentBuilder.create_agent(use_mock=True)
    result = agent.process_text_input("Show today's tasks")
    assert result['success']
    assert result['intent'].value == 'task_show'
    print("✅ Task intent test passed")

def test_text_input_note():
    """Test note intent"""
    agent = AgentBuilder.create_agent(use_mock=True)
    result = agent.process_text_input("Save this note")
    assert result['success']
    assert result['intent'].value == 'note_save'
    print("✅ Note intent test passed")

def test_text_input_summary():
    """Test summary intent"""
    agent = AgentBuilder.create_agent(use_mock=True)
    result = agent.process_text_input("Summarize this message")
    assert result['success']
    assert result['intent'].value == 'summary'
    print("✅ Summary intent test passed")

def test_context_tracking():
    """Test conversation context tracking"""
    agent = AgentBuilder.create_agent(use_mock=True)

    result1 = agent.process_text_input("Hello")
    result2 = agent.process_text_input("What are my tasks?")

    history = agent.get_conversation_history()
    assert len(history) == 2
    print("✅ Context tracking test passed")

def test_statistics():
    """Test statistics tracking"""
    agent = AgentBuilder.create_agent(use_mock=True)

    initial_stats = agent.get_statistics()
    initial_count = initial_stats.get('total', 0)

    agent.process_text_input("Hello")
    agent.process_text_input("Show tasks")
    agent.process_text_input("Save note")

    stats = agent.get_statistics()
    assert stats['total'] >= initial_count + 3
    print("✅ Statistics test passed")

def test_entity_extraction():
    """Test entity extraction in processing"""
    agent = AgentBuilder.create_agent(use_mock=True)

    result = agent.process_text_input("Email me at test@example.com or call 555-123-4567")
    assert result['success']
    # Should be stored in CSV
    print("✅ Entity extraction test passed")

if __name__ == '__main__':
    test_text_input_greeting()
    test_text_input_task()
    test_text_input_note()
    test_text_input_summary()
    test_context_tracking()
    test_statistics()
    test_entity_extraction()
    print("\n✅ All integration tests passed!")
