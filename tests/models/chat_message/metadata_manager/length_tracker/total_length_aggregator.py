"""Aggregates and tracks total message lengths"""
from typing import Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel
from .prompt_length_calculator import ComponentLength
from .completion_length_calculator import CompletionLength, GenerationStats

class LengthAggregation(BaseModel):
    """Container for length aggregation data"""
    tokens: Optional[int] = None
    characters: int = 0
    components: Dict[str, int] = {}
    metadata: Dict[str, Union[int, float]] = {}

class TotalLengthAggregator:
    """Aggregates and tracks total message lengths"""
    
    def __init__(self):
        self.prompt_lengths = LengthAggregation()
        self.completion_lengths = LengthAggregation()
        self.generation_tracking: List[GenerationStats] = []
        
    def add_prompt_length(
        self,
        component_lengths: Dict[str, ComponentLength],
        totals: Dict[str, int]
    ) -> None:
        """
        Add prompt lengths to aggregation
        
        Args:
            component_lengths: Length details for each component
            totals: Total counts for the prompt
        """
        # Update prompt token count
        if totals.get("total_tokens"):
            self.prompt_lengths.tokens = (self.prompt_lengths.tokens or 0) + totals["total_tokens"]
        
        # Update prompt character count
        self.prompt_lengths.characters += totals["total_chars"]
        
        # Track component-specific counts
        for name, component in component_lengths.items():
            if component.token_count:
                self.prompt_lengths.components[f"{name}_tokens"] = (
                    self.prompt_lengths.components.get(f"{name}_tokens", 0) + 
                    component.token_count
                )
            self.prompt_lengths.components[f"{name}_chars"] = (
                self.prompt_lengths.components.get(f"{name}_chars", 0) + 
                component.char_count
            )
    
    def add_completion_length(
        self,
        completion: CompletionLength
    ) -> None:
        """
        Add completion length to aggregation
        
        Args:
            completion: Length details for a completion
        """
        # Update completion token count
        if completion.token_count:
            self.completion_lengths.tokens = (
                (self.completion_lengths.tokens or 0) + completion.token_count
            )
        
        # Update completion character count
        self.completion_lengths.characters += completion.char_count
        
        # Store generation stats if available
        if completion.generation_stats:
            self.generation_tracking.append(completion.generation_stats)
    
    def get_totals(self) -> Dict[str, Union[int, float]]:
        """Get aggregated length totals"""
        totals = {
            "total_chars": self.prompt_lengths.characters + self.completion_lengths.characters,
            "prompt_chars": self.prompt_lengths.characters,
            "completion_chars": self.completion_lengths.characters,
        }
        
        # Add token counts if available
        if self.prompt_lengths.tokens is not None or self.completion_lengths.tokens is not None:
            totals.update({
                "total_tokens": (self.prompt_lengths.tokens or 0) + 
                               (self.completion_lengths.tokens or 0),
                "prompt_tokens": self.prompt_lengths.tokens,
                "completion_tokens": self.completion_lengths.tokens
            })
        
        # Add generation statistics if available
        if self.generation_tracking:
            first_gen = self.generation_tracking[0]
            last_gen = self.generation_tracking[-1]
            total_duration = (last_gen.end_time - first_gen.start_time).total_seconds()
            
            totals.update({
                "generation_duration": total_duration,
                "generations_count": len(self.generation_tracking)
            })
            
            if self.completion_lengths.tokens:
                totals["tokens_per_second"] = self.completion_lengths.tokens / total_duration
            
            totals["chars_per_second"] = self.completion_lengths.characters / total_duration
        
        return totals
    
    def get_component_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get length breakdown by component"""
        return {
            "prompt": self.prompt_lengths.components,
            "completion": self.completion_lengths.components
        }