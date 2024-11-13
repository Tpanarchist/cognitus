"""Fetches and validates available role options"""
from enum import Enum
from typing import Set

class ValidRoles(str, Enum):
    """Enumeration of valid role types"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class ValidRoleFetcher:
    """Fetches and manages valid role options"""
    
    @staticmethod
    def get_valid_roles() -> Set[str]:
        """Get set of valid role values"""
        return {role.value for role in ValidRoles}
    
    @staticmethod
    def get_default_role() -> str:
        """Get default role for messages"""
        return ValidRoles.USER.value