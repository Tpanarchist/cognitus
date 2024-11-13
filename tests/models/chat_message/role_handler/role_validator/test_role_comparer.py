"""Tests for role comparison functionality"""
import pytest
from models.chat_message.role_handler.role_validator import RoleComparer, ValidRoles

@pytest.fixture
def role_comparer():
    """Fixture providing RoleComparer instance"""
    return RoleComparer()

def test_is_valid_role(role_comparer):
    """Test validation of roles"""
    assert role_comparer.is_valid_role("system") is True
    assert role_comparer.is_valid_role("user") is True
    assert role_comparer.is_valid_role("assistant") is True
    assert role_comparer.is_valid_role("function") is True
    assert role_comparer.is_valid_role("invalid_role") is False
    assert role_comparer.is_valid_role("") is False

def test_get_role_type(role_comparer):
    """Test role type retrieval"""
    assert role_comparer.get_role_type("system") == ValidRoles.SYSTEM
    assert role_comparer.get_role_type("user") == ValidRoles.USER
    assert role_comparer.get_role_type("invalid_role") is None