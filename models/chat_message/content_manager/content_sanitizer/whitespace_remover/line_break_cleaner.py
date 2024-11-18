"""Handles normalization of line breaks"""
from typing import Dict
import re
from pydantic import BaseModel

class LineBreakConfig(BaseModel):
    """Configuration for line break cleaning"""
    max_consecutive_breaks: int = 2
    normalize_line_endings: bool = True
    preserve_markdown_breaks: bool = False
    preserve_code_blocks: bool = True

class LineBreakCleaner:
    """Handles normalization of line breaks"""
    
    def __init__(self, config: LineBreakConfig = None):
        self.config = config or LineBreakConfig()
        
    def _preserve_code_blocks(self, text: str) -> tuple[str, Dict[str, str]]:
        """Temporarily replace code blocks with markers"""
        preserved = {}
        counter = 0
        
        def replace(match):
            nonlocal counter
            marker = f"\x00CODE{counter}\x00"
            preserved[marker] = match.group(0)
            counter += 1
            return marker
            
        # Preserve code blocks
        result = re.sub(r'```[\s\S]*?```', replace, text)
        return result, preserved
        
    def clean_breaks(self, text: str) -> tuple[str, Dict[str, int]]:
        """
        Clean and normalize line breaks
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (cleaned text, stats about changes made)
        """
        stats = {
            "breaks_removed": 0,
            "breaks_normalized": 0
        }
        
        result = text
        preserved_code = {}
        
        # Preserve code blocks if configured
        if self.config.preserve_code_blocks:
            result, preserved_code = self._preserve_code_blocks(result)
            
        # Normalize line endings if configured
        if self.config.normalize_line_endings:
            original_length = len(result)
            result = result.replace('\r\n', '\n').replace('\r', '\n')
            stats["breaks_normalized"] = original_length - len(result)
            
        # Preserve markdown line breaks if configured
        if self.config.preserve_markdown_breaks:
            # Temporarily replace markdown line breaks
            result = result.replace('  \n', '\x01')
            
        # Handle consecutive breaks
        if self.config.max_consecutive_breaks > 0:
            pattern = r'\n{' + str(self.config.max_consecutive_breaks + 1) + r',}'
            while re.search(pattern, result):
                original_length = len(result)
                result = re.sub(pattern, '\n' * self.config.max_consecutive_breaks, result)
                stats["breaks_removed"] += original_length - len(result)
                
        # Restore markdown line breaks if they were preserved
        if self.config.preserve_markdown_breaks:
            result = result.replace('\x01', '  \n')
            
        # Restore code blocks if they were preserved
        for marker, code in preserved_code.items():
            result = result.replace(marker, code)
            
        return result, stats