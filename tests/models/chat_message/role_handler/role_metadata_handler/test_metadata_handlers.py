"""Tests for role metadata handling functionality"""
import pytest
from models.chat_message.role_handler.role_metadata_handler import (
    RolePropertyAdder,
    RoleProperties,
    RoleBehaviorApplier
)

@pytest.fixture
def property_adder():
    """Fixture providing RolePropertyAdder instance"""
    return RolePropertyAdder()

@pytest.fixture
def behavior_applier():
    """Fixture providing RoleBehaviorApplier instance"""
    return RoleBehaviorApplier()

class TestRolePropertyAdder:
    """Tests for RolePropertyAdder"""
    
    def test_add_assistant_properties(self, property_adder):
        """Test adding properties for assistant role"""
        properties = property_adder.add_properties("assistant")
        assert isinstance(properties, RoleProperties)
        
    def test_add_other_role_properties(self, property_adder):
        """Test adding properties for other roles"""
        properties = property_adder.add_properties("user")
        assert isinstance(properties, RoleProperties)
        assert properties.prompt_length is None
        assert properties.completion_length is None
        assert properties.total_length is None
        assert properties.finish_reason is None

class TestRoleBehaviorApplier:
    """Tests for RoleBehaviorApplier"""
    
    def test_system_role_behavior(self, behavior_applier):
        """Test system role content processing"""
        content = "  test content  "
        result = behavior_applier.apply_role_behavior("system", content)
        assert result == "test content"
    
    def test_function_role_behavior(self, behavior_applier):
        """Test function role content processing"""
        content = '{"test": "value"}'
        result = behavior_applier.apply_role_behavior("function", content)
        assert result == content
    
    def test_other_role_behavior(self, behavior_applier):
        """Test other role content processing"""
        content = "test content"
        result = behavior_applier.apply_role_behavior("user", content)
        assert result == content