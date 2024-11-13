"""Adds role-specific properties to messages"""
from typing import Dict, Optional
from pydantic import BaseModel
from ..role_validator.valid_role_fetcher import ValidRoles

class RoleProperties(BaseModel):
    """Properties specific to different roles"""
    prompt_length: Optional[int] = None
    completion_length: Optional[int] = None
    total_length: Optional[int] = None
    finish_reason: Optional[str] = None

class RolePropertyAdder:
    """Adds role-specific properties to messages"""
    
    def add_properties(self, role: str) -> RoleProperties:
        """Add properties based on role type"""
        if role == ValidRoles.ASSISTANT.value:
            return RoleProperties()
        return RoleProperties(
            prompt_length=None,
            completion_length=None,
            total_length=None,
            finish_reason=None
        )