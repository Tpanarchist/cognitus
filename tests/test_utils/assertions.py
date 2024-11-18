"""Custom assertions for testing"""
from typing import Any, Dict, Optional
import re

def assert_valid_message(
    message: Dict[str, Any],
    expected_role: Optional[str] = None,
    expected_content_pattern: Optional[str] = None
):
    """Assert that a message has valid structure and content"""
    # Check basic structure
    assert isinstance(message, dict), "Message must be a dictionary"
    assert "role" in message, "Message must have a role"
    assert "content" in message, "Message must have content"
    
    # Check role if specified
    if expected_role:
        assert message["role"] == expected_role, f"Expected role {expected_role}"
    
    # Check content pattern if specified
    if expected_content_pattern:
        assert re.match(expected_content_pattern, message["content"]), \
            f"Content does not match pattern {expected_content_pattern}"

def assert_valid_function_call(
    function_call: Dict[str, Any],
    expected_name: Optional[str] = None
):
    """Assert that a function call is valid"""
    assert isinstance(function_call, dict), "Function call must be a dictionary"
    assert "name" in function_call, "Function call must have a name"
    
    if expected_name:
        assert function_call["name"] == expected_name, \
            f"Expected function name {expected_name}"

def assert_successful_result(result: Dict[str, Any]):
    """Assert that an operation result indicates success"""
    assert isinstance(result, dict), "Result must be a dictionary"
    assert result.get("success") is True, "Result must indicate success"
    assert "error" not in result, "Successful result should not have error"

def assert_valid_error(
    error: Dict[str, Any],
    expected_type: Optional[str] = None
):
    """Assert that an error has valid structure"""
    assert isinstance(error, dict), "Error must be a dictionary"
    assert "error" in error, "Error must have error message"
    
    if expected_type:
        assert error.get("type") == expected_type, \
            f"Expected error type {expected_type}"

def assert_valid_metadata(metadata: Dict[str, Any]):
    """Assert that metadata has valid structure"""
    assert isinstance(metadata, dict), "Metadata must be a dictionary"
    # Add specific metadata validation as needed

def assert_performance_within_limits(
    time_taken: float,
    limit: float
):
    """Assert that operation performance is within limits"""
    assert time_taken <= limit, \
        f"Operation took {time_taken}s, exceeding limit of {limit}s"