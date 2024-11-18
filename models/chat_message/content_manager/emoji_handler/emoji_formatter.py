"""Formats and modifies emoji content in text"""
import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from .emoji_extractor import EmojiExtractor, EmojiConfig

class FormatterConfig(BaseModel):
    """Configuration for emoji formatting"""
    normalize_text_emoji: bool = True
    unicode_to_text: bool = False
    text_to_unicode: bool = True
    limit_emoji: Optional[int] = None
    emoji_spacing: bool = True
    text_to_unicode_map: Dict[str, str] = {
        ":)": "😊",
        ":(": "😢",
        ":D": "😃",
        ";)": "😉",
        "<3": "❤️",
        ":P": "😛",
        ":O": "😮",
        "xD": "😆",
    }
    unicode_to_text_map: Dict[str, str] = {
        "😊": ":)",
        "😢": ":(",
        "😃": ":D",
        "😉": ";)",
        "❤️": "<3",
        "😛": ":P",
        "😮": ":O",
        "😆": "xD",
    }

class EmojiFormatter:
    """Formats and modifies emoji in text"""
    
    def __init__(
        self,
        formatter_config: Optional[FormatterConfig] = None,
        extractor_config: Optional[EmojiConfig] = None
    ):
        self.config = formatter_config or FormatterConfig()
        self.extractor = EmojiExtractor(extractor_config)
        
    def _normalize_text_emoji(self, text: str) -> str:
        """Normalize text emoji to standard forms"""
        result = text
        
        # Normalize common variations
        normalizations = {
            r':-?\)': ':)',
            r':-?\(': ':(',
            r';-?\)': ';)',
            r':-?D': ':D',
            r':-?P': ':P',
            r':-?O': ':O',
        }
        
        for pattern, replacement in normalizations.items():
            result = re.sub(pattern, replacement, result)
            
        return result
        
    def _add_emoji_spacing(self, text: str) -> str:
        """Add proper spacing around emoji"""
        result = text
        
        # Add space after emoji if followed by text
        result = re.sub(r'([\x{1F300}-\x{1F9FF}])([^\s\x{1F300}-\x{1F9FF}])', 
                       r'\1 \2', result)
        
        # Add space before emoji if preceded by text
        result = re.sub(r'([^\s\x{1F300}-\x{1F9FF}])([\x{1F300}-\x{1F9FF}])', 
                       r'\1 \2', result)
        
        return result
        
    def _convert_text_to_unicode(self, text: str) -> str:
        """Convert text emoji to unicode emoji"""
        result = text
        
        for text_emoji, unicode_emoji in self.config.text_to_unicode_map.items():
            result = result.replace(text_emoji, unicode_emoji)
            
        return result
        
    def _convert_unicode_to_text(self, text: str) -> str:
        """Convert unicode emoji to text emoji"""
        result = text
        
        for unicode_emoji, text_emoji in self.config.unicode_to_text_map.items():
            result = result.replace(unicode_emoji, text_emoji)
            
        return result
        
    def _limit_emoji_count(self, text: str, limit: int) -> str:
        """Limit the number of emoji in text"""
        if not limit:
            return text
            
        result = text
        emoji_info = self.extractor.extract_emoji(text)
        total_emoji = (emoji_info["unicode_emoji"]["count"] + 
                      emoji_info["text_emoji"]["count"])
        
        if total_emoji <= limit:
            return result
            
        # Remove excess emoji, preserving first 'limit' occurrences
        positions = (
            [(pos, True) for pos in emoji_info["unicode_emoji"]["positions"]] +
            [(pos, False) for pos in emoji_info["text_emoji"]["positions"]]
        )
        positions.sort()
        
        # Remove emoji from end to start to maintain position accuracy
        for pos, is_unicode in reversed(positions[limit:]):
            if is_unicode:
                # Remove unicode emoji (typically 1-2 characters)
                char = result[pos]
                result = result[:pos] + result[pos + len(char):]
            else:
                # Remove text emoji (match against patterns)
                for patterns in self.extractor.config.text_emoji_patterns.values():
                    for pattern in patterns:
                        match = re.match(pattern, result[pos:])
                        if match:
                            result = result[:pos] + result[pos + len(match.group()):]
                            break
                            
        return result
        
    def format_emoji(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Format emoji in text according to configuration
        
        Args:
            text: Text to format
            
        Returns:
            Tuple of (formatted text, stats about changes)
        """
        stats = {
            "text_emoji_normalized": 0,
            "text_to_unicode": 0,
            "unicode_to_text": 0,
            "emoji_limited": 0,
            "spacing_fixed": 0
        }
        
        result = text
        
        # Normalize text emoji
        if self.config.normalize_text_emoji:
            original = result
            result = self._normalize_text_emoji(result)
            stats["text_emoji_normalized"] = sum(1 for a, b in 
                zip(original, result) if a != b)
            
        # Convert between text and unicode emoji
        if self.config.text_to_unicode:
            original = result
            result = self._convert_text_to_unicode(result)
            stats["text_to_unicode"] = sum(1 for a, b in 
                zip(original, result) if a != b)
        elif self.config.unicode_to_text:
            original = result
            result = self._convert_unicode_to_text(result)
            stats["unicode_to_text"] = sum(1 for a, b in 
                zip(original, result) if a != b)
            
        # Limit emoji count
        if self.config.limit_emoji:
            original = result
            result = self._limit_emoji_count(result, self.config.limit_emoji)
            stats["emoji_limited"] = sum(1 for a, b in 
                zip(original, result) if a != b)
            
        # Fix emoji spacing
        if self.config.emoji_spacing:
            original = result
            result = self._add_emoji_spacing(result)
            stats["spacing_fixed"] = sum(1 for a, b in 
                zip(original, result) if a != b)
            
        return result, stats