"""
Function call tracking and management components.

This module provides comprehensive handling of function calls in chat messages, including:
- Function name extraction and validation
- Argument parsing and validation
- Execution result tracking and formatting
"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Function Name Components
from .function_name_extractor import (
    FunctionNameConfig,
    FunctionIdentifier,
    SanitizationConfig as NameSanitizationConfig,
    FunctionNameSanitizer
)

# Argument Parsing Components
from .argument_parser import (
    ArgumentConfig,
    ArgumentExtractor,
    ValidationConfig,
    ArgumentSchema,
    ArgumentValidator,
    SanitizationConfig as ArgSanitizationConfig,
    ArgumentSanitizer
)

# Execution Result Components
from .execution_result_handler import (
    ExecutionResult,
    StorageConfig,
    ResultStorage,
    FormatterConfig,
    OutputFormat,
    ResultFormatter
)

class FunctionCallTracker:
    """Coordinates function call tracking and management"""
    
    def __init__(
        self,
        name_config: Optional[FunctionNameConfig] = None,
        arg_config: Optional[ArgumentConfig] = None,
        validation_config: Optional[ValidationConfig] = None,
        storage_config: Optional[StorageConfig] = None,
        formatter_config: Optional[FormatterConfig] = None
    ):
        # Initialize components
        self.function_identifier = FunctionIdentifier(name_config)
        self.name_sanitizer = FunctionNameSanitizer(NameSanitizationConfig())
        self.arg_extractor = ArgumentExtractor(arg_config)
        self.arg_validator = ArgumentValidator(validation_config)
        self.arg_sanitizer = ArgumentSanitizer(ArgSanitizationConfig())
        self.result_storage = ResultStorage(storage_config)
        self.result_formatter = ResultFormatter(formatter_config)
        
    def process_function_call(
        self,
        raw_name: str,
        raw_args: str,
        schema: Optional[Union[ArgumentSchema, List[ArgumentSchema]]] = None
    ) -> Dict[str, Any]:
        """
        Process a function call
        
        Args:
            raw_name: Raw function name
            raw_args: Raw argument string
            schema: Optional argument validation schema
            
        Returns:
            Dict containing processed function call details
        """
        # Process function name
        valid_name, name_validation = self.function_identifier.identify_function(raw_name)
        if valid_name:
            sanitized_name, name_changes = self.name_sanitizer.sanitize_name(valid_name)
        else:
            return {
                "success": False,
                "error": "Invalid function name",
                "validation_errors": name_validation
            }
            
        # Extract and process arguments
        kwargs, args, arg_errors = self.arg_extractor.extract_arguments(raw_args)
        if arg_errors:
            return {
                "success": False,
                "error": "Argument extraction failed",
                "validation_errors": arg_errors
            }
            
        # Sanitize arguments
        sanitized_kwargs, san_changes = self.arg_sanitizer.sanitize_arguments(kwargs)
        
        # Validate arguments if schema provided
        if schema:
            is_valid, validation_errors = self.arg_validator.validate_arguments(
                sanitized_kwargs,
                args,
                schema
            )
            if not is_valid:
                return {
                    "success": False,
                    "error": "Argument validation failed",
                    "validation_errors": validation_errors
                }
                
        return {
            "success": True,
            "function_name": sanitized_name,
            "kwargs": sanitized_kwargs,
            "args": args,
            "changes": {
                "name": name_changes,
                "arguments": san_changes
            }
        }
        
    def track_execution(
        self,
        function_name: str,
        result: Any,
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OutputFormat:
        """
        Track function execution result
        
        Args:
            function_name: Name of executed function
            result: Function result or error
            execution_time: Execution time in seconds
            success: Whether execution was successful
            error: Optional error message
            metadata: Optional metadata
            
        Returns:
            Formatted execution result
        """
        # Store result
        execution_result = self.result_storage.store_result(
            function_name=function_name,
            result=result,
            execution_time=execution_time,
            success=success,
            error=error,
            metadata=metadata
        )
        
        # Format and return result
        return self.result_formatter.format_result(execution_result)
        
    def get_execution_history(
        self,
        function_name: Optional[str] = None,
        success_only: bool = False,
        limit: Optional[int] = None
    ) -> List[OutputFormat]:
        """Get formatted execution history"""
        results = self.result_storage.get_results(
            function_name=function_name,
            success_only=success_only,
            limit=limit
        )
        return self.result_formatter.format_results(results)
        
    def get_performance_metrics(
        self,
        function_name: Optional[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """Get formatted performance metrics"""
        metrics = self.result_storage.get_performance_metrics(function_name)
        return self.result_formatter.format_performance_metrics(metrics)

__all__ = [
    # Main Tracker
    "FunctionCallTracker",
    
    # Function Name Components
    "FunctionNameConfig",
    "FunctionIdentifier",
    "NameSanitizationConfig",
    "FunctionNameSanitizer",
    
    # Argument Components
    "ArgumentConfig",
    "ArgumentExtractor",
    "ValidationConfig",
    "ArgumentSchema",
    "ArgumentValidator",
    "ArgSanitizationConfig",
    "ArgumentSanitizer",
    
    # Result Components
    "ExecutionResult",
    "StorageConfig",
    "ResultStorage",
    "FormatterConfig",
    "OutputFormat",
    "ResultFormatter",
]