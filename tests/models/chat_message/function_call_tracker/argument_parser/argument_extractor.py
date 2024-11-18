"""Extracts and identifies function arguments"""
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel
import json
import re

class ArgumentConfig(BaseModel):
    """Configuration for argument extraction"""
    parse_json: bool = True
    parse_kwargs: bool = True
    parse_positional: bool = True
    allow_empty: bool = True
    max_args: Optional[int] = None
    max_nesting: int = 5

class ArgumentExtractor:
    """Extracts and parses function arguments"""
    
    def __init__(self, config: Optional[ArgumentConfig] = None):
        self.config = config or ArgumentConfig()
        
    def _parse_json_args(self, json_str: str) -> Tuple[Dict[str, Any], List[str]]:
        """Parse JSON formatted arguments"""
        errors = []
        try:
            args = json.loads(json_str)
            if not isinstance(args, dict):
                errors.append("JSON arguments must be an object")
                return {}, errors
            return args, errors
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error: {str(e)}")
            return {}, errors
            
    def _parse_kwargs_string(self, kwargs_str: str) -> Tuple[Dict[str, Any], List[str]]:
        """Parse keyword arguments from string format"""
        args = {}
        errors = []
        
        # Match pattern: key=value pairs, handling quotes and nested structures
        pattern = r'(\w+)\s*=\s*(?:"([^"]*?)"|\'([^\']*?)\'|([^\s,]+))'
        matches = re.finditer(pattern, kwargs_str)
        
        for match in matches:
            key = match.group(1)
            # Get the first non-None value from the captured groups
            value = next(v for v in match.groups()[1:] if v is not None)
            
            # Try to convert value to appropriate type
            try:
                # Try as JSON first for complex types
                args[key] = json.loads(value)
            except json.JSONDecodeError:
                # Fall back to string if not valid JSON
                args[key] = value
                
        return args, errors
        
    def _parse_positional_args(self, args_str: str) -> Tuple[List[Any], List[str]]:
        """Parse positional arguments from string format"""
        args = []
        errors = []
        
        # Split on commas outside quotes and brackets
        in_quotes = False
        in_brackets = 0
        current_arg = []
        quote_char = None
        
        for char in args_str:
            if char in '"\'':
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current_arg.append(char)
            elif char in '[{(':
                in_brackets += 1
                current_arg.append(char)
            elif char in ']})':
                in_brackets -= 1
                current_arg.append(char)
            elif char == ',' and not in_quotes and in_brackets == 0:
                arg_str = ''.join(current_arg).strip()
                if arg_str:
                    try:
                        # Try parsing as JSON
                        args.append(json.loads(arg_str))
                    except json.JSONDecodeError:
                        # Fall back to string
                        args.append(arg_str)
                current_arg = []
            else:
                current_arg.append(char)
                
        # Handle last argument
        if current_arg:
            arg_str = ''.join(current_arg).strip()
            if arg_str:
                try:
                    args.append(json.loads(arg_str))
                except json.JSONDecodeError:
                    args.append(arg_str)
                    
        return args, errors
        
    def extract_arguments(
        self,
        raw_args: str
    ) -> Tuple[Dict[str, Any], List[Any], List[str]]:
        """
        Extract and parse function arguments
        
        Args:
            raw_args: Raw argument string
            
        Returns:
            Tuple of (kwargs dict, positional args list, errors list)
        """
        kwargs = {}
        args = []
        errors = []
        
        if not raw_args.strip() and not self.config.allow_empty:
            errors.append("Empty arguments not allowed")
            return kwargs, args, errors
            
        # Try JSON parsing first
        if self.config.parse_json:
            json_kwargs, json_errors = self._parse_json_args(raw_args)
            if not json_errors:
                kwargs.update(json_kwargs)
                return kwargs, args, errors
            errors.extend(json_errors)
            
        # Fall back to kwargs string parsing
        if self.config.parse_kwargs:
            kw_args, kw_errors = self._parse_kwargs_string(raw_args)
            kwargs.update(kw_args)
            errors.extend(kw_errors)
            
        # Parse positional args if configured
        if self.config.parse_positional:
            pos_args, pos_errors = self._parse_positional_args(raw_args)
            args.extend(pos_args)
            errors.extend(pos_errors)
            
        # Check argument limits
        if self.config.max_args:
            if len(args) + len(kwargs) > self.config.max_args:
                errors.append(f"Too many arguments (max {self.config.max_args})")
                
        return kwargs, args, errors