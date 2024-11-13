"""Role metadata handling components for message handling"""

from .role_property_adder import RolePropertyAdder, RoleProperties
from .role_specific_behavior_applier import RoleBehaviorApplier

__all__ = [
    "RolePropertyAdder",
    "RoleProperties",
    "RoleBehaviorApplier",
]