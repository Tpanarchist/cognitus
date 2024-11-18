"""Categorizes completion types based on finish reasons"""
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
from .finish_reason_fetcher import FinishReason, FinishReasonMetadata

class CompletionType(str, Enum):
    """Enumeration of completion types"""
    SUCCESSFUL = "successful"        # Normal, successful completion
    TRUNCATED = "truncated"         # Cut off but usable
    FAILED = "failed"               # Failed or unusable
    PARTIAL = "partial"             # Partially complete
    FILTERED = "filtered"           # Content filtered
    FUNCTION = "function"           # Function call completion

class CompletionCategory(BaseModel):
    """Category information for a completion"""
    type: CompletionType
    reason: FinishReason
    is_usable: bool
    requires_retry: bool
    meta_flags: Dict[str, bool] = {}

class CompletionTypeCategorizer:
    """Categorizes completion types based on finish reasons"""
    
    def __init__(self):
        self._init_category_mappings()
    
    def _init_category_mappings(self):
        """Initialize mappings between reasons and categories"""
        self.category_mappings = {
            FinishReason.STOP: CompletionCategory(
                type=CompletionType.SUCCESSFUL,
                reason=FinishReason.STOP,
                is_usable=True,
                requires_retry=False,
                meta_flags={"complete": True, "natural_stop": True}
            ),
            FinishReason.LENGTH: CompletionCategory(
                type=CompletionType.TRUNCATED,
                reason=FinishReason.LENGTH,
                is_usable=True,
                requires_retry=False,
                meta_flags={"complete": False, "truncated": True}
            ),
            FinishReason.FUNCTION_CALL: CompletionCategory(
                type=CompletionType.FUNCTION,
                reason=FinishReason.FUNCTION_CALL,
                is_usable=True,
                requires_retry=False,
                meta_flags={"function_call": True}
            ),
            FinishReason.CONTENT_FILTER: CompletionCategory(
                type=CompletionType.FILTERED,
                reason=FinishReason.CONTENT_FILTER,
                is_usable=False,
                requires_retry=True,
                meta_flags={"filtered": True, "requires_modification": True}
            ),
            FinishReason.ERROR: CompletionCategory(
                type=CompletionType.FAILED,
                reason=FinishReason.ERROR,
                is_usable=False,
                requires_retry=True,
                meta_flags={"error": True, "requires_retry": True}
            ),
            FinishReason.INCOMPLETE: CompletionCategory(
                type=CompletionType.PARTIAL,
                reason=FinishReason.INCOMPLETE,
                is_usable=False,
                requires_retry=True,
                meta_flags={"incomplete": True, "interrupted": True}
            ),
            FinishReason.TIME_LIMIT: CompletionCategory(
                type=CompletionType.TRUNCATED,
                reason=FinishReason.TIME_LIMIT,
                is_usable=True,
                requires_retry=False,
                meta_flags={"timeout": True, "truncated": True}
            ),
            FinishReason.UNKNOWN: CompletionCategory(
                type=CompletionType.FAILED,
                reason=FinishReason.UNKNOWN,
                is_usable=False,
                requires_retry=True,
                meta_flags={"unknown": True, "requires_investigation": True}
            )
        }
    
    def get_completion_category(
        self,
        metadata: FinishReasonMetadata
    ) -> CompletionCategory:
        """
        Get category information for a completion
        
        Args:
            metadata: Finish reason metadata
            
        Returns:
            CompletionCategory object
        """
        return self.category_mappings.get(
            metadata.reason,
            self.category_mappings[FinishReason.UNKNOWN]
        )
    
    def is_completion_usable(
        self,
        metadata: FinishReasonMetadata,
        min_token_count: Optional[int] = None
    ) -> bool:
        """
        Check if a completion is usable
        
        Args:
            metadata: Finish reason metadata
            min_token_count: Optional minimum token count
            
        Returns:
            Boolean indicating if completion is usable
        """
        category = self.get_completion_category(metadata)
        
        if not category.is_usable:
            return False
            
        if min_token_count and metadata.token_count:
            if metadata.token_count < min_token_count:
                return False
                
        return True
    
    def needs_retry(
        self,
        metadata: FinishReasonMetadata
    ) -> tuple[bool, Optional[str]]:
        """
        Check if completion needs retry
        
        Args:
            metadata: Finish reason metadata
            
        Returns:
            Tuple of (needs_retry, retry_reason)
        """
        category = self.get_completion_category(metadata)
        
        if not category.requires_retry:
            return False, None
            
        retry_reasons = {
            FinishReason.ERROR: "error occurred",
            FinishReason.CONTENT_FILTER: "content filtered",
            FinishReason.INCOMPLETE: "completion interrupted",
            FinishReason.UNKNOWN: "unknown completion reason"
        }
        
        return True, retry_reasons.get(metadata.reason, "retry required")