"""Utility functions for tests"""
from typing import Any, Dict, Optional, Type
from contextlib import contextmanager
import json

def create_role_test_case(
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    expected_behavior: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized role test case"""
    return {
        "role": role,
        "content": content,
        "metadata": metadata or {},
        "expected_behavior": expected_behavior
    }

def verify_role_behavior(
    role_handler: Any,
    test_case: Dict[str, Any]
) -> Dict[str, Any]:
    """Verify role handling behavior"""
    result = role_handler.process_role(
        test_case["role"],
        test_case["content"],
        test_case.get("metadata")
    )
    
    if test_case["expected_behavior"] == "strip_whitespace":
        assert result["content"] == test_case["content"].strip()
    elif test_case["expected_behavior"] == "validate_json":
        try:
            json.loads(result["content"])
        except json.JSONDecodeError:
            raise AssertionError("Invalid JSON content")
            
    return result

@contextmanager
def assert_logs_error(caplog: Any, expected_message: str):
    """Assert that an error was logged"""
    with caplog.at_level("ERROR"):
        yield
        assert any(expected_message in record.message for record in caplog.records)

class MockComponent:
    """Mock component for testing"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def create_mock_handler(**kwargs) -> MockComponent:
    """Create a mock handler with specified attributes"""
    return MockComponent(**kwargs)