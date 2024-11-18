"""Calculates and validates completion lengths"""
from typing import Dict, Optional, Union, List
from pydantic import BaseModel
from datetime import datetime

class CompletionLengthConfig(BaseModel):
    """Configuration for completion length calculation"""
    count_tokens: bool = True
    count_chars: bool = True
    track_generation_speed: bool = True
    max_tokens: Optional[int] = None
    max_chars: Optional[int] = None
    min_tokens: Optional[int] = None
    min_chars: Optional[int] = None

class GenerationStats(BaseModel):
    """Statistics about the generation process"""
    start_time: datetime
    end_time: Optional[datetime] = None
    tokens_per_second: Optional[float] = None
    chars_per_second: Optional[float] = None
    duration_seconds: Optional[float] = None

class CompletionLength(BaseModel):
    """Length details for a completion"""
    token_count: Optional[int] = None
    char_count: int
    content_type: str = "text"
    generation_stats: Optional[GenerationStats] = None
    metadata: Dict[str, Union[int, float]] = {}

class CompletionLengthCalculator:
    """Calculates and validates completion lengths"""
    
    def __init__(self, config: Optional[CompletionLengthConfig] = None):
        self.config = config or CompletionLengthConfig()
        
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count for text"""
        # Basic estimation: ~4 chars per token on average
        return len(text) // 4
        
    def begin_tracking(self) -> GenerationStats:
        """Begin tracking generation statistics"""
        return GenerationStats(start_time=datetime.now())
        
    def _calculate_generation_stats(
        self,
        stats: GenerationStats,
        token_count: Optional[int],
        char_count: int
    ) -> GenerationStats:
        """Calculate final generation statistics"""
        stats.end_time = datetime.now()
        stats.duration_seconds = (
            stats.end_time - stats.start_time
        ).total_seconds()
        
        if token_count:
            stats.tokens_per_second = token_count / stats.duration_seconds
            
        stats.chars_per_second = char_count / stats.duration_seconds
        
        return stats
        
    def calculate_length(
        self,
        text: str,
        generation_stats: Optional[GenerationStats] = None,
        content_type: str = "text"
    ) -> CompletionLength:
        """
        Calculate completion length details
        
        Args:
            text: Completion text to analyze
            generation_stats: Optional generation tracking stats
            content_type: Type of content being measured
            
        Returns:
            CompletionLength object with details
        """
        char_count = len(text)
        token_count = self._estimate_token_count(text) if self.config.count_tokens else None
        
        metadata = {
            "lines": text.count('\n') + 1,
            "words": len(text.split()),
            "whitespace_chars": sum(c.isspace() for c in text),
            "special_chars": sum(not c.isalnum() and not c.isspace() for c in text),
        }
        
        if generation_stats and self.config.track_generation_speed:
            generation_stats = self._calculate_generation_stats(
                generation_stats,
                token_count,
                char_count
            )
            
        return CompletionLength(
            token_count=token_count,
            char_count=char_count,
            content_type=content_type,
            generation_stats=generation_stats,
            metadata=metadata
        )
        
    def validate_length(
        self,
        completion_length: CompletionLength
    ) -> tuple[bool, Dict[str, str]]:
        """
        Validate completion length against configured limits
        
        Args:
            completion_length: CompletionLength to validate
            
        Returns:
            Tuple of (is_valid, dict of validation errors)
        """
        validation_errors = {}
        
        # Check token count if configured
        if self.config.count_tokens and completion_length.token_count:
            if self.config.max_tokens and completion_length.token_count > self.config.max_tokens:
                validation_errors["tokens_max"] = (
                    f"Token count ({completion_length.token_count}) exceeds "
                    f"maximum ({self.config.max_tokens})"
                )
            if self.config.min_tokens and completion_length.token_count < self.config.min_tokens:
                validation_errors["tokens_min"] = (
                    f"Token count ({completion_length.token_count}) below "
                    f"minimum ({self.config.min_tokens})"
                )
                
        # Check character count if configured
        if self.config.max_chars and completion_length.char_count > self.config.max_chars:
            validation_errors["chars_max"] = (
                f"Character count ({completion_length.char_count}) exceeds "
                f"maximum ({self.config.max_chars})"
            )
        if self.config.min_chars and completion_length.char_count < self.config.min_chars:
            validation_errors["chars_min"] = (
                f"Character count ({completion_length.char_count}) below "
                f"minimum ({self.config.min_chars})"
            )
            
        return len(validation_errors) == 0, validation_errors