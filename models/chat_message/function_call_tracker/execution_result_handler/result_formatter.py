"""Formats function execution results for output"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel
from .result_storage import ExecutionResult

class FormatterConfig(BaseModel):
    """Configuration for result formatting"""
    include_timestamp: bool = True
    include_execution_time: bool = True
    include_metadata: bool = True
    format_errors: bool = True
    max_result_length: Optional[int] = None
    datetime_format: str = "%Y-%m-%d %H:%M:%S"

class OutputFormat(BaseModel):
    """Formatted output structure"""
    success: bool
    function_name: str
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class ResultFormatter:
    """Formats execution results for output"""
    
    def __init__(self, config: Optional[FormatterConfig] = None):
        self.config = config or FormatterConfig()
        
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp according to configuration"""
        return timestamp.strftime(self.config.datetime_format)
        
    def _format_error(self, error: str) -> str:
        """Format error message"""
        if not self.config.format_errors:
            return error
            
        # Add structure to error message
        if ":" in error:
            error_type, message = error.split(":", 1)
            return f"Error ({error_type.strip()}): {message.strip()}"
        return f"Error: {error}"
        
    def _truncate_result(self, result: Any) -> Any:
        """Truncate result if needed"""
        if not self.config.max_result_length:
            return result
            
        if isinstance(result, str):
            if len(result) > self.config.max_result_length:
                return f"{result[:self.config.max_result_length]}..."
        elif isinstance(result, dict):
            return {k: self._truncate_result(v) for k, v in result.items()}
        elif isinstance(result, list):
            return [self._truncate_result(v) for v in result]
            
        return result
        
    def format_result(
        self,
        execution_result: ExecutionResult
    ) -> OutputFormat:
        """
        Format a single execution result
        
        Args:
            execution_result: ExecutionResult to format
            
        Returns:
            Formatted output
        """
        execution_details = {}
        
        if self.config.include_timestamp:
            execution_details["timestamp"] = self._format_timestamp(
                execution_result.timestamp
            )
            
        if self.config.include_execution_time:
            execution_details["execution_time"] = f"{execution_result.execution_time:.4f}s"
            
        result = None
        error = None
        
        if execution_result.success:
            result = self._truncate_result(execution_result.result)
        else:
            error = self._format_error(execution_result.error or "Unknown error")
            
        metadata = {}
        if self.config.include_metadata:
            metadata = execution_result.metadata
            
        return OutputFormat(
            success=execution_result.success,
            function_name=execution_result.function_name,
            result=result,
            error=error,
            execution_details=execution_details,
            metadata=metadata
        )
        
    def format_results(
        self,
        execution_results: List[ExecutionResult]
    ) -> List[OutputFormat]:
        """Format multiple execution results"""
        return [self.format_result(result) for result in execution_results]
        
    def format_performance_metrics(
        self,
        metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, str]]:
        """Format performance metrics"""
        formatted = {}
        for function_name, function_metrics in metrics.items():
            formatted[function_name] = {
                "min_time": f"{function_metrics['min_time']:.4f}s",
                "max_time": f"{function_metrics['max_time']:.4f}s",
                "avg_time": f"{function_metrics['avg_time']:.4f}s",
                "total_time": f"{function_metrics['total_time']:.4f}s",
                "call_count": str(function_metrics['count'])
            }
        return formatted