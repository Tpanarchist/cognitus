"""Applies positive tone to text content"""
from typing import Dict, List, Tuple, Optional
import re
import random
from pydantic import BaseModel

class PositiveToneConfig(BaseModel):
    """Configuration for positive tone settings"""
    word_replacements: Dict[str, str] = {
        "problem": "challenge",
        "difficult": "challenging",
        "hard": "challenging",
        "fail": "attempt",
        "failed": "attempted",
        "bad": "less than ideal",
        "issue": "opportunity",
        "mistake": "learning opportunity",
        "wrong": "different",
        "impossible": "challenging",
        "terrible": "needs improvement",
    }
    
    phrase_additions: Dict[str, List[str]] = {
        "can't": ["yet", "at the moment"],
        "impossible": ["right now", "at this stage"],
        "failed": ["this time", "in this attempt"],
    }
    
    positive_prefixes: List[str] = [
        "We can ",
        "Let's try to ",
        "We could ",
        "Consider ",
        "Perhaps we can ",
    ]
    
    preserve_code_blocks: bool = True
    preserve_technical_terms: bool = True
    maintain_context: bool = True

class PositiveToneApplier:
    """Applies positive tone to text"""
    
    def __init__(self, config: Optional[PositiveToneConfig] = None):
        self.config = config or PositiveToneConfig()
        
    def _preserve_special_content(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Preserve code and technical content"""
        preserved = {}
        result = text
        
        if self.config.preserve_code_blocks:
            # Preserve code blocks and inline code
            for i, match in enumerate(re.finditer(r'`[^`]+`|```[\s\S]*?```', result)):
                marker = f"\x00CODE{i}\x00"
                preserved[marker] = match.group(0)
                result = result.replace(match.group(0), marker)
                
        if self.config.preserve_technical_terms:
            # Preserve technical terms (e.g., camelCase, snake_case, etc.)
            for i, match in enumerate(re.finditer(r'\b[a-z]+(?:[A-Z][a-z]*)+\b|\b[a-z]+(?:_[a-z]+)+\b', result)):
                marker = f"\x00TECH{i}\x00"
                preserved[marker] = match.group(0)
                result = result.replace(match.group(0), marker)
                
        return result, preserved
        
    def _add_positive_prefix(self, text: str) -> Tuple[str, bool]:
        """Add positive prefix to sentences where appropriate"""
        import random
        
        # Check if sentence already starts with a positive prefix
        for prefix in self.config.positive_prefixes:
            if text.startswith(prefix):
                return text, False
                
        # Add prefix for negative starts
        negative_starts = ["can't", "cannot", "don't", "won't", "impossible"]
        for neg in negative_starts:
            if text.lower().startswith(neg):
                prefix = random.choice(self.config.positive_prefixes)
                return f"{prefix}{text}", True
                
        return text, False
        
    def _add_hopeful_phrases(self, text: str, word: str) -> str:
        """Add hopeful phrases to negative words"""
        if word in self.config.phrase_additions:
            addition = random.choice(self.config.phrase_additions[word])
            return f"{text} {addition}"
        return text
        
    def apply_positive_tone(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Apply positive tone to text
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (positive text, stats about changes)
        """
        stats = {
            "words_replaced": 0,
            "phrases_added": 0,
            "prefixes_added": 0
        }
        
        # Preserve special content
        result, preserved = self._preserve_special_content(text)
        
        # Replace negative words with positive alternatives
        for negative, positive in self.config.word_replacements.items():
            pattern = fr'\b{negative}\b'
            matches = re.finditer(pattern, result, re.IGNORECASE)
            for match in matches:
                original_word = match.group(0)
                # Maintain original capitalization
                if original_word[0].isupper():
                    replacement = positive.capitalize()
                else:
                    replacement = positive
                    
                result = result[:match.start()] + replacement + result[match.end():]
                stats["words_replaced"] += 1
                
                # Add hopeful phrases where appropriate
                result = self._add_hopeful_phrases(result, negative)
                stats["phrases_added"] += 1
                
        # Add positive prefixes to sentences
        sentences = re.split(r'([.!?]\s+)', result)
        modified_sentences = []
        for sentence in sentences:
            if sentence.strip():
                modified, added = self._add_positive_prefix(sentence)
                if added:
                    stats["prefixes_added"] += 1
                modified_sentences.append(modified)
            else:
                modified_sentences.append(sentence)
                
        result = ''.join(modified_sentences)
        
        # Restore preserved content
        for marker, content in preserved.items():
            result = result.replace(marker, content)
            
        return result, stats