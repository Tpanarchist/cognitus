"""Handles logging of role validation errors"""
import logging
from typing import Optional

class RoleErrorLogger:
    """Handles logging of role validation errors"""
    
    def __init__(self):
        self.logger = logging.getLogger("cognitus.role_validator")
        
    def log_invalid_role(self, role: str, context: Optional[str] = None) -> None:
        """Log invalid role error with context"""
        msg = f"Invalid role '{role}' provided"
        if context:
            msg += f" in {context}"
        self.logger.error(msg)