"""Comprehensive error handling and validation for the voice assistant"""

from typing import Dict, Any, Optional, List
from enum import Enum
import re
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ValidationError(Exception):
    """Base exception for validation errors"""
    pass


class InputValidationError(ValidationError):
    """Raised when input validation fails"""
    pass


class ProcessingError(ValidationError):
    """Raised when processing fails"""
    pass


class ServiceError(ValidationError):
    """Raised when external service fails"""
    pass


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class InputValidator:
    """Validates input data"""

    @staticmethod
    def validate_text_input(text: str, min_length: int = 1, max_length: int = 1000) -> Dict[str, Any]:
        """
        Validate text input
        Returns: {valid: bool, errors: list, cleaned: str}
        """
        errors = []

        if not text:
            errors.append("Input cannot be empty")
            return {'valid': False, 'errors': errors, 'cleaned': ''}

        if not isinstance(text, str):
            errors.append(f"Input must be string, got {type(text).__name__}")
            return {'valid': False, 'errors': errors, 'cleaned': ''}

        cleaned = text.strip()

        if len(cleaned) < min_length:
            errors.append(f"Input too short (minimum {min_length} characters)")

        if len(cleaned) > max_length:
            errors.append(f"Input too long (maximum {max_length} characters)")
            cleaned = cleaned[:max_length]

        # Check for suspicious patterns
        if InputValidator._contains_sql_injection(cleaned):
            errors.append("Input contains suspicious SQL patterns")

        if InputValidator._contains_script_injection(cleaned):
            errors.append("Input contains suspicious script patterns")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'cleaned': cleaned
        }

    @staticmethod
    def validate_audio_duration(duration: float) -> Dict[str, Any]:
        """Validate audio recording duration"""
        errors = []

        if not isinstance(duration, (int, float)):
            errors.append(f"Duration must be numeric, got {type(duration).__name__}")
            return {'valid': False, 'errors': errors}

        if duration <= 0:
            errors.append("Duration must be positive")

        if duration > 300:  # 5 minutes max
            errors.append("Duration exceeds maximum (5 minutes)")

        if duration < 0.5:  # 0.5 seconds min
            errors.append("Duration too short (minimum 0.5 seconds)")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'duration': max(0.5, min(300, duration)) if len(errors) == 0 else duration
        }

    @staticmethod
    def validate_intent(intent: Any) -> Dict[str, Any]:
        """Validate intent object"""
        errors = []

        if intent is None:
            errors.append("Intent cannot be None")
            return {'valid': False, 'errors': errors}

        if not hasattr(intent, 'value'):
            errors.append("Intent must have 'value' attribute")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def validate_confidence_score(score: float) -> Dict[str, Any]:
        """Validate confidence score (0.0 - 1.0)"""
        errors = []

        if not isinstance(score, (int, float)):
            errors.append(f"Score must be numeric, got {type(score).__name__}")
            return {'valid': False, 'errors': errors}

        if score < 0 or score > 1:
            errors.append(f"Score must be between 0 and 1, got {score}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'score': max(0, min(1, score))  # Clamp to valid range
        }

    @staticmethod
    def _contains_sql_injection(text: str) -> bool:
        """Detect potential SQL injection patterns"""
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bOR\b.*=.*)",
            r"(--|\#|\/\*)",
            r"(\bDROP\b.*\b)",
            r"(\bDELETE\b.*\b)",
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in sql_patterns)

    @staticmethod
    def _contains_script_injection(text: str) -> bool:
        """Detect potential script injection patterns"""
        script_patterns = [
            r"(<script|javascript:|onerror=|onclick=)",
            r"(\${.*})",
            r"(__proto__|constructor)",
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in script_patterns)


class ErrorHandler:
    """Central error handling and recovery"""

    def __init__(self):
        self.error_history = []
        self.max_history = 100

    def log_error(
        self,
        error: Exception,
        severity: ErrorSeverity,
        context: str = "",
        recoverable: bool = True
    ) -> Dict[str, Any]:
        """Log error with context"""

        error_record = {
            'type': type(error).__name__,
            'message': str(error),
            'severity': severity.value,
            'context': context,
            'recoverable': recoverable,
        }

        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)

        log_func = {
            ErrorSeverity.LOW: logger.warning,
            ErrorSeverity.MEDIUM: logger.error,
            ErrorSeverity.HIGH: logger.error,
            ErrorSeverity.CRITICAL: logger.critical,
        }.get(severity, logger.error)

        log_func(f"[{severity.value}] {context}: {str(error)}")

        return error_record

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_history:
            return {'total': 0, 'errors': []}

        severity_counts = {}
        for error in self.error_history:
            sev = error['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            'total': len(self.error_history),
            'by_severity': severity_counts,
            'recent': self.error_history[-10:]
        }


