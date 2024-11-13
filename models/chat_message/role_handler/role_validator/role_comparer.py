"""Validates roles against allowed options"""
from typing import Optional
from .valid_role_fetcher import ValidRoleFetcher, ValidRoles

class RoleComparer:
    """Validates roles against allowed options"""
    
    def __init__(self):
        self.valid_roles = ValidRoleFetcher.get_valid_roles()
    
    def is_valid_role(self, role: str) -> bool:
        """Check if role is valid"""
        return role in self.valid_roles
    
    def get_role_type(self, role: str) -> Optional[ValidRoles]:
        """Get enum type for role if valid"""
        try:
            return ValidRoles(role)
        except ValueError:
            return None