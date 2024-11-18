"""Removes excessive punctuation from text"""
import re
from typing import Dict, Set
from pydantic import BaseModel

class ExcessConfig(BaseModel):
    """Configuration for excess punctuation removal"""
    max_consecutive: Dict[str, int] = {
        '!': 3,  # Allow up to 3 exclamation marks
        '?': 2,  # Allow up to 2 question marks
        '.': 3,  # Allow up to 3 dots (ellipsis)
        '-': 2,  # Allow up to 2 hyphens
    }
    preserve_markdown: bool = True
    preserve_urls: bool = True
    preserve_code: bool = True

class ExcessPunctuationRemover:
    """Removes excessive punctuation"""
    
    def __init__(self, config: ExcessConfig = None):
        self.config = config or ExcessConfig()
        
    def _preserve_special_content(self, text: str) -> tuple[str, Dict[str, Set[str]]]:
        """Preserve special content like code, URLs, etc."""
        preserved = {
            'code': set(),
            'urls': set(),
            'markdown': set()
        }
        result = text
        
        if self.config.preserve_code:
            # Preserve inline and block code
            code_blocks = re.finditer(r'(`[^`]+`|```[\s\S]*?```)', result)
            for i, match in enumerate(code_blocks):
                marker = f"\x00CODE{i}\x00"
                preserved['code'].add((marker, match.group(0)))
                result = result.replace(match.group(0), marker)
                
        if self.config.preserve_urls:
            # Preserve URLs
            urls = re.finditer(r'(https?://\S+)', result)
            for i, match in enumerate(urls):
                marker = f"\x00URL{i}\x00"
                preserved['urls'].add((marker, match.group(0)))
                result = result.replace(match.group(0), marker)
                
        if self.config.preserve_markdown:
            # Preserve markdown syntax
            markdown_patterns = [
                r'(\*\*[\s\S]*?\*\*)',  # Bold
                r'(__[\s\S]*?__)',      # Bold
                r'(\*[\s\S]*?\*)',      # Italic
                r'(_[\s\S]*?_)',        # Italic
                r'(~~[\s\S]*?~~)',      # Strikethrough
            ]
            for pattern in markdown_patterns:
                markdown = re.finditer(pattern, result)
                for i, match in enumerate(markdown):
                    marker = f"\x00MD{i}\x00"
                    preserved['markdown'].add((marker, match.group(0)))
                    result = result.replace(match.group(0), marker)
                    
        return result, preserved
        
    def _restore_special_content(
        self,
        text: str,
        preserved: Dict[str, Set[str]]
    ) -> str:
        """Restore preserved special content"""
        result = text
        
        # Restore in reverse order: markdown, urls, code
        for marker_type in ['markdown', 'urls', 'code']:
            for marker, content in preserved[marker_type]:
                result = result.replace(marker, content)
                
        return result
        
    def remove_excess(self, text: str) -> tuple[str, Dict[str, int]]:
        """
        Remove excessive punctuation from text
        
        Args:
            text: Text to process
            
        Returns:
            Tuple of (cleaned text, stats about removals)
        """
        stats = {mark: 0 for mark in self.config.max_consecutive.keys()}
        
        # Preserve special content
        result, preserved = self._preserve_special_content(text)
        
        # Process each punctuation mark
        for mark, max_count in self.config.max_consecutive.items():
            pattern = f'\\{mark}' * (max_count + 1) + '+'
            while True:
                match = re.search(pattern, result)
                if not match:
                    break
                    
                original_len = len(match.group(0))
                replacement = mark * max_count
                result = result[:match.start()] + replacement + result[match.end():]
                stats[mark] += original_len - max_count
                
        # Restore preserved content
        result = self._restore_special_content(result, preserved)
        
        return result, stats