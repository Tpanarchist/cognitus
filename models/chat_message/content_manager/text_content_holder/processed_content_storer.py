"""Stores processed and modified message content"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ContentModification(BaseModel):
    """Record of a content modification"""
    modification_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    original_content: str
    modified_content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProcessedContent(BaseModel):
    """Model for storing processed message content"""
    content: str
    original_content: str
    modifications: list[ContentModification] = Field(default_factory=list)
    final_length: int = Field(default=0)
    processing_complete: bool = Field(default=False)

class ProcessedContentStorer:
    """Handles storage of processed message content"""
    
    def store_content(
        self, 
        content: str,
        original_content: str,
        modification_type: Optional[str] = None
    ) -> ProcessedContent:
        """
        Store processed content with tracking information
        
        Args:
            content: The processed content to store
            original_content: The original content before processing
            modification_type: Type of modification applied
            
        Returns:
            ProcessedContent object containing the content and tracking info
        """
        processed = ProcessedContent(
            content=content,
            original_content=original_content,
            final_length=len(content)
        )
        
        if modification_type:
            modification = ContentModification(
                modification_type=modification_type,
                original_content=original_content,
                modified_content=content
            )
            processed.modifications.append(modification)
            
        return processed
    
    def add_modification(
        self,
        processed_content: ProcessedContent,
        new_content: str,
        modification_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessedContent:
        """
        Add a new modification to existing processed content
        
        Args:
            processed_content: Existing ProcessedContent object
            new_content: New modified content
            modification_type: Type of modification applied
            metadata: Optional metadata about the modification
            
        Returns:
            Updated ProcessedContent object
        """
        modification = ContentModification(
            modification_type=modification_type,
            original_content=processed_content.content,
            modified_content=new_content,
            metadata=metadata or {}
        )
        
        processed_content.modifications.append(modification)
        processed_content.content = new_content
        processed_content.final_length = len(new_content)
        
        return processed_content
    
    def mark_complete(self, processed_content: ProcessedContent) -> ProcessedContent:
        """Mark content processing as complete"""
        processed_content.processing_complete = True
        return processed_content
    
    def get_modification_history(
        self,
        processed_content: ProcessedContent
    ) -> list[ContentModification]:
        """Get complete modification history"""
        return processed_content.modifications