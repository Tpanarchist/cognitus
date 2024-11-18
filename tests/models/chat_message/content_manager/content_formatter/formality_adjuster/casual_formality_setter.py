"""Sets casual formality in text content"""
from typing import Dict, List, Tuple
from pydantic import BaseModel

class CasualFormality(BaseModel):
    """Configuration for casual formality settings"""
    contractions: Dict[str, str] = {
        "are not": "aren't",
        "cannot": "can't",
        "could not": "couldn't",
        "did not": "didn't",
        "does not": "doesn't",
        "do not": "don't",
        "had not": "hadn't",
        "has not": "hasn't",
        "have not": "haven't",
        "is not": "isn't",
        "it is": "it's",
        "should not": "shouldn't",
        "that is": "that's",
        "they are": "they're",
        "was not": "wasn't",
        "were not": "weren't",
        "what is": "what's",
        "will not": "won't",
        "would not": "wouldn't",
        "you are": "you're"
    }
    casual_words: Dict[str, str] = {
        "hello": "hi",
        "goodbye": "bye",
        "please": "pls",
        "thanks": "thx",
        "approximately": "about",
        "regarding": "about",
    }
    preserve_formal_quotes: bool = True
    preserve_code_blocks: bool = True

class CasualFormalitySetter:
    """Sets casual formality in text content"""
    
    def __init__(self, config: CasualFormality = None):
        self.config = config or CasualFormality()
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile word patterns for replacement"""
        # Sort by length (longest first) to handle overlapping patterns
        self.formal_patterns = sorted(
            list(self.config.contractions.items()) + 
            list(self.config.casual_words.items()),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
    def _preserve_special_content(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Preserve quotes and code blocks"""
        import re
        preserved = {}
        result = text
        
        if self.config.preserve_formal_quotes:
            # Preserve quoted content
            for i, match in enumerate(re.finditer(r'"([^"]+)"', result)):
                marker = f"\x00QUOTE{i}\x00"
                preserved[marker] = match.group(0)
                result = result.replace(match.group(0), marker)
                
        if self.config.preserve_code_blocks:
            # Preserve code blocks
            for i, match in enumerate(re.finditer(r'`[^`]+`|```[\s\S]*?```', result)):
                marker = f"\x00CODE{i}\x00"
                preserved[marker] = match.group(0)
                result = result.replace(match.group(0), marker)
                
        return result, preserved
        
    def set_casual_formality(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Convert text to casual formality
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (casual text, stats about changes)
        """
        stats = {
            "contractions_applied": 0,
            "casual_words_applied": 0
        }
        
        # Preserve special content
        result, preserved = self._preserve_special_content(text)
        
        # Apply patterns
        for formal, casual in self.formal_patterns:
            if formal in result:
                count = result.count(formal)
                result = result.replace(formal, casual)
                
                # Track statistics
                if formal in self.config.contractions:
                    stats["contractions_applied"] += count
                else:
                    stats["casual_words_applied"] += count
                    
        # Restore preserved content
        for marker, content in preserved.items():
            result = result.replace(marker, content)
            
        return result, stats