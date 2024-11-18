"""Stores and manages function execution results"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel
import json

class ExecutionResult(BaseModel):
    """Model for function execution result"""
    function_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class StorageConfig(BaseModel):
    """Configuration for result storage"""
    track_history: bool = True
    max_history: Optional[int] = 100
    store_errors: bool = True
    track_performance: bool = True
    serializable_only: bool = False

class ResultStorage:
    """Stores and manages function execution results"""
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self.results: List[ExecutionResult] = []
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
    def _is_serializable(self, value: Any) -> bool:
        """Check if a value is JSON serializable"""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError, OverflowError):
            return False
            
    def _prepare_result(self, result: Any) -> Any:
        """Prepare result for storage"""
        if not self.config.serializable_only:
            return result
            
        if isinstance(result, dict):
            return {k: self._prepare_result(v) for k, v in result.items()
                   if self._is_serializable(v)}
        elif isinstance(result, list):
            return [self._prepare_result(v) for v in result
                   if self._is_serializable(v)]
        elif self._is_serializable(result):
            return result
        else:
            return str(result)
            
    def _update_performance_metrics(
        self,
        function_name: str,
        execution_time: float
    ) -> None:
        """Update performance tracking metrics"""
        if function_name not in self.performance_metrics:
            self.performance_metrics[function_name] = {
                "min_time": execution_time,
                "max_time": execution_time,
                "total_time": execution_time,
                "count": 1,
                "avg_time": execution_time
            }
        else:
            metrics = self.performance_metrics[function_name]
            metrics["min_time"] = min(metrics["min_time"], execution_time)
            metrics["max_time"] = max(metrics["max_time"], execution_time)
            metrics["total_time"] += execution_time
            metrics["count"] += 1
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]
            
    def store_result(
        self,
        function_name: str,
        result: Any,
        execution_time: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Store a function execution result
        
        Args:
            function_name: Name of executed function
            result: Function result or None
            execution_time: Execution time in seconds
            success: Whether execution was successful
            error: Optional error message
            metadata: Optional metadata
            
        Returns:
            ExecutionResult object
        """
        # Prepare result for storage
        prepared_result = self._prepare_result(result)
        
        # Create execution result
        execution_result = ExecutionResult(
            function_name=function_name,
            success=success,
            result=prepared_result if success else None,
            error=error if not success and self.config.store_errors else None,
            execution_time=execution_time,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store result if tracking history
        if self.config.track_history:
            self.results.append(execution_result)
            # Trim history if needed
            if (self.config.max_history and 
                len(self.results) > self.config.max_history):
                self.results = self.results[-self.config.max_history:]
                
        # Update performance metrics if tracking
        if self.config.track_performance and success:
            self._update_performance_metrics(function_name, execution_time)
            
        return execution_result
        
    def get_results(
        self,
        function_name: Optional[str] = None,
        success_only: bool = False,
        limit: Optional[int] = None
    ) -> List[ExecutionResult]:
        """Get stored execution results with optional filtering"""
        filtered = self.results
        
        if function_name:
            filtered = [r for r in filtered if r.function_name == function_name]
            
        if success_only:
            filtered = [r for r in filtered if r.success]
            
        if limit:
            filtered = filtered[-limit:]
            
        return filtered
        
    def get_performance_metrics(
        self,
        function_name: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for functions"""
        if function_name:
            return {
                function_name: self.performance_metrics.get(
                    function_name,
                    {
                        "min_time": 0,
                        "max_time": 0,
                        "total_time": 0,
                        "count": 0,
                        "avg_time": 0
                    }
                )
            }
        return self.performance_metrics
        
    def clear_results(
        self,
        function_name: Optional[str] = None,
        clear_metrics: bool = False
    ) -> None:
        """Clear stored results and optionally metrics"""
        if function_name:
            self.results = [r for r in self.results 
                          if r.function_name != function_name]
            if clear_metrics:
                self.performance_metrics.pop(function_name, None)
        else:
            self.results.clear()
            if clear_metrics:
                self.performance_metrics.clear()