"""Handles replacement of profanity in text"""
from typing import Optional, Dict
import re
from pydantic import BaseModel
from .blacklist_loader import BlacklistLoader, BlacklistConfig

class ReplacementConfig(BaseModel):
    """Configuration for profanity replacement"""
    replacement_char: str = "*"
    preserve_length: bool = True
    whole_words_only: bool = True
    custom_replacements: Dict[str, str] = {}

class ProfanityReplacer:
    """Handles replacement of profanity in text"""
    
    def __init__(
        self,
        blacklist_config: Optional[BlacklistConfig] = None,
        replacement_config: Optional[ReplacementConfig] = None
    ):
        self.blacklist_loader = BlacklistLoader(blacklist_config)
        self.config = replacement_config or ReplacementConfig()
        
    def _get_replacement(self, word: str) -> str:
        """Get replacement for a blacklisted word"""
        if word in self.config.custom_replacements:
            return self.config.custom_replacements[word]
            
        if self.config.preserve_length:
            return self.config.replacement_char * len(word)
        return self.config.replacement_char
        
    def replace_profanity(self, text: str) -> tuple[str, Dict[str, int]]:
        """
        Replace profanity in text
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (cleaned text, dict of {word: count} of replaced words)
        """
        replaced_counts: Dict[str, int] = {}
        cleaned_text = text
        
        blacklist = self.blacklist_loader.get_blacklist()
        
        if self.config.whole_words_only:
            # Replace only whole words
            for word in blacklist:
                pattern = fr'\b{re.escape(word)}\b'
                if matches := re.finditer(pattern, cleaned_text, 
                    flags=0 if self.config.blacklist_loader.config.case_sensitive 
                    else re.IGNORECASE):
                    
                    count = 0
                    for match in matches:
                        count += 1
                        matched_word = match.group()
                        replacement = self._get_replacement(matched_word)
                        cleaned_text = cleaned_text[:match.start()] + replacement + cleaned_text[match.end():]
                    
                    if count > 0:
                        replaced_counts[word] = count
        else:
            # Replace all occurrences
            for word in blacklist:
                if word in cleaned_text:
                    replacement = self._get_replacement(word)
                    count = cleaned_text.count(word)
                    cleaned_text = cleaned_text.replace(word, replacement)
                    replaced_counts[word] = count
                    
        return cleaned_text, replaced_counts