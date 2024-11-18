"""Validates function arguments against schemas and constraints"""
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel, ValidationError
import inspect
import re

class ValidationConfig(BaseModel):
    """Configuration for argument validation"""
    check_types: bool = True
    check_required: bool = True
    allow_extra: bool = False
    validate_defaults: bool = True
    max_str_length: Optional[int] = None
    max_list_length: Optional[int] = None
    max_dict_depth: Optional[int] = 5

class ArgumentSchema(BaseModel):
    """Schema for function arguments"""
    name: str
    type: Type
    required: bool = True
    default: Any = None
    constraints: Dict[str, Any] = {}

class ArgumentValidator:
    """Validates function arguments against schemas"""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        
    def _validate_type(
        self,
        value: Any,
        expected_type: Type
    ) -> tuple[bool, Optional[str]]:
        """Validate argument type"""
        try:
            if isinstance(expected_type, type):
                if not isinstance(value, expected_type):
                    return False, f"Expected type {expected_type.__name__}"
            return True, None
        except Exception as e:
            return False, str(e)
            
    def _validate_constraints(
        self,
        value: Any,
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Validate argument against constraints"""
        errors = []
        
        for constraint, constraint_value in constraints.items():
            if constraint == "min":
                if value < constraint_value:
                    errors.append(f"Value below minimum {constraint_value}")
            elif constraint == "max":
                if value > constraint_value:
                    errors.append(f"Value above maximum {constraint_value}")
            elif constraint == "regex":
                if not re.match(constraint_value, str(value)):
                    errors.append(f"Value does not match pattern {constraint_value}")
            elif constraint == "enum":
                if value not in constraint_value:
                    errors.append(f"Value not in allowed values: {constraint_value}")
            elif constraint == "custom":
                if callable(constraint_value):
                    try:
                        if not constraint_value(value):
                            errors.append("Failed custom validation")
                    except Exception as e:
                        errors.append(f"Custom validation error: {str(e)}")
                        
        return errors
        
    def _check_depth(self, value: Any, current_depth: int = 0) -> Optional[str]:
        """Check nesting depth of complex types"""
        if current_depth > self.config.max_dict_depth:
            return "Maximum nesting depth exceeded"
            
        if isinstance(value, dict):
            for v in value.values():
                error = self._check_depth(v, current_depth + 1)
                if error:
                    return error
        elif isinstance(value, (list, tuple)):
            for v in value:
                error = self._check_depth(v, current_depth + 1)
                if error:
                    return error
                    
        return None
        
    def validate_arguments(
        self,
        kwargs: Dict[str, Any],
        args: List[Any],
        schema: Union[Type[BaseModel], List[ArgumentSchema]]
    ) -> tuple[bool, Dict[str, List[str]]]:
        """
        Validate arguments against schema
        
        Args:
            kwargs: Keyword arguments
            args: Positional arguments
            schema: Validation schema
            
        Returns:
            Tuple of (is_valid, dict of validation errors)
        """
        validation_errors = {}
        
        # Handle Pydantic model schema
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            try:
                combined_args = {**kwargs}
                # Add positional args if they match model fields
                model_fields = schema.model_fields
                for i, arg in enumerate(args):
                    if i < len(model_fields):
                        field_name = list(model_fields.keys())[i]
                        combined_args[field_name] = arg
                        
                schema.model_validate(combined_args)
                return True, {}
            except ValidationError as e:
                return False, {"schema": [str(e)]}
                
        # Handle list of ArgumentSchema
        arg_schemas = schema if isinstance(schema, list) else []
        
        # Validate keyword arguments
        for name, value in kwargs.items():
            errors = []
            
            # Find matching schema
            arg_schema = next(
                (s for s in arg_schemas if s.name == name),
                None
            )
            
            if arg_schema:
                # Type validation
                if self.config.check_types:
                    type_valid, type_error = self._validate_type(
                        value,
                        arg_schema.type
                    )
                    if not type_valid:
                        errors.append(type_error)
                        
                # Constraint validation
                errors.extend(
                    self._validate_constraints(value, arg_schema.constraints)
                )
            elif not self.config.allow_extra:
                errors.append("Unexpected argument")
                
            # Check string length
            if isinstance(value, str) and self.config.max_str_length:
                if len(value) > self.config.max_str_length:
                    errors.append(f"String exceeds max length {self.config.max_str_length}")
                    
            # Check list length
            if isinstance(value, (list, tuple)) and self.config.max_list_length:
                if len(value) > self.config.max_list_length:
                    errors.append(f"List exceeds max length {self.config.max_list_length}")
                    
            # Check nesting depth
            depth_error = self._check_depth(value)
            if depth_error:
                errors.append(depth_error)
                
            if errors:
                validation_errors[name] = errors
                
        # Check required arguments
        if self.config.check_required:
            for schema in arg_schemas:
                if schema.required and schema.name not in kwargs:
                    validation_errors[schema.name] = ["Required argument missing"]
                    
        return len(validation_errors) == 0, validation_errors