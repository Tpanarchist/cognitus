"""Handles removal of excessive whitespace"""
from typing import Dict
import re
from pydantic import BaseModel

class SpaceTrimConfig(BaseModel):
    """Configuration for space trimming"""
    trim_edges: bool = True
    max_consecutive_spaces: int = 1
    preserve_indentation: bool = False
    preserve_paragraph_breaks: bool = True

class ExtraSpaceTrimmer:
    """Handles removal of excessive whitespace"""
    
    def __init__(self, config: SpaceTrimConfig = None):
        self.config = config or SpaceTrimConfig()
        
    def trim_spaces(self, text: str) -> tuple[str, Dict[str, int]]:
        """
        Remove excessive whitespace from text
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (trimmed text, stats about changes made)
        """
        stats = {
            "spaces_removed": 0,
            "edges_trimmed": 0
        }
        
        result = text
        
        # Handle edge whitespace
        if self.config.trim_edges:
            original_length = len(result)
            result = result.strip()
            stats["edges_trimmed"] = original_length - len(result)
            
        # Preserve paragraph breaks if configured
        if self.config.preserve_paragraph_breaks:
            # Replace multiple newlines with a marker
            result = re.sub(r'\n\s*\n', '\n\x00\n', result)
            
        # Handle consecutive spaces
        if self.config.max_consecutive_spaces > 0:
            pattern = r' {' + str(self.config.max_consecutive_spaces + 1) + r',}'
            while re.search(pattern, result):
                original_length = len(result)
                result = re.sub(pattern, ' ' * self.config.max_consecutive_spaces, result)
                stats["spaces_removed"] += original_length - len(result)
                
        # Restore paragraph breaks if they were preserved
        if self.config.preserve_paragraph_breaks:
            result = result.replace('\x00', '\n')
            
        # Handle indentation preservation
        if not self.config.preserve_indentation:
            # Remove leading spaces from each line, except in paragraph breaks
            result = '\n'.join(
                line.lstrip() if not line.isspace() else line
                for line in result.splitlines()
            )
            
        return result, stats