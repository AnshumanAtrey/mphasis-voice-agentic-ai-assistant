from abc import ABC, abstractmethod
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseLLMService(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class GeminiLLMService(BaseLLMService):
    def __init__(self, api_key: str = None, model: str = None):
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            logger.error("google-generativeai not installed. Install with: pip install google-generativeai")
            raise

        api_key = api_key or Settings.GEMINI_API_KEY
        if not api_key:
            logger.error("GEMINI_API_KEY not set in environment variables")
            raise ValueError("GEMINI_API_KEY required")

        self.genai.configure(api_key=api_key)
        self.model_name = model or Settings.LLM_MODEL
        self.model = self.genai.GenerativeModel(self.model_name)

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': Settings.LLM_TEMPERATURE,
                    'max_output_tokens': Settings.LLM_MAX_TOKENS,
                }
            )
            return response.text if response else "Unable to generate response"
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "I encountered an error processing your request."

class MockLLMService(BaseLLMService):
    """Mock service for testing without API keys"""
    def generate_response(self, prompt: str) -> str:
        responses = {
            'task': "You have 3 tasks due today: finish project report, review code, update documentation.",
            'note': "Note saved successfully.",
            'summary': "Here's a summary of your message.",
            'search': "Found 5 results related to your query.",
        }
        for key, response in responses.items():
            if key in prompt.lower():
                return response
        return f"I understood: {prompt}. How can I help?"

def create_llm_service(use_mock: bool = False, **kwargs) -> BaseLLMService:
    if use_mock:
        return MockLLMService()
    return GeminiLLMService(**kwargs)