class FallbackResponseGenerator:
    """Generate helpful fallback responses for error scenarios"""

    @staticmethod
    def generate_input_error_response(errors: List[str]) -> str:
        """Generate response for input validation errors"""
        if not errors:
            return "I didn't understand your input. Please try again."

        primary_error = errors[0]
        responses = {
            'empty': "I didn't hear anything. Could you please speak again?",
            'too short': "That was quite brief. Could you provide more details?",
            'too long': "That was quite long. Could you rephrase more concisely?",
            'suspicious': "I couldn't process that input. Please try a different phrasing.",
        }

        for key, response in responses.items():
            if key in primary_error.lower():
                return response

        return "I had trouble understanding that. Could you rephrase it?"

    @staticmethod
    def generate_processing_error_response(error_type: str) -> str:
        """Generate response for processing errors"""
        responses = {
            'intent': "I wasn't sure what you meant. Could you clarify?",
            'entity': "I had trouble understanding the details. Could you provide them again?",
            'speech': "I had trouble understanding the audio. Could you speak clearly?",
            'service': "I'm having trouble processing requests right now. Please try again.",
        }
        return responses.get(error_type, "I encountered an issue. Please try again.")

    @staticmethod
    def generate_confidence_response(confidence: float) -> str:
        """Generate response for low confidence intents"""
        if confidence < 0.5:
            return "I'm not confident about your request. Could you clarify?"
        elif confidence < 0.65:
            return "I think you might be asking about something, but I'm not sure. Could you be more specific?"
        else:
            return "Just to confirm, did you mean...?"

    @staticmethod
    def generate_generic_recovery_response() -> str:
        """Generate generic recovery response"""
        return "I encountered an issue. Let me try that again. Please repeat your request."


class EdgeCaseHandler:
    """Handle edge cases and boundary conditions"""

    @staticmethod
    def handle_empty_result(original_input: str) -> Dict[str, Any]:
        """Handle when processing returns no result"""
        return {
            'success': False,
            'intent': None,
            'response': FallbackResponseGenerator.generate_input_error_response(['empty']),
            'user_input': original_input,
            'error': 'No result from processing pipeline',
            'recovery_suggested': True
        }

    @staticmethod
    def handle_none_intent(original_input: str) -> Dict[str, Any]:
        """Handle when intent is None"""
        return {
            'success': False,
            'intent': None,
            'response': FallbackResponseGenerator.generate_processing_error_response('intent'),
            'user_input': original_input,
            'error': 'Intent classification failed',
            'recovery_suggested': True
        }

    @staticmethod
    def handle_missing_confidence(result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle when confidence score is missing"""
        result['confidence'] = 0.5  # Default to neutral confidence
        result['confidence_warning'] = True
        return result

    @staticmethod
    def handle_malformed_response(original_input: str, error: Exception) -> Dict[str, Any]:
        """Handle malformed responses from services"""
        logger.error(f"Malformed response: {str(error)}")
        return {
            'success': False,
            'intent': None,
            'response': FallbackResponseGenerator.generate_processing_error_response('service'),
            'user_input': original_input,
            'error': 'Service returned invalid response',
            'recovery_suggested': True
        }

    @staticmethod
    def handle_service_timeout(original_input: str, timeout_seconds: float) -> Dict[str, Any]:
        """Handle service timeout"""
        logger.warning(f"Service timeout after {timeout_seconds}s")
        return {
            'success': False,
            'intent': None,
            'response': FallbackResponseGenerator.generate_processing_error_response('service'),
            'user_input': original_input,
            'error': f'Request timed out after {timeout_seconds}s',
            'recovery_suggested': True,
            'timeout': True
        }

    @staticmethod
    def handle_null_entities(result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle null or missing entities"""
        if 'entities' not in result:
            result['entities'] = {}
        return result

    @staticmethod
    def validate_result_structure(result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and repair result structure"""
        required_keys = ['success', 'intent', 'response', 'user_input']

        for key in required_keys:
            if key not in result:
                if key == 'success':
                    result[key] = False
                elif key == 'response':
                    result[key] = FallbackResponseGenerator.generate_generic_recovery_response()
                elif key == 'user_input':
                    result[key] = ''
                else:
                    result[key] = None

        if 'confidence' not in result:
            result['confidence'] = 0.5

        if 'entities' not in result:
            result['entities'] = {}

        return result
