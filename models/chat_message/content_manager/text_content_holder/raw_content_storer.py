"""Stores original, unmodified message content"""
from typing import Optional
from pydantic import BaseModel, Field

class RawContent(BaseModel):
    """Model for storing raw message content"""
    content: str
    content_type: str = Field(default="text")
    encoding: str = Field(default="utf-8")
    length: int = Field(default=0)

class RawContentStorer:
    """Handles storage of raw message content"""
    
    def store_content(self, content: str) -> RawContent:
        """
        Store raw content with metadata
        
        Args:
            content: The raw message content to store
            
        Returns:
            RawContent object containing the content and metadata
        """
        return RawContent(
            content=content,
            length=len(content)
        )
    
    def retrieve_content(self, raw_content: RawContent) -> str:
        """
        Retrieve stored raw content
        
        Args:
            raw_content: RawContent object containing stored content
            
        Returns:
            Original raw content string
        """
        return raw_content.content