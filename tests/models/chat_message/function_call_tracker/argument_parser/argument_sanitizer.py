"""Sanitizes and normalizes function arguments"""
from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel

class SanitizationConfig(BaseModel):
    """Configuration for argument sanitization"""
    strip_strings: bool = True
    normalize_booleans: bool = True
    convert_numeric_strings: bool = True
    normalize_none: bool = True
    remove_empty: bool = False
    escape_html: bool = False
    max_string_length: Optional[int] = None

class ArgumentSanitizer:
    """Sanitizes and normalizes function arguments"""
    
    def __init__(self, config: Optional[SanitizationConfig] = None):
        self.config = config or SanitizationConfig()
        
    def _sanitize_string(self, value: str) -> Tuple[str, bool]:
        """
        Sanitize string value
        
        Returns:
            Tuple of (sanitized value, whether changes were made)
        """
        original = value
        result = value
        
        if self.config.strip_strings:
            result = result.strip()
            
        if self.config.escape_html:
            result = (
                result.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;")
            )
            
        if self.config.max_string_length:
            result = result[:self.config.max_string_length]
            
        return result, result != original
    
    def _normalize_value(self, value: Any) -> Tuple[Any, Optional[str]]:
        """
        Normalize a single value based on configuration
        
        Returns:
            Tuple of (normalized value, description of change if any)
        """
        if value is None and self.config.normalize_none:
            return None, None
            
        if isinstance(value, str):
            # Handle empty strings
            if not value and self.config.remove_empty:
                return None, "removed empty string"
                
            # Try numeric conversion
            if self.config.convert_numeric_strings:
                try:
                    if "." in value:
                        return float(value), "converted to float"
                    return int(value), "converted to integer"
                except ValueError:
                    pass
                    
            # Try boolean conversion
            if self.config.normalize_booleans:
                lower_value = value.lower().strip()
                if lower_value in ("true", "1", "yes", "on"):
                    return True, "converted to boolean"
                if lower_value in ("false", "0", "no", "off"):
                    return False, "converted to boolean"
                    
            # Apply string sanitization
            sanitized, changed = self._sanitize_string(value)
            if changed:
                return sanitized, "sanitized string"
                
        return value, None
    
    def sanitize_arguments(
        self,
        kwargs: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Sanitize function arguments
        
        Args:
            kwargs: Dictionary of keyword arguments
            
        Returns:
            Tuple of (sanitized arguments, changes made)
        """
        sanitized = {}
        changes = {}
        
        for key, value in kwargs.items():
            # Handle nested dictionaries
            if isinstance(value, dict):
                nested_sanitized, nested_changes = self.sanitize_arguments(value)
                if nested_changes:
                    changes[key] = f"nested changes: {nested_changes}"
                sanitized[key] = nested_sanitized
                continue
                
            # Handle lists/tuples
            if isinstance(value, (list, tuple)):
                sanitized_list = []
                list_changes = []
                for i, item in enumerate(value):
                    normalized, change = self._normalize_value(item)
                    if change:
                        list_changes.append(f"item {i}: {change}")
                    sanitized_list.append(normalized)
                if list_changes:
                    changes[key] = f"list changes: {list_changes}"
                sanitized[key] = sanitized_list
                continue
                
            # Handle single values
            normalized, change = self._normalize_value(value)
            if change:
                changes[key] = change
            sanitized[key] = normalized
            
        return sanitized, changes