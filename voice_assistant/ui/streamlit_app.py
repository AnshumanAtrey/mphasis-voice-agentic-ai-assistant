#!/usr/bin/env python3
"""Voice Agentic AI Assistant - Modern Minimal UI"""

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
    page_title="Voice Assistant",
    page_icon="◉",
    layout="centered",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stHeader"] {display: none;}
[data-testid="stSidebar"] {background: #0a0a0a; border-right: 1px solid #1a1a1a;}

.stApp {
    background: linear-gradient(180deg, #0a0a0a 0%, #050505 100%);
    color: #e5e5e5;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 8rem !important;
    max-width: 720px !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #fafafa !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

.app-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #fafafa;
    letter-spacing: -0.02em;
    margin: 0;
}
.app-subtitle {
    font-size: 0.875rem;
    color: #6b6b6b;
    margin-top: 0.25rem;
    font-weight: 400;
}

.chat-bubble-user {
    background: #1a1a1a;
    color: #fafafa;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px auto;
    max-width: 75%;
    width: fit-content;
    font-size: 0.95rem;
    line-height: 1.5;
    border: 1px solid #222;
}
.chat-bubble-assistant {
    background: transparent;
    color: #e5e5e5;
    padding: 14px 0;
    margin: 8px 0;
    font-size: 0.95rem;
    line-height: 1.6;
}
.chat-row {
    display: flex;
    margin-bottom: 4px;
}
.chat-row-user { justify-content: flex-end; }
.chat-row-assistant { justify-content: flex-start; }

.metadata {
    display: flex;
    gap: 12px;
    margin-top: 6px;
    font-size: 0.75rem;
    color: #6b6b6b;
    align-items: center;
}
.metadata-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 12px;
    font-size: 0.7rem;
    color: #888;
    letter-spacing: 0.02em;
}
.metadata-chip.intent { color: #d4d4d4; }
.metadata-chip.confidence-high { color: #5eead4; border-color: #134e4a; }
.metadata-chip.confidence-med { color: #fde047; border-color: #422006; }
.metadata-chip.confidence-low { color: #fb7185; border-color: #4c0519; }
.metadata-chip.pattern { color: #a78bfa; border-color: #2e1065; }
.metadata-chip.clarify { color: #fbbf24; border-color: #422006; }

.entity-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 8px;
}
.entity {
    padding: 2px 10px;
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    font-size: 0.7rem;
    color: #9ca3af;
    font-family: 'SF Mono', Monaco, monospace !important;
}

.empty-state {
    text-align: center;
    padding: 4rem 1rem 2rem;
}
.empty-orb {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #2a2a2a, #0a0a0a);
    margin: 0 auto 1.5rem;
    box-shadow: 0 0 60px rgba(255,255,255,0.05), inset 0 0 30px rgba(255,255,255,0.02);
    animation: breathe 3s ease-in-out infinite;
}
@keyframes breathe {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.05); opacity: 1; }
}
.empty-text {
    color: #6b6b6b;
    font-size: 0.95rem;
    font-weight: 400;
}
.empty-hint {
    color: #404040;
    font-size: 0.8rem;
    margin-top: 0.5rem;
}

.input-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, transparent 0%, #050505 30%);
    padding: 3rem 1rem 1.5rem;
    z-index: 100;
    pointer-events: none;
}
.input-footer > div { pointer-events: auto; }

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent;
    border-bottom: 1px solid #1a1a1a;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b6b6b !important;
    border: none !important;
    padding: 8px 16px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #fafafa !important;
    border-bottom: 2px solid #fafafa !important;
}

.stTextInput input {
    background: #0d0d0d !important;
    border: 1px solid #1f1f1f !important;
    color: #fafafa !important;
    padding: 14px 18px !important;
    border-radius: 16px !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus {
    border-color: #404040 !important;
    box-shadow: 0 0 0 1px #404040 !important;
}

.stButton button, .stFormSubmitButton button {
    background: #fafafa !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.15s ease !important;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    background: #e5e5e5 !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"] {
    background: #1a1a1a !important;
    color: #e5e5e5 !important;
    border: 1px solid #2a2a2a !important;
}

audio {
    height: 36px;
    margin-top: 8px;
    filter: invert(0.92) hue-rotate(180deg);
    opacity: 0.6;
}
audio:hover { opacity: 1; }

[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="stExpander"] summary {
    color: #6b6b6b !important;
    font-size: 0.8rem !important;
    padding: 4px 0 !important;
}
[data-testid="stExpander"] summary:hover {
    color: #9ca3af !important;
}

.stProgress > div > div { background: #1a1a1a; }
.stProgress > div > div > div { background: linear-gradient(90deg, #6366f1, #a78bfa); }

[data-testid="stMetricValue"] {
    color: #fafafa !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    color: #6b6b6b !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.sidebar-section {
    color: #6b6b6b;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin: 1.5rem 0 0.75rem;
}

hr {
    border: none !important;
    border-top: 1px solid #1a1a1a !important;
    margin: 1.5rem 0 !important;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1a1a1a; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2a2a2a; }

div[data-testid="stToast"] {
    background: #1a1a1a !important;
    color: #fafafa !important;
    border: 1px solid #2a2a2a !important;
}

.stAlert {
    background: #0d0d0d !important;
    border: 1px solid #1f1f1f !important;
    color: #d4d4d4 !important;
}

.recording-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: #1a1a1a;
    border-radius: 100px;
    border: 1px solid #2a2a2a;
}
.recording-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ef4444;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


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
        st.error("GEMINI_API_KEY not configured")
        st.stop()

    llm_service = GeminiLLMService(api_key=api_key)
    speech_service = create_speech_service(use_mock=True)
    audio_service = create_audio_service(use_mock=True)

    return EnhancedVoiceAgent(
        pipeline_executor=PipelineExecutor(
            voice_input=VoiceInputStage(audio_service),
            speech_to_text=SpeechToTextStage(speech_service),
            text_processor=TextProcessorStage(EntityExtractor()),
            intent_classifier=IntentClassificationStage(IntentClassifier()),
            llm_generator=LLMGeneratorStage(llm_service),
            text_to_speech=TextToSpeechStage(audio_service),
        ),
        llm_service=llm_service,
        conversation_logger=ConversationLogger(CSVHandler()),
    )


def transcribe_audio(audio_bytes: bytes) -> str:
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
        st.toast(f"Transcription failed", icon="⚠")
        return ""


def text_to_audio(text: str) -> bytes:
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return b""


def process_input(agent, user_input: str):
    if not user_input.strip():
        return

    with st.spinner(""):
        result = agent.process_text_input(user_input)

    audio_bytes = text_to_audio(result['response'])

    st.session_state.history.append({
        'user': user_input,
        'response': result['response'],
        'intent': str(result.get('intent', 'UNKNOWN')).replace('IntentType.', ''),
        'confidence': result.get('confidence', 0.0),
        'entities': result.get('entities', {}),
        'follow_up_type': result.get('follow_up_type'),
        'needs_clarification': result.get('needs_clarification', False),
        'audio': audio_bytes,
    })


def render_turn(turn, idx, is_last):
    user_html = f'<div class="chat-row chat-row-user"><div class="chat-bubble-user">{turn["user"]}</div></div>'
    st.markdown(user_html, unsafe_allow_html=True)

    response_text = turn['response'].replace('\n', '<br>')
    assistant_html = f'<div class="chat-row chat-row-assistant"><div class="chat-bubble-assistant">{response_text}</div></div>'
    st.markdown(assistant_html, unsafe_allow_html=True)

    if turn.get('audio'):
        st.audio(turn['audio'], format='audio/mp3', autoplay=is_last)

    conf = turn['confidence'] * 100
    conf_class = 'confidence-high' if conf >= 70 else ('confidence-med' if conf >= 40 else 'confidence-low')

    chips = [f'<span class="metadata-chip intent">{turn["intent"]}</span>']
    chips.append(f'<span class="metadata-chip {conf_class}">{conf:.0f}%</span>')

    if turn.get('follow_up_type'):
        chips.append(f'<span class="metadata-chip pattern">{turn["follow_up_type"]}</span>')
    if turn.get('needs_clarification'):
        chips.append(f'<span class="metadata-chip clarify">clarification needed</span>')

    st.markdown(f'<div class="metadata">{"".join(chips)}</div>', unsafe_allow_html=True)

    entities = {k: v for k, v in turn.get('entities', {}).items() if v}
    if entities:
        entity_chips = []
        for etype, vals in entities.items():
            for v in (vals if isinstance(vals, list) else [vals]):
                entity_chips.append(f'<span class="entity">{etype}: {v}</span>')
        st.markdown(f'<div class="entity-row">{"".join(entity_chips)}</div>', unsafe_allow_html=True)


def main():
    if 'history' not in st.session_state:
        st.session_state.history = []

    agent = get_agent()

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div class="app-title">◉ &nbsp;Voice Assistant</div>
        <div class="app-subtitle">Powered by Gemini 2.5 Flash</div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="app-title">Insights</div>', unsafe_allow_html=True)

        if st.session_state.history:
            insights = agent.get_agent_insights()
            analysis = agent.get_conversation_analysis()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Turns", analysis.get('total_turns', 0))
            with col2:
                st.metric("Confidence", f"{analysis.get('avg_confidence', 0) * 100:.0f}%")

            st.markdown('<div class="sidebar-section">State</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-size: 0.85rem; color: #d4d4d4; line-height: 1.8;">
                <div>Maturity &nbsp;·&nbsp; <span style="color:#888">{insights.get('conversation_maturity', '—')}</span></div>
                <div>Focus &nbsp;·&nbsp; <span style="color:#888">{insights.get('conversation_focus', '—')}</span></div>
            </div>
            """, unsafe_allow_html=True)

            clarity = insights.get('user_intent_clarity', 0)
            st.markdown('<div class="sidebar-section">Intent Clarity</div>', unsafe_allow_html=True)
            st.progress(clarity)

            intents = analysis.get('intent_distribution', {})
            if intents:
                st.markdown('<div class="sidebar-section">Intents</div>', unsafe_allow_html=True)
                for intent, count in intents.items():
                    intent_clean = str(intent).replace('IntentType.', '')
                    st.markdown(f'<div style="font-size: 0.8rem; color: #9ca3af; display: flex; justify-content: space-between; padding: 4px 0;"><span>{intent_clean}</span><span style="color:#6b6b6b">{count}</span></div>', unsafe_allow_html=True)

            patterns = analysis.get('conversation_patterns', [])
            if patterns:
                st.markdown('<div class="sidebar-section">Patterns</div>', unsafe_allow_html=True)
                for p in patterns:
                    st.markdown(f'<div style="font-size: 0.8rem; color: #a78bfa; padding: 2px 0;">{p}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Clear conversation", use_container_width=True, type="secondary"):
                st.session_state.history = []
                st.rerun()
        else:
            st.markdown('<div style="color:#6b6b6b; font-size: 0.85rem; margin-top: 1rem;">Start a conversation to see insights</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-orb"></div>
            <div class="empty-text">How can I help you today?</div>
            <div class="empty-hint">Try saying "show my tasks" or "save a note"</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, turn in enumerate(st.session_state.history):
            is_last = idx == len(st.session_state.history) - 1
            render_turn(turn, idx, is_last)

    st.markdown('<div style="height: 6rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="input-footer"><div>', unsafe_allow_html=True)

    tab_voice, tab_text = st.tabs(["Voice", "Text"])

    with tab_voice:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            audio_result = mic_recorder(
                start_prompt="●  Hold to speak",
                stop_prompt="◼  Stop",
                just_once=True,
                use_container_width=True,
                key='recorder',
            )

        if audio_result and audio_result.get('bytes'):
            with st.spinner(""):
                transcript = transcribe_audio(audio_result['bytes'])

            if transcript:
                process_input(agent, transcript)
                st.rerun()
            else:
                st.toast("Couldn't understand. Try again.", icon="◯")

    with tab_text:
        with st.form(key='text_form', clear_on_submit=True):
            cols = st.columns([5, 1])
            with cols[0]:
                user_text = st.text_input(
                    "msg",
                    placeholder="Message...",
                    label_visibility="collapsed",
                )
            with cols[1]:
                submitted = st.form_submit_button("Send", use_container_width=True)

            if submitted and user_text:
                process_input(agent, user_text)
                st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
