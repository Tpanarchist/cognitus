"""Applies role-specific behaviors and constraints"""
from ..role_validator.valid_role_fetcher import ValidRoles

class RoleBehaviorApplier:
    """Applies role-specific behaviors and constraints"""
    
    def apply_role_behavior(self, role: str, content: str) -> str:
        """Apply any role-specific content modifications"""
        if role == ValidRoles.SYSTEM.value:
            # System messages get stripped of leading/trailing whitespace
            return content.strip()
        elif role == ValidRoles.FUNCTION.value:
            # Function messages should be valid JSON
            # This would integrate with the content_manager component
            return content
        return content