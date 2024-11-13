"""Role assignment components for message handling"""

from .primary_role_setter import PrimaryRoleSetter
from .secondary_role_assigner import SecondaryRoleAssigner, RoleMetadata

__all__ = [
    "PrimaryRoleSetter",
    "SecondaryRoleAssigner",
    "RoleMetadata",
]