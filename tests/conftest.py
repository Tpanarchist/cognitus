"""Global pytest configuration and fixtures"""
import pytest
import logging
from typing import Any, Dict, Optional
from contextlib import contextmanager
from dataclasses import dataclass

# Custom test result data class
@dataclass
class RoleTestResult:
    """Container for role test results"""
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    is_valid: bool = True
    error_message: Optional[str] = None

# Reusable test data
@pytest.fixture
def valid_roles():
    """Valid role test data"""
    return {
        "system": {
            "content": "You are a helpful assistant.",
            "expected_behavior": "strip_whitespace"
        },
        "user": {
            "content": "Hello!",
            "expected_behavior": "preserve"
        },
        "assistant": {
            "content": "How can I help?",
            "expected_behavior": "preserve"
        },
        "function": {
            "content": '{"result": 42}',
            "expected_behavior": "validate_json"
        }
    }

@pytest.fixture
def function_metadata():
    """Sample function metadata"""
    return {
        "basic": {
            "name": "calculator",
            "function_call": "calculate_sum"
        },
        "complex": {
            "name": "data_processor",
            "function_call": "process_data",
            "additional_params": {"timeout": 30}
        }
    }

# Log capture helper
@pytest.fixture
def capture_logs():
    """Helper to capture and verify logs"""
    @contextmanager
    def _capture_logs(logger_name: str, level=logging.INFO):
        logger = logging.getLogger(logger_name)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        logger.addHandler(handler)
        messages = []
        
        def handler_func(record):
            messages.append(record.getMessage())
        
        handler.handle = handler_func
        try:
            yield messages
        finally:
            logger.removeHandler(handler)
            
    return _capture_logs

# Role validation helpers
@pytest.fixture
def assert_valid_role():
    """Helper to assert role validity and properties"""
    def _assert_valid_role(result: Dict[str, Any], expected: RoleTestResult):
        assert result is not None
        assert result["role"] == expected.role
        assert result["content"] == expected.content
        if expected.metadata:
            for key, value in expected.metadata.items():
                assert result.get(key) == value
                
    return _assert_valid_role

@pytest.fixture
def assert_invalid_role():
    """Helper to assert role invalidity"""
    def _assert_invalid_role(result: Optional[Dict[str, Any]], logs: List[str], expected_error: str):
        assert result is None
        assert any(expected_error in log for log in logs)
        
    return _assert_invalid_role

# Content behavior helpers
class ContentBehaviorHelper:
    """Helpers for testing content behavior"""
    
    @staticmethod
    def apply_strip_whitespace(content: str) -> str:
        """Apply whitespace stripping behavior"""
        return content.strip()
    
    @staticmethod
    def apply_preserve(content: str) -> str:
        """Apply content preservation behavior"""
        return content
    
    @staticmethod
    def apply_validate_json(content: str) -> bool:
        """Apply JSON validation behavior"""
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False

@pytest.fixture
def content_behavior():
    """Helper for content behavior testing"""
    return ContentBehaviorHelper()

# Error injection helper
@pytest.fixture
def error_injection():
    """Helper to simulate errors in components"""
    @contextmanager
    def _inject_error(component: Any, method_name: str, error: Exception):
        original_method = getattr(component, method_name)
        def error_method(*args, **kwargs):
            raise error
        setattr(component, method_name, error_method)
        try:
            yield
        finally:
            setattr(component, method_name, original_method)
    return _inject_error