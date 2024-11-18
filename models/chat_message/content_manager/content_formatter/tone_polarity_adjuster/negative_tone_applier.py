"""Applies negative tone to text content"""
import random
from typing import Dict, List, Tuple, Optional
import re
from pydantic import BaseModel

class NegativeToneConfig(BaseModel):
    """Configuration for negative tone settings"""
    word_replacements: Dict[str, str] = {
        "good": "mediocre",
        "great": "barely adequate",
        "excellent": "passable",
        "amazing": "unremarkable",
        "perfect": "acceptable",
        "easy": "deceptively simple",
        "simple": "oversimplified",
        "helpful": "marginally useful",
        "successful": "barely successful",
        "improve": "patch",
    }
    
    phrase_additions: Dict[str, List[str]] = {
        "can": ["but probably shouldn't", "though it's risky"],
        "will": ["eventually", "somehow"],
        "should": ["if you must", "I suppose"],
    }
    
    negative_prefixes: List[str] = [
        "Unfortunately, ",
        "Regrettably, ",
        "As expected, ",
        "Predictably, ",
        "Not surprisingly, ",
    ]
    
    preserve_code_blocks: bool = True
    preserve_technical_terms: bool = True
    maintain_professionalism: bool = True

class NegativeToneApplier:
    """Applies negative tone to text"""
    
    def __init__(self, config: Optional[NegativeToneConfig] = None):
        self.config = config or NegativeToneConfig()
        
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
            # Preserve technical terms
            for i, match in enumerate(re.finditer(r'\b[a-z]+(?:[A-Z][a-z]*)+\b|\b[a-z]+(?:_[a-z]+)+\b', result)):
                marker = f"\x00TECH{i}\x00"
                preserved[marker] = match.group(0)
                result = result.replace(match.group(0), marker)
                
        return result, preserved
        
    def _add_negative_prefix(self, text: str) -> Tuple[str, bool]:
        """Add negative prefix to sentences where appropriate"""
        import random
        
        # Check if sentence already starts with a negative prefix
        for prefix in self.config.negative_prefixes:
            if text.startswith(prefix):
                return text, False
                
        # Add prefix for positive starts
        positive_starts = ["great", "good", "excellent", "perfect", "amazing"]
        for pos in positive_starts:
            if text.lower().startswith(pos):
                prefix = random.choice(self.config.negative_prefixes)
                return f"{prefix}{text}", True
                
        return text, False
        
    def _add_doubtful_phrases(self, text: str, word: str) -> str:
        """Add doubtful phrases to positive words"""
        if word in self.config.phrase_additions:
            addition = random.choice(self.config.phrase_additions[word])
            return f"{text} {addition}"
        return text
        
    def apply_negative_tone(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Apply negative tone to text
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (negative text, stats about changes)
        """
        stats = {
            "words_replaced": 0,
            "phrases_added": 0,
            "prefixes_added": 0
        }
        
        # Preserve special content
        result, preserved = self._preserve_special_content(text)
        
        # Replace positive words with negative alternatives
        for positive, negative in self.config.word_replacements.items():
            pattern = fr'\b{positive}\b'
            matches = re.finditer(pattern, result, re.IGNORECASE)
            for match in matches:
                original_word = match.group(0)
                # Maintain original capitalization
                if original_word[0].isupper():
                    replacement = negative.capitalize()
                else:
                    replacement = negative
                    
                result = result[:match.start()] + replacement + result[match.end():]
                stats["words_replaced"] += 1
                
                # Add doubtful phrases where appropriate
                result = self._add_doubtful_phrases(result, positive)
                stats["phrases_added"] += 1
                
        # Add negative prefixes to sentences
        if self.config.maintain_professionalism:
            sentences = re.split(r'([.!?]\s+)', result)
            modified_sentences = []
            for sentence in sentences:
                if sentence.strip():
                    modified, added = self._add_negative_prefix(sentence)
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