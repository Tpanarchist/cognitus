"""Calculates and validates prompt lengths"""
from typing import Dict, Optional, List
from pydantic import BaseModel

class PromptLengthConfig(BaseModel):
    """Configuration for prompt length calculation"""
    count_tokens: bool = True
    count_chars: bool = True
    max_tokens: Optional[int] = None
    max_chars: Optional[int] = None
    track_components: bool = True
    include_system: bool = True
    include_functions: bool = True

class ComponentLength(BaseModel):
    """Length details for a message component"""
    token_count: Optional[int] = None
    char_count: int
    component_type: str
    metadata: Dict[str, int] = {}

class PromptLengthCalculator:
    """Calculates and validates prompt lengths"""
    
    def __init__(self, config: Optional[PromptLengthConfig] = None):
        self.config = config or PromptLengthConfig()
        
    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text
        
        Note: This is a basic estimation. In practice, you'd want to use
        the actual tokenizer from your LLM (like tiktoken for OpenAI).
        """
        # Basic estimation: ~4 chars per token on average
        return len(text) // 4
        
    def _calculate_component_length(
        self,
        text: str,
        component_type: str
    ) -> ComponentLength:
        """Calculate length details for a message component"""
        char_count = len(text)
        token_count = self._estimate_token_count(text) if self.config.count_tokens else None
        
        metadata = {
            "whitespace_chars": sum(c.isspace() for c in text),
            "special_chars": sum(not c.isalnum() and not c.isspace() for c in text),
        }
        
        return ComponentLength(
            token_count=token_count,
            char_count=char_count,
            component_type=component_type,
            metadata=metadata
        )
        
    def calculate_lengths(
        self,
        components: Dict[str, str]
    ) -> tuple[Dict[str, ComponentLength], Dict[str, int]]:
        """
        Calculate lengths for all prompt components
        
        Args:
            components: Dict of component name to text content
            
        Returns:
            Tuple of (component lengths dict, totals dict)
        """
        component_lengths = {}
        totals = {
            "total_tokens": 0,
            "total_chars": 0,
            "total_components": 0
        }
        
        # Calculate lengths for each component
        for name, text in components.items():
            # Skip components based on configuration
            if name == "system" and not self.config.include_system:
                continue
            if name.startswith("function") and not self.config.include_functions:
                continue
                
            length = self._calculate_component_length(text, name)
            
            if self.config.track_components:
                component_lengths[name] = length
                
            # Update totals
            totals["total_chars"] += length.char_count
            if length.token_count:
                totals["total_tokens"] += length.token_count
            totals["total_components"] += 1
            
        return component_lengths, totals
        
    def validate_lengths(
        self,
        component_lengths: Dict[str, ComponentLength],
        totals: Dict[str, int]
    ) -> tuple[bool, Dict[str, str]]:
        """
        Validate calculated lengths against configured limits
        
        Args:
            component_lengths: Dict of component lengths
            totals: Dict of total counts
            
        Returns:
            Tuple of (is_valid, dict of validation errors)
        """
        validation_errors = {}
        
        # Check token count if configured
        if self.config.count_tokens and self.config.max_tokens:
            if totals["total_tokens"] > self.config.max_tokens:
                validation_errors["tokens"] = (
                    f"Total tokens ({totals['total_tokens']}) exceeds "
                    f"maximum ({self.config.max_tokens})"
                )
                
        # Check character count if configured
        if self.config.max_chars:
            if totals["total_chars"] > self.config.max_chars:
                validation_errors["chars"] = (
                    f"Total characters ({totals['total_chars']}) exceeds "
                    f"maximum ({self.config.max_chars})"
                )
                
        return len(validation_errors) == 0, validation_errors