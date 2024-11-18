"""Fetches and manages completion finish reasons"""
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel

class FinishReason(str, Enum):
    """Enumeration of possible finish reasons"""
    STOP = "stop"              # Natural completion
    LENGTH = "length"          # Max tokens reached
    FUNCTION_CALL = "function_call"  # Function call completed
    CONTENT_FILTER = "content_filter"  # Content filter triggered
    ERROR = "error"            # Error during completion
    INCOMPLETE = "incomplete"  # Stream interrupted
    TIME_LIMIT = "time_limit"  # Time limit exceeded
    UNKNOWN = "unknown"        # Unknown reason

class FinishReasonMetadata(BaseModel):
    """Metadata associated with finish reasons"""
    reason: FinishReason
    timestamp: float
    token_count: Optional[int] = None
    error_details: Optional[str] = None
    filter_flags: Optional[Dict[str, bool]] = None

class FinishReasonFetcher:
    """Fetches and manages completion finish reasons"""
    
    @staticmethod
    def get_finish_reason(raw_reason: str) -> FinishReason:
        """
        Get standardized finish reason from raw input
        
        Args:
            raw_reason: Raw finish reason string
            
        Returns:
            Standardized FinishReason enum value
        """
        # Normalize input
        normalized = raw_reason.lower().strip()
        
        # Map common variations to standard reasons
        reason_map = {
            "stop": FinishReason.STOP,
            "stopped": FinishReason.STOP,
            "completed": FinishReason.STOP,
            "max_length": FinishReason.LENGTH,
            "length": FinishReason.LENGTH,
            "max_tokens": FinishReason.LENGTH,
            "function_call": FinishReason.FUNCTION_CALL,
            "function": FinishReason.FUNCTION_CALL,
            "content_filter": FinishReason.CONTENT_FILTER,
            "filtered": FinishReason.CONTENT_FILTER,
            "error": FinishReason.ERROR,
            "incomplete": FinishReason.INCOMPLETE,
            "interrupted": FinishReason.INCOMPLETE,
            "time_limit": FinishReason.TIME_LIMIT,
            "timeout": FinishReason.TIME_LIMIT
        }
        
        return reason_map.get(normalized, FinishReason.UNKNOWN)
    
    @staticmethod
    def create_metadata(
        reason: str,
        timestamp: float,
        token_count: Optional[int] = None,
        error_details: Optional[str] = None,
        filter_flags: Optional[Dict[str, bool]] = None
    ) -> FinishReasonMetadata:
        """
        Create metadata for a finish reason
        
        Args:
            reason: Raw finish reason string
            timestamp: Completion timestamp
            token_count: Optional token count
            error_details: Optional error details
            filter_flags: Optional content filter flags
            
        Returns:
            FinishReasonMetadata object
        """
        finish_reason = FinishReasonFetcher.get_finish_reason(reason)
        
        return FinishReasonMetadata(
            reason=finish_reason,
            timestamp=timestamp,
            token_count=token_count,
            error_details=error_details,
            filter_flags=filter_flags
        )