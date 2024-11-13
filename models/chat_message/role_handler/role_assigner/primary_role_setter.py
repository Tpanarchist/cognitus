"""Sets and validates primary message role"""
from typing import Optional
from ..role_validator.role_comparer import RoleComparer
from ..role_validator.role_error_logger import RoleErrorLogger

class PrimaryRoleSetter:
    """Sets and validates primary message role"""
    
    def __init__(self):
        self.role_comparer = RoleComparer()
        self.error_logger = RoleErrorLogger()
    
    def set_role(self, role: str) -> Optional[str]:
        """Set primary role after validation"""
        if self.role_comparer.is_valid_role(role):
            return role
        
        self.error_logger.log_invalid_role(role, "primary role setting")
        return None