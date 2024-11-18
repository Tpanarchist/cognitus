"""Extracts and analyzes emoji content from text"""
from typing import Dict, List, Set, Tuple
import re
from pydantic import BaseModel
import unicodedata

class EmojiConfig(BaseModel):
    """Configuration for emoji extraction"""
    extract_unicode_emoji: bool = True
    extract_text_emoji: bool = True
    categorize_emoji: bool = True
    text_emoji_patterns: Dict[str, List[str]] = {
        "happy": [r":+\)", r":+D", r"\(+:", r"=\)"],
        "sad": [r":-?\(", r"=\(", r";\("],
        "wink": [r";-?\)", r";-?D"],
        "laugh": [r"xD", r"XD"],
        "surprise": [r":o", r":O", r"=O"],
        "love": [r"<3", r"♥"],
    }

class EmojiExtractor:
    """Extracts and analyzes emoji from text"""
    
    def __init__(self, config: EmojiConfig = None):
        self.config = config or EmojiConfig()
        self._compile_patterns()
        
    def _compile_patterns(self) -> None:
        """Compile regex patterns for text emoji"""
        self.text_patterns = {
            category: re.compile('|'.join(patterns))
            for category, patterns in self.config.text_emoji_patterns.items()
        }
        
    def _is_emoji(self, char: str) -> bool:
        """Check if a character is an emoji"""
        try:
            return 'Emoji' in unicodedata.name(char)
        except ValueError:
            # Some emoji might not have 'Emoji' in their name
            # Additional checks for common emoji ranges
            code = ord(char)
            return (0x1F300 <= code <= 0x1F9FF or  # Miscellaneous Symbols and Pictographs
                    0x2600 <= code <= 0x26FF or    # Miscellaneous Symbols
                    0x2700 <= code <= 0x27BF or    # Dingbats
                    0x1F600 <= code <= 0x1F64F)    # Emoticons
                    
    def extract_unicode_emoji(self, text: str) -> List[Tuple[str, int]]:
        """Extract unicode emoji and their positions"""
        emoji_list = []
        for i, char in enumerate(text):
            if self._is_emoji(char):
                emoji_list.append((char, i))
        return emoji_list
        
    def extract_text_emoji(self, text: str) -> Dict[str, List[Tuple[str, int]]]:
        """Extract text-based emoji by category"""
        results = {category: [] for category in self.config.text_emoji_patterns}
        
        for category, pattern in self.text_patterns.items():
            for match in pattern.finditer(text):
                results[category].append((match.group(), match.start()))
                
        return results
        
    def categorize_emoji(self, emoji: str) -> str:
        """Categorize an emoji into a general emotion/meaning"""
        try:
            name = unicodedata.name(emoji).lower()
            if any(word in name for word in ['smiling', 'grin', 'joy']):
                return 'happy'
            elif any(word in name for word in ['sad', 'cry', 'tear']):
                return 'sad'
            elif any(word in name for word in ['heart', 'love']):
                return 'love'
            elif any(word in name for word in ['surprise', 'astonish']):
                return 'surprise'
            else:
                return 'other'
        except ValueError:
            return 'unknown'
            
    def extract_emoji(self, text: str) -> Dict[str, Dict]:
        """
        Extract all emoji from text with analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing extracted emoji information
        """
        results = {
            "unicode_emoji": {
                "count": 0,
                "emoji": [],
                "positions": [],
                "categories": {}
            },
            "text_emoji": {
                "count": 0,
                "by_category": {},
                "positions": []
            }
        }
        
        # Extract unicode emoji
        if self.config.extract_unicode_emoji:
            unicode_emoji = self.extract_unicode_emoji(text)
            results["unicode_emoji"]["count"] = len(unicode_emoji)
            results["unicode_emoji"]["emoji"] = [e[0] for e in unicode_emoji]
            results["unicode_emoji"]["positions"] = [e[1] for e in unicode_emoji]
            
            if self.config.categorize_emoji:
                categories = {}
                for emoji, _ in unicode_emoji:
                    category = self.categorize_emoji(emoji)
                    categories[category] = categories.get(category, 0) + 1
                results["unicode_emoji"]["categories"] = categories
                
        # Extract text emoji
        if self.config.extract_text_emoji:
            text_emoji = self.extract_text_emoji(text)
            total_count = sum(len(matches) for matches in text_emoji.values())
            results["text_emoji"]["count"] = total_count
            results["text_emoji"]["by_category"] = {
                category: [match[0] for match in matches]
                for category, matches in text_emoji.items()
                if matches
            }
            results["text_emoji"]["positions"] = [
                match[1]
                for matches in text_emoji.values()
                for match in matches
            ]
            
        return results