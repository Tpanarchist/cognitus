"""
Metadata management components for message handling.

This module provides comprehensive metadata handling for chat messages, including:
- Completion state tracking (finish reasons, types)
- Message length calculation and tracking
- Timestamp generation and management
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
import time

# Finish Reason Components
from .finish_reason_handler import (
    FinishReason,
    FinishReasonMetadata,
    FinishReasonFetcher,
    ValidationConfig as FinishReasonValidationConfig,
    FinishReasonValidator,
    CompletionType,
    CompletionCategory,
    CompletionTypeCategorizer
)

# Length Tracking Components
from .length_tracker import (
    PromptLengthConfig,
    ComponentLength,
    PromptLengthCalculator,
    CompletionLengthConfig,
    CompletionLength,
    GenerationStats,
    CompletionLengthCalculator,
    LengthAggregation,
    TotalLengthAggregator
)

# Timestamp Components
from .timestamp_generator import (
    TimestampConfig,
    TimestampMetadata,
    TimestampCreator,
    TimezoneConfig,
    TimezoneConversion,
    TimezoneAdjuster
)

class MessageMetadata:
    """Container for all message metadata"""
    
    def __init__(
        self,
        finish_reason_config: Optional[FinishReasonValidationConfig] = None,
        prompt_length_config: Optional[PromptLengthConfig] = None,
        completion_length_config: Optional[CompletionLengthConfig] = None,
        timestamp_config: Optional[TimestampConfig] = None,
        timezone_config: Optional[TimezoneConfig] = None
    ):
        # Initialize handlers
        self.finish_reason = FinishReasonValidator(finish_reason_config)
        self.completion_type = CompletionTypeCategorizer()
        self.prompt_length = PromptLengthCalculator(prompt_length_config)
        self.completion_length = CompletionLengthCalculator(completion_length_config)
        self.length_aggregator = TotalLengthAggregator()
        self.timestamp_creator = TimestampCreator(timestamp_config)
        self.timezone_adjuster = TimezoneAdjuster(timezone_config)
        
    def process_prompt(
        self,
        components: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process prompt metadata

        Args:
            components: Dict of component name to text content
            
        Returns:
            Dict containing prompt metadata
        """
        # Calculate lengths
        component_lengths, totals = self.prompt_length.calculate_lengths(components)
        self.length_aggregator.add_prompt_length(component_lengths, totals)
        
        # Generate timestamp
        timestamp, timestamp_meta = self.timestamp_creator.create_timestamp()
        
        return {
            "lengths": {
                "components": component_lengths,
                "totals": totals
            },
            "timestamp": {
                "created_at": timestamp,
                "metadata": timestamp_meta
            }
        }
        
    def process_completion(
        self,
        text: str,
        finish_reason: str,
        timestamp: Optional[datetime] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process completion metadata

        Args:
            text: Completion text
            finish_reason: Raw finish reason
            timestamp: Optional timestamp for the completion
            additional_metadata: Optional additional metadata
            
        Returns:
            Dict containing completion metadata
        """
        # Process finish reason
        reason_meta = FinishReasonFetcher.create_metadata(
            finish_reason,
            timestamp.timestamp() if timestamp else time.time(),
            **(additional_metadata or {})
        )
        is_valid, validation_errors = self.finish_reason.validate_finish_reason(reason_meta)
        
        # Categorize completion
        category = self.completion_type.get_completion_category(reason_meta)
        
        # Calculate length
        completion_length = self.completion_length.calculate_length(text)
        self.length_aggregator.add_completion_length(completion_length)
        
        # Get or create timestamp
        if timestamp:
            ts_meta = TimestampMetadata(
                unix_timestamp=timestamp.timestamp(),
                is_utc=timestamp.tzinfo is timezone.utc,
                has_timezone=timestamp.tzinfo is not None
            )
        else:
            timestamp, ts_meta = self.timestamp_creator.create_timestamp()
            
        return {
            "finish_reason": {
                "metadata": reason_meta,
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "category": category
            },
            "length": completion_length,
            "timestamp": {
                "created_at": timestamp,
                "metadata": ts_meta
            }
        }
        
    def get_aggregated_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        return {
            "lengths": {
                "totals": self.length_aggregator.get_totals(),
                "components": self.length_aggregator.get_component_breakdown()
            },
            "timestamps": {
                "timezone_conversions": self.timezone_adjuster.get_conversion_history()
            }
        }

__all__ = [
    # Message Metadata Container
    "MessageMetadata",
    
    # Finish Reason Components
    "FinishReason",
    "FinishReasonMetadata",
    "FinishReasonFetcher",
    "FinishReasonValidationConfig",
    "FinishReasonValidator",
    "CompletionType",
    "CompletionCategory",
    "CompletionTypeCategorizer",
    
    # Length Tracking Components
    "PromptLengthConfig",
    "ComponentLength",
    "PromptLengthCalculator",
    "CompletionLengthConfig",
    "CompletionLength",
    "GenerationStats",
    "CompletionLengthCalculator",
    "LengthAggregation",
    "TotalLengthAggregator",
    
    # Timestamp Components
    "TimestampConfig",
    "TimestampMetadata",
    "TimestampCreator",
    "TimezoneConfig",
    "TimezoneConversion",
    "TimezoneAdjuster",
]