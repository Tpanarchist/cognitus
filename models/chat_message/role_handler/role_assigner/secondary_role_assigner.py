"""Handles assignment of secondary role attributes"""
from typing import Dict, Optional
from pydantic import BaseModel

class RoleMetadata(BaseModel):
    """Metadata for secondary roles"""
    name: Optional[str] = None
    function_call: Optional[str] = None

class SecondaryRoleAssigner:
    """Handles assignment of secondary role attributes"""
    
    def assign_metadata(self, role: str, metadata: Dict) -> RoleMetadata:
        """Assign secondary role metadata based on role type"""
        if role == "function":
            return RoleMetadata(
                name=metadata.get("name"),
                function_call=metadata.get("function_call")
            )
        return RoleMetadata()