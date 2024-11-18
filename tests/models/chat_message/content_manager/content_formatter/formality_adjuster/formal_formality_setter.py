"""Sets formal formality in text content"""
from typing import Dict, List, Tuple
import re
from pydantic import BaseModel

class FormalFormality(BaseModel):
    """Configuration for formal formality settings"""
    expand_contractions: Dict[str, str] = {
        "aren't": "are not",
        "can't": "cannot",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hasn't": "has not",
        "haven't": "have not",
        "isn't": "is not",
        "it's": "it is",
        "shouldn't": "should not",
        "that's": "that is",
        "they're": "they are",
        "wasn't": "was not",
        "weren't": "were not",
        "what's": "what is",
        "won't": "will not",
        "wouldn't": "would not",
        "you're": "you are"
    }
    formal_words: Dict[str, str] = {
        "hi": "hello",
        "hey": "hello",
        "bye": "goodbye",
        "pls": "please",
        "thx": "thanks",
        "about": "regarding",
        "ok": "acceptable",
    }
    capitalize_sentences: bool = True
    standardize_greetings: bool = True
    preserve_code_blocks: bool = True

class FormalFormalitySetter:
    """Sets formal formality in text content"""
    
    def __init__(self, config: FormalFormality = None):
        self.config = config or FormalFormality()
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile word patterns for replacement"""
        # Sort by length (longest first) to handle overlapping patterns
        self.casual_patterns = sorted(
            list(self.config.expand_contractions.items()) + 
            list(self.config.formal_words.items()),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
    def _preserve_code_blocks(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Preserve code blocks from modification"""
        import re
        preserved = {}
        result = text
        
        if self.config.preserve_code_blocks:
            for i, match in enumerate(re.finditer(r'`[^`]+`|```[\s\S]*?```', result)):
                marker = f"\x00CODE{i}\x00"
                preserved[marker] = match.group(0)
                result = result.replace(match.group(0), marker)
                
        return result, preserved
        
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize the first letter of each sentence"""
        import re
        
        def capitalize_match(match):
            return match.group(1) + match.group(2).upper() + match.group(3)
            
        # Pattern matches: (end of previous sentence or start) (space) (first letter)
        pattern = r'([.!?]\s+|^)(\s*)([a-z])'
        return re.sub(pattern, capitalize_match, text)
        
    def _standardize_greetings(self, text: str) -> str:
        """Standardize common greetings to formal versions"""
        import re
        greetings_map = {
            r'\bhi\b': 'Hello',
            r'\bhey\b': 'Hello',
            r'\bbye\b': 'Goodbye',
            r'\bsee ya\b': 'Goodbye',
        }
        
        result = text
        for pattern, replacement in greetings_map.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
        
    def set_formal_formality(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Convert text to formal formality
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (formal text, stats about changes)
        """
        stats = {
            "contractions_expanded": 0,
            "formal_words_applied": 0,
            "sentences_capitalized": 0,
            "greetings_standardized": 0
        }
        
        # Preserve code blocks
        result, preserved = self._preserve_code_blocks(text)
        
        # Apply patterns
        for casual, formal in self.casual_patterns:
            if casual in result.lower():  # Case-insensitive match
                count = sum(1 for match in re.finditer(r'\b' + re.escape(casual) + r'\b', 
                                                     result, re.IGNORECASE))
                result = re.sub(r'\b' + re.escape(casual) + r'\b', 
                              formal, result, flags=re.IGNORECASE)
                
                # Track statistics
                if casual in self.config.expand_contractions:
                    stats["contractions_expanded"] += count
                else:
                    stats["formal_words_applied"] += count
                    
        # Capitalize sentences if configured
        if self.config.capitalize_sentences:
            original = result
            result = self._capitalize_sentences(result)
            stats["sentences_capitalized"] = sum(1 for a, b in 
                zip(original, result) if a != b)
            
        # Standardize greetings if configured
        if self.config.standardize_greetings:
            original = result
            result = self._standardize_greetings(result)
            stats["greetings_standardized"] = sum(1 for a, b in 
                zip(original, result) if a != b)
            
        # Restore preserved content
        for marker, content in preserved.items():
            result = result.replace(marker, content)
            
        return result, stats