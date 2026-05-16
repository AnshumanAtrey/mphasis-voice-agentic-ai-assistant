#!/usr/bin/env python3
"""Streamlit UI for Voice Agentic AI Assistant - Full Featured"""

import sys
import os
import io
import tempfile
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).parent.parent / '.env')

import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

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


st.set_page_config(
    page_title="Voice Agentic AI Assistant",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_agent():
    """Initialize agent with real Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY', '')

    if not api_key:
        try:
            api_key = st.secrets.get('GEMINI_API_KEY', '')
        except (FileNotFoundError, KeyError):
            pass

    if not api_key:
        st.error("GEMINI_API_KEY not found. Set it in .env (local) or Streamlit Cloud secrets.")
        st.stop()

    llm_service = GeminiLLMService(api_key=api_key)
    speech_service = create_speech_service(use_mock=True)
    audio_service = create_audio_service(use_mock=True)

    entity_extractor = EntityExtractor()
    intent_classifier = IntentClassifier()

    pipeline_executor = PipelineExecutor(
        voice_input=VoiceInputStage(audio_service),
        speech_to_text=SpeechToTextStage(speech_service),
        text_processor=TextProcessorStage(entity_extractor),
        intent_classifier=IntentClassificationStage(intent_classifier),
        llm_generator=LLMGeneratorStage(llm_service),
        text_to_speech=TextToSpeechStage(audio_service),
    )

    return EnhancedVoiceAgent(
        pipeline_executor=pipeline_executor,
        llm_service=llm_service,
        conversation_logger=ConversationLogger(CSVHandler()),
    )


def transcribe_audio(audio_bytes: bytes) -> str:
    """Convert audio bytes to text using SpeechRecognition"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio.export(tmp.name, format='wav')
            tmp_path = tmp.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language='en-US')
        os.unlink(tmp_path)
        return text
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""


def text_to_audio(text: str) -> bytes:
    """Generate audio bytes from text using gTTS"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        st.error(f"TTS error: {e}")
        return b""


def process_input(agent, user_input: str):
    """Process user input through agent and update state"""
    if not user_input.strip():
        return

    with st.spinner("Processing..."):
        result = agent.process_text_input(user_input)

    audio_bytes = text_to_audio(result['response'])

    st.session_state.history.append({
        'user': user_input,
        'response': result['response'],
        'intent': str(result.get('intent', 'UNKNOWN')),
        'confidence': result.get('confidence', 0.0),
        'entities': result.get('entities', {}),
        'follow_up_type': result.get('follow_up_type'),
        'needs_clarification': result.get('needs_clarification', False),
        'audio': audio_bytes,
        'success': result.get('success', False),
    })


def render_message(turn, idx):
    """Render a single conversation turn"""
    with st.chat_message("user"):
        st.markdown(turn['user'])

    with st.chat_message("assistant"):
        st.markdown(turn['response'])

        if turn.get('audio'):
            st.audio(turn['audio'], format='audio/mp3', autoplay=(idx == len(st.session_state.history) - 1))

        cols = st.columns(3)
        with cols[0]:
            intent_label = turn['intent'].replace('IntentType.', '')
            st.caption(f"🎯 **{intent_label}**")
        with cols[1]:
            conf_pct = turn['confidence'] * 100
            color = "🟢" if conf_pct >= 70 else "🟡" if conf_pct >= 40 else "🔴"
            st.caption(f"{color} **{conf_pct:.0f}%** confidence")
        with cols[2]:
            if turn.get('follow_up_type'):
                st.caption(f"🔗 **{turn['follow_up_type']}**")
            elif turn.get('needs_clarification'):
                st.caption("❓ **Clarification needed**")

        entities = turn.get('entities', {})
        non_empty = {k: v for k, v in entities.items() if v}
        if non_empty:
            with st.expander("📋 Extracted Entities"):
                for entity_type, values in non_empty.items():
                    if values:
                        st.write(f"**{entity_type}**: {', '.join(map(str, values))}")


def main():
    if 'history' not in st.session_state:
        st.session_state.history = []

    agent = get_agent()

    st.title("🎤 Voice Agentic AI Assistant")
    st.caption("Powered by Gemini 2.5 Flash • SpeechRecognition • gTTS")

    with st.sidebar:
        st.header("📊 Conversation Insights")

        if st.session_state.history:
            insights = agent.get_agent_insights()
            analysis = agent.get_conversation_analysis()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Turns", analysis.get('total_turns', 0))
            with col2:
                avg_conf = analysis.get('avg_confidence', 0) * 100
                st.metric("Avg Confidence", f"{avg_conf:.0f}%")

            st.markdown("---")
            st.markdown("**Conversation State**")
            st.write(f"🎓 Maturity: `{insights.get('conversation_maturity', 'N/A')}`")
            st.write(f"🎯 Focus: `{insights.get('conversation_focus', 'N/A')}`")

            clarity = insights.get('user_intent_clarity', 0) * 100
            st.progress(clarity / 100, text=f"Intent Clarity: {clarity:.0f}%")

            st.markdown("---")
            st.markdown("**Intent Distribution**")
            for intent, count in analysis.get('intent_distribution', {}).items():
                intent_clean = str(intent).replace('IntentType.', '')
                st.write(f"• {intent_clean}: {count}")

            patterns = analysis.get('conversation_patterns', [])
            if patterns:
                st.markdown("---")
                st.markdown("**Detected Patterns**")
                for pattern in patterns:
                    st.write(f"🔄 {pattern}")
        else:
            st.info("Start a conversation to see insights")

        st.markdown("---")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.history = []
            get_agent.clear()
            st.rerun()

        st.markdown("---")
        st.markdown("**💡 Try saying:**")
        st.markdown("""
        - "Show my tasks for today"
        - "Save this as a note"
        - "Summarize this message"
        - "Email me at john@test.com"
        - "Schedule a meeting tomorrow"
        """)

    for idx, turn in enumerate(st.session_state.history):
        render_message(turn, idx)

    st.markdown("---")

    tab1, tab2 = st.tabs(["🎙️ Voice Input", "💬 Text Input"])

    with tab1:
        st.markdown("**Click the microphone to record, click again to stop**")
        audio_result = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            key='recorder',
        )

        if audio_result and audio_result.get('bytes'):
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(audio_result['bytes'])

            if transcript:
                st.success(f"Heard: \"{transcript}\"")
                process_input(agent, transcript)
                st.rerun()
            else:
                st.warning("Could not understand audio. Please try again.")

    with tab2:
        with st.form(key='text_form', clear_on_submit=True):
            user_text = st.text_input(
                "Type your message:",
                placeholder="e.g., Show my tasks for today",
            )
            submitted = st.form_submit_button("Send", use_container_width=True)

            if submitted and user_text:
                process_input(agent, user_text)
                st.rerun()


if __name__ == "__main__":
    main()
