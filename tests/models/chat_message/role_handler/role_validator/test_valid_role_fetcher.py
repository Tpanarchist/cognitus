"""Tests for valid role fetcher functionality"""
import pytest
from models.chat_message.role_handler.role_validator import ValidRoles, ValidRoleFetcher

def test_get_valid_roles():
    """Test that valid roles are correctly returned"""
    valid_roles = ValidRoleFetcher.get_valid_roles()
    assert isinstance(valid_roles, set)
    assert "system" in valid_roles
    assert "user" in valid_roles
    assert "assistant" in valid_roles
    assert "function" in valid_roles
    assert len(valid_roles) == 4  # Ensure no unexpected roles

def test_get_default_role():
    """Test default role is user"""
    default_role = ValidRoleFetcher.get_default_role()
    assert default_role == "user"

def test_valid_roles_enum():
    """Test ValidRoles enum values"""
    assert ValidRoles.SYSTEM.value == "system"
    assert ValidRoles.USER.value == "user"
    assert ValidRoles.ASSISTANT.value == "assistant"
    assert ValidRoles.FUNCTION.value == "function"