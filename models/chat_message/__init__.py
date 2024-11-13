"""Chat message components and handlers"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .role_handler import RoleHandler, RoleMetadata, RoleProperties

def now_tz():
    """Get current datetime with timezone"""
    return datetime.now(datetime.timezone.utc)

class ChatMessage(BaseModel):
    """Base chat message model"""
    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[str] = None
    received_at: datetime = Field(default_factory=now_tz)
    finish_reason: Optional[str] = None
    prompt_length: Optional[int] = None
    completion_length: Optional[int] = None
    total_length: Optional[int] = None
    
    _role_handler: RoleHandler = RoleHandler()
    
    def __init__(self, **data):
        # Process role before parent initialization
        role_data = self._role_handler.process_role(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            metadata={
                "name": data.get("name"),
                "function_call": data.get("function_call")
            }
        )
        if role_data:
            data.update(role_data)
        super().__init__(**data)
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """Custom serialization to handle role-specific data"""
        exclude = kwargs.pop("exclude", set())
        exclude.add("_role_handler")
        return super().model_dump(*args, exclude=exclude, **kwargs)

__all__ = ["ChatMessage"]