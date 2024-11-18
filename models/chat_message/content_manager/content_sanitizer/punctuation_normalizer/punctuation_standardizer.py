"""Standardizes punctuation marks in text"""
from typing import Dict, Set
import re
from pydantic import BaseModel

class StandardizationConfig(BaseModel):
    """Configuration for punctuation standardization"""
    # Maps non-standard marks to standard ones
    punctuation_map: Dict[str, str] = {
        # Quotes
        '"': '"',  # Straight quotes
        '"': '"',  # Smart quotes
        '"': '"',
        ''': "'",  # Smart single quotes
        ''': "'",
        # Dashes
        '—': '-',  # Em dash
        '–': '-',  # En dash
        '―': '-',  # Horizontal bar
        # Ellipsis
        '…': '...',
        # Other
        '․': '.',  # One dot leader
        '‥': '..',  # Two dot leader
    }
    preserve_quotes_in_code: bool = True
    standardize_ellipsis: bool = True
    fix_spacing: bool = True
    
class PunctuationStandardizer:
    """Standardizes punctuation marks"""
    
    def __init__(self, config: StandardizationConfig = None):
        self.config = config or StandardizationConfig()
        
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
            
        result = re.sub(r'`[^`]+`|```[\s\S]*?```', replace, text)
        return result, preserved
        
    def _fix_spacing(self, text: str) -> str:
        """Fix spacing around punctuation marks"""
        # No space before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        # One space after punctuation
        text = re.sub(r'([.,!?;:])(?!\s|$)', r'\1 ', text)
        return text
        
    def standardize(self, text: str) -> tuple[str, Dict[str, int]]:
        """
        Standardize punctuation in text
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (standardized text, stats about changes made)
        """
        stats = {mark: 0 for mark in self.config.punctuation_map.keys()}
        result = text
        preserved_code = {}
        
        # Preserve code blocks if configured
        if self.config.preserve_quotes_in_code:
            result, preserved_code = self._preserve_code_blocks(result)
            
        # Replace non-standard punctuation
        for original, standard in self.config.punctuation_map.items():
            if original in result:
                count = result.count(original)
                result = result.replace(original, standard)
                stats[original] = count
                
        # Handle ellipsis standardization
        if self.config.standardize_ellipsis:
            # Standardize multiple dots
            result = re.sub(r'\.{2,}', '...', result)
            
        # Fix spacing if configured
        if self.config.fix_spacing:
            result = self._fix_spacing(result)
            
        # Restore code blocks
        for marker, code in preserved_code.items():
            result = result.replace(marker, code)
            
        return result, stats