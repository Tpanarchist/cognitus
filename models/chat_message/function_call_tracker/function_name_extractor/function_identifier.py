"""Identifies and validates function names from chat message calls"""
from typing import Optional, Dict, List, Set
from pydantic import BaseModel
import re

class FunctionNameConfig(BaseModel):
    """Configuration for function name validation"""
    allowed_patterns: List[str] = [
        r"^[a-zA-Z_][a-zA-Z0-9_]*$",  # Standard Python function naming
        r"^[a-z][a-zA-Z0-9_]*\.[a-z][a-zA-Z0-9_]*$"  # Module.function pattern
    ]
    max_length: int = 64
    reserved_prefixes: Set[str] = {"__", "system_", "internal_"}
    case_sensitive: bool = True
    allowed_namespaces: Optional[Set[str]] = None

class FunctionIdentifier:
    """Identifies and validates function names"""
    
    def __init__(self, config: Optional[FunctionNameConfig] = None):
        self.config = config or FunctionNameConfig()
        self._compile_patterns()
        
    def _compile_patterns(self) -> None:
        """Compile regex patterns for validation"""
        self.patterns = [re.compile(pattern) for pattern in self.config.allowed_patterns]
        
    def _check_reserved_prefixes(self, name: str) -> bool:
        """Check if name uses reserved prefixes"""
        return not any(name.startswith(prefix) for prefix in self.config.reserved_prefixes)
        
    def _check_namespace(self, name: str) -> bool:
        """Check if namespace is allowed"""
        if not self.config.allowed_namespaces or "." not in name:
            return True
        namespace = name.split(".")[0]
        return namespace in self.config.allowed_namespaces
        
    def identify_function(
        self, 
        raw_name: str
    ) -> tuple[Optional[str], Dict[str, bool]]:
        """
        Identify and validate function name
        
        Args:
            raw_name: Raw function name string
            
        Returns:
            Tuple of (validated name or None, dict of validation flags)
        """
        name = raw_name if self.config.case_sensitive else raw_name.lower()
        validation = {
            "valid_length": len(name) <= self.config.max_length,
            "valid_pattern": any(pattern.match(name) for pattern in self.patterns),
            "valid_prefix": self._check_reserved_prefixes(name),
            "valid_namespace": self._check_namespace(name)
        }
        
        if all(validation.values()):
            return name, validation
        return None, validation