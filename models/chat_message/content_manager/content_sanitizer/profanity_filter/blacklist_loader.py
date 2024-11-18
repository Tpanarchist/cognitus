"""Loads and manages profanity blacklists"""
from typing import Set, Optional
from pathlib import Path
import json
from pydantic import BaseModel

class BlacklistConfig(BaseModel):
    """Configuration for blacklist loading"""
    default_blacklist: Set[str] = set()
    custom_blacklist: Set[str] = set()
    locale: str = "en"
    case_sensitive: bool = False

class BlacklistLoader:
    """Loads and manages profanity blacklists"""
    
    def __init__(self, config: Optional[BlacklistConfig] = None):
        self.config = config or BlacklistConfig()
        self._combined_blacklist: Set[str] = set()
        self._initialize_blacklist()
    
    def _initialize_blacklist(self) -> None:
        """Initialize the combined blacklist"""
        self._combined_blacklist = self.config.default_blacklist.union(
            self.config.custom_blacklist
        )
        if not self.config.case_sensitive:
            self._combined_blacklist = {
                word.lower() for word in self._combined_blacklist
            }
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load blacklist from a file
        
        Args:
            file_path: Path to blacklist file (txt or json)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Blacklist file not found: {file_path}")
            
        if path.suffix == '.json':
            with path.open('r', encoding='utf-8') as f:
                words = set(json.load(f))
        else:
            with path.open('r', encoding='utf-8') as f:
                words = {line.strip() for line in f if line.strip()}
                
        self.config.custom_blacklist.update(words)
        self._initialize_blacklist()
    
    def add_words(self, words: Set[str]) -> None:
        """Add words to custom blacklist"""
        self.config.custom_blacklist.update(words)
        self._initialize_blacklist()
    
    def remove_words(self, words: Set[str]) -> None:
        """Remove words from custom blacklist"""
        self.config.custom_blacklist.difference_update(words)
        self._initialize_blacklist()
    
    def is_blacklisted(self, word: str) -> bool:
        """Check if a word is blacklisted"""
        check_word = word if self.config.case_sensitive else word.lower()
        return check_word in self._combined_blacklist
    
    def get_blacklist(self) -> Set[str]:
        """Get current combined blacklist"""
        return self._combined_blacklist.copy()