"""Sanitizes and normalizes function names"""
from typing import Optional, Dict
from pydantic import BaseModel
import re

class SanitizationConfig(BaseModel):
    """Configuration for function name sanitization"""
    remove_whitespace: bool = True
    normalize_case: bool = True
    normalize_separators: bool = True
    max_consecutive_underscores: int = 1
    strip_invalid_chars: bool = True
    valid_chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_."

class FunctionNameSanitizer:
    """Sanitizes and normalizes function names"""
    
    def __init__(self, config: Optional[SanitizationConfig] = None):
        self.config = config or SanitizationConfig()
        
    def _remove_whitespace(self, name: str) -> str:
        """Remove whitespace from function name"""
        if self.config.remove_whitespace:
            return "".join(name.split())
        return name
        
    def _normalize_case(self, name: str) -> str:
        """Normalize function name case"""
        if self.config.normalize_case:
            # Convert camelCase to snake_case
            name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return name
        
    def _normalize_separators(self, name: str) -> str:
        """Normalize separator characters"""
        if self.config.normalize_separators:
            # Replace multiple underscores with single
            name = re.sub(r"_+", "_", name)
            # Handle dots for namespaces
            name = re.sub(r"\.+", ".", name)
            # Remove leading/trailing separators
            name = name.strip("_").strip(".")
        return name
        
    def _strip_invalid_chars(self, name: str) -> str:
        """Remove invalid characters"""
        if self.config.strip_invalid_chars:
            return "".join(c for c in name if c in self.config.valid_chars)
        return name
        
    def sanitize_name(self, raw_name: str) -> tuple[str, Dict[str, bool]]:
        """
        Sanitize function name according to configuration
        
        Args:
            raw_name: Raw function name to sanitize
            
        Returns:
            Tuple of (sanitized name, dict of applied changes)
        """
        changes = {
            "whitespace_removed": False,
            "case_normalized": False,
            "separators_normalized": False,
            "invalid_chars_removed": False
        }
        
        result = raw_name
        
        # Apply sanitization steps
        if self.config.remove_whitespace:
            original = result
            result = self._remove_whitespace(result)
            changes["whitespace_removed"] = result != original
            
        if self.config.normalize_case:
            original = result
            result = self._normalize_case(result)
            changes["case_normalized"] = result != original
            
        if self.config.normalize_separators:
            original = result
            result = self._normalize_separators(result)
            changes["separators_normalized"] = result != original
            
        if self.config.strip_invalid_chars:
            original = result
            result = self._strip_invalid_chars(result)
            changes["invalid_chars_removed"] = result != original
            
        return result, changes