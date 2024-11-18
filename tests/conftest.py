"""Global pytest fixtures and configurations"""
import pytest
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

# Configure logging for tests
@pytest.fixture(scope="session")
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Sample data fixtures
@pytest.fixture
def sample_messages() -> Dict[str, Dict[str, Any]]:
    """Provides sample messages for testing"""
    return {
        "user_message": {
            "role": "user",
            "content": "Hello, world!",
            "metadata": {}
        },
        "system_message": {
            "role": "system",
            "content": "You are a helpful assistant.",
            "metadata": {}
        },
        "assistant_message": {
            "role": "assistant",
            "content": "Hi! How can I help you today?",
            "metadata": {}
        },
        "function_message": {
            "role": "function",
            "content": '{"result": 42}',
            "name": "calculate",
            "metadata": {"function_call": True}
        }
    }

@pytest.fixture
def sample_function_calls() -> Dict[str, Dict[str, Any]]:
    """Provides sample function calls for testing"""
    return {
        "basic_call": {
            "name": "calculate_sum",
            "args": {"numbers": [1, 2, 3]},
            "metadata": {}
        },
        "complex_call": {
            "name": "process_data",
            "args": {
                "input": "test data",
                "options": {"format": "json", "validate": True}
            },
            "metadata": {"priority": "high"}
        }
    }

@pytest.fixture
def temp_test_dir(tmp_path):
    """Provides temporary directory for test files"""
    return tmp_path

# Mock response fixtures
@pytest.fixture
def mock_successful_response():
    """Provides mock successful response data"""
    return {
        "success": True,
        "data": {"result": "test_result"},
        "metadata": {"processing_time": 0.1}
    }

@pytest.fixture
def mock_error_response():
    """Provides mock error response data"""
    return {
        "success": False,
        "error": "test_error",
        "metadata": {"error_code": "TEST_ERROR"}
    }

# Test data helpers
class TestDataHelper:
    """Helper class for managing test data"""
    
    @staticmethod
    def load_test_data(filename: str) -> Dict[str, Any]:
        """Load test data from JSON file"""
        data_path = Path(__file__).parent / "test_data" / filename
        with data_path.open() as f:
            return json.load(f)
    
    @staticmethod
    def create_test_message(
        role: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a test message with given parameters"""
        return {
            "role": role,
            "content": content,
            "metadata": kwargs.get("metadata", {}),
            **kwargs
        }

@pytest.fixture
def test_data_helper():
    """Provides TestDataHelper instance"""
    return TestDataHelper

# Error injection helper
@pytest.fixture
def error_injector():
    """Helper for injecting errors in tests"""
    class ErrorInjector:
        @staticmethod
        def raise_error(*args, **kwargs):
            raise Exception("Test error")
            
        @staticmethod
        def return_error(*args, **kwargs):
            return None, "Test error"
    
    return ErrorInjector()

# Performance tracking helper
@pytest.fixture
def performance_tracker():
    """Helper for tracking test performance"""
    class PerformanceTracker:
        def __init__(self):
            self.timings = {}
            
        def record_timing(self, operation: str, time_taken: float):
            if operation not in self.timings:
                self.timings[operation] = []
            self.timings[operation].append(time_taken)
            
        def get_average(self, operation: str) -> Optional[float]:
            if operation in self.timings:
                return sum(self.timings[operation]) / len(self.timings[operation])
            return None
    
    return PerformanceTracker()

# Cleanup helper
@pytest.fixture(autouse=True)
def cleanup():
    """Automatic cleanup after each test"""
    yield
    # Add any necessary cleanup code here