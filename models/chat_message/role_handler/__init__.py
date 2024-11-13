"""Role handling components for chat messages"""

from typing import Dict, Optional
from .role_validator import ValidRoles, ValidRoleFetcher, RoleComparer, RoleErrorLogger
from .role_assigner import PrimaryRoleSetter, SecondaryRoleAssigner, RoleMetadata
from .role_metadata_handler import RolePropertyAdder, RoleProperties, RoleBehaviorApplier

class RoleHandler:
    """Coordinates role handling components"""
    
    def __init__(self):
        self.role_comparer = RoleComparer()
        self.primary_setter = PrimaryRoleSetter()
        self.secondary_assigner = SecondaryRoleAssigner()
        self.property_adder = RolePropertyAdder()
        self.behavior_applier = RoleBehaviorApplier()
        self.error_logger = RoleErrorLogger()
    
    def process_role(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Process a role and return all necessary role-related data"""
        # 1. Handle empty role by using default
        if not role:
            role = ValidRoleFetcher.get_default_role()
        
        # 2. Validate role
        if not self.role_comparer.is_valid_role(role):
            self.error_logger.log_invalid_role(role)
            return None
        
        # 3. Set primary role
        validated_role = self.primary_setter.set_role(role)
        if not validated_role:
            return None
        
        # 4. Handle secondary role attributes and metadata
        role_metadata = self.secondary_assigner.assign_metadata(
            validated_role,
            metadata or {}
        )
        
        # 5. Add role properties
        properties = self.property_adder.add_properties(validated_role)
        
        # 6. Apply role-specific behaviors
        processed_content = self.behavior_applier.apply_role_behavior(
            validated_role,
            content
        )
        
        # 7. Build and return complete result
        result = {
            "role": validated_role,
            "content": processed_content,
        }
        
        # Add metadata if present
        if role_metadata:
            result.update(role_metadata.model_dump(exclude_none=True))
            
        # Add properties if present
        if properties:
            result.update(properties.model_dump(exclude_none=True))
            
        return result

__all__ = [
    "RoleHandler",
    "ValidRoles",
    "ValidRoleFetcher",
    "RoleComparer",
    "RoleErrorLogger",
    "PrimaryRoleSetter",
    "SecondaryRoleAssigner",
    "RoleMetadata",
    "RolePropertyAdder",
    "RoleProperties",
    "RoleBehaviorApplier",
]