"""Integration tests for RoleHandler"""
import pytest
from models.chat_message.role_handler import RoleHandler

@pytest.fixture
def role_handler():
    """Fixture providing RoleHandler instance"""
    return RoleHandler()

class TestRoleHandler:
    """Integration tests for RoleHandler"""
    
    def test_process_user_role(self, role_handler):
        """Test processing user role"""
        result = role_handler.process_role("user", "test content")
        assert result["role"] == "user"
        assert result["content"] == "test content"
    
    def test_process_system_role(self, role_handler):
        """Test processing system role"""
        result = role_handler.process_role("system", "  test content  ")
        assert result["role"] == "system"
        assert result["content"] == "test content"
    
    def test_process_function_role(self, role_handler):
        """Test processing function role with metadata"""
        metadata = {
            "name": "test_function",
            "function_call": "calculate"
        }
        result = role_handler.process_role("function", '{"test": "value"}', metadata)
        assert result["role"] == "function"
        assert result["name"] == "test_function"
        assert result["function_call"] == "calculate"
    
    def test_process_invalid_role(self, role_handler):
        """Test processing invalid role"""
        result = role_handler.process_role("invalid_role", "test content")
        assert result is None
    
    def test_process_empty_role(self, role_handler):
        """Test processing empty role defaults to user"""
        result = role_handler.process_role("", "test content")
        assert result["role"] == "user"