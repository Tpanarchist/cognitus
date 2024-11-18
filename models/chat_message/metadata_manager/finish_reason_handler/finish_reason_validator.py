"""Validates completion finish reasons"""
from typing import Dict, Optional, Tuple
from pydantic import BaseModel
import logging
from .finish_reason_fetcher import FinishReason, FinishReasonMetadata

class ValidationConfig(BaseModel):
    """Configuration for finish reason validation"""
    allow_unknown: bool = False
    validate_token_count: bool = True
    validate_error_details: bool = True
    min_token_count: int = 1
    max_token_count: Optional[int] = None
    log_validation_errors: bool = True

class FinishReasonValidator:
    """Validates completion finish reasons and metadata"""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.logger = logging.getLogger("cognitus.finish_reason_validator")
    
    def _validate_token_count(
        self,
        metadata: FinishReasonMetadata
    ) -> Tuple[bool, Optional[str]]:
        """Validate token count if present"""
        if not metadata.token_count:
            return True, None
            
        if metadata.token_count < self.config.min_token_count:
            return False, f"Token count {metadata.token_count} below minimum {self.config.min_token_count}"
            
        if (self.config.max_token_count and 
            metadata.token_count > self.config.max_token_count):
            return False, f"Token count {metadata.token_count} above maximum {self.config.max_token_count}"
            
        return True, None
    
    def _validate_error_details(
        self,
        metadata: FinishReasonMetadata
    ) -> Tuple[bool, Optional[str]]:
        """Validate error details if present"""
        if metadata.reason == FinishReason.ERROR:
            if not metadata.error_details:
                return False, "Error reason requires error details"
        elif metadata.error_details:
            return False, "Error details present for non-error reason"
            
        return True, None
    
    def _validate_filter_flags(
        self,
        metadata: FinishReasonMetadata
    ) -> Tuple[bool, Optional[str]]:
        """Validate filter flags if present"""
        if metadata.reason == FinishReason.CONTENT_FILTER:
            if not metadata.filter_flags:
                return False, "Content filter reason requires filter flags"
        elif metadata.filter_flags:
            return False, "Filter flags present for non-filter reason"
            
        return True, None
    
    def validate_finish_reason(
        self,
        metadata: FinishReasonMetadata
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Validate finish reason metadata
        
        Args:
            metadata: FinishReasonMetadata to validate
            
        Returns:
            Tuple of (is_valid, dict of validation errors)
        """
        validation_errors = {}
        
        # Check basic reason validity
        if metadata.reason == FinishReason.UNKNOWN and not self.config.allow_unknown:
            validation_errors["reason"] = "Unknown finish reason not allowed"
        
        # Validate token count if configured
        if self.config.validate_token_count:
            is_valid, error = self._validate_token_count(metadata)
            if not is_valid:
                validation_errors["token_count"] = error
        
        # Validate error details if configured
        if self.config.validate_error_details:
            is_valid, error = self._validate_error_details(metadata)
            if not is_valid:
                validation_errors["error_details"] = error
        
        # Validate filter flags
        is_valid, error = self._validate_filter_flags(metadata)
        if not is_valid:
            validation_errors["filter_flags"] = error
        
        # Log validation errors if configured
        if validation_errors and self.config.log_validation_errors:
            error_msg = "Finish reason validation errors: " + ", ".join(
                f"{k}: {v}" for k, v in validation_errors.items()
            )
            self.logger.error(error_msg)
        
        return len(validation_errors) == 0, validation_errors