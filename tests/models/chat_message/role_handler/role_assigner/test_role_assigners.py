"""Tests for role assignment functionality"""
import pytest
from models.chat_message.role_handler.role_assigner import (
    PrimaryRoleSetter,
    SecondaryRoleAssigner,
    RoleMetadata
)

@pytest.fixture
def primary_setter():
    """Fixture providing PrimaryRoleSetter instance"""
    return PrimaryRoleSetter()

@pytest.fixture
def secondary_assigner():
    """Fixture providing SecondaryRoleAssigner instance"""
    return SecondaryRoleAssigner()

class TestPrimaryRoleSetter:
    """Tests for PrimaryRoleSetter"""
    
    def test_set_valid_role(self, primary_setter):
        """Test setting valid role"""
        assert primary_setter.set_role("user") == "user"
        assert primary_setter.set_role("system") == "system"
        assert primary_setter.set_role("assistant") == "assistant"
        assert primary_setter.set_role("function") == "function"
    
    def test_set_invalid_role(self, primary_setter):
        """Test setting invalid role"""
        assert primary_setter.set_role("invalid_role") is None

class TestSecondaryRoleAssigner:
    """Tests for SecondaryRoleAssigner"""
    
    def test_assign_function_metadata(self, secondary_assigner):
        """Test assigning function metadata"""
        metadata = {
            "name": "test_function",
            "function_call": "calculate"
        }
        result = secondary_assigner.assign_metadata("function", metadata)
        assert isinstance(result, RoleMetadata)
        assert result.name == "test_function"
        assert result.function_call == "calculate"
    
    def test_assign_non_function_metadata(self, secondary_assigner):
        """Test assigning non-function metadata"""
        result = secondary_assigner.assign_metadata("user", {})
        assert isinstance(result, RoleMetadata)
        assert result.name is None
        assert result.function_call is None