"""Mock objects for testing"""
from typing import Dict, Any, Optional, List
from datetime import datetime

class MockMessageStore:
    """Mock message storage for testing"""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        
    def add_message(self, message: Dict[str, Any]):
        self.messages.append(message)
        
    def get_messages(self) -> List[Dict[str, Any]]:
        return self.messages.copy()
        
    def clear(self):
        self.messages.clear()

class MockFunctionExecutor:
    """Mock function executor for testing"""
    
    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.calls: List[Dict[str, Any]] = []
        
    def execute(
        self,
        function_name: str,
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        self.calls.append({
            "name": function_name,
            "args": args,
            "timestamp": datetime.now()
        })
        
        if self.should_succeed:
            return {
                "success": True,
                "result": "mock_result",
                "metadata": {"execution_time": 0.1}
            }
        else:
            return {
                "success": False,
                "error": "mock_error",
                "metadata": {"error_code": "MOCK_ERROR"}
            }

class MockContentProcessor:
    """Mock content processor for testing"""
    
    def __init__(self):
        self.processed_content: List[Dict[str, Any]] = []
        
    def process(
        self,
        content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        result = {
            "original": content,
            "processed": f"processed_{content}",
            "options": options or {},
            "timestamp": datetime.now()
        }
        self.processed_content.append(result)
        return result

class MockMetadataTracker:
    """Mock metadata tracker for testing"""
    
    def __init__(self):
        self.metadata: Dict[str, Any] = {}
        
    def add_metadata(
        self,
        key: str,
        value: Any
    ):
        self.metadata[key] = value
        
    def get_metadata(self, key: str) -> Optional[Any]:
        return self.metadata.get(key)
        
    def clear(self):
        self.metadata.clear()