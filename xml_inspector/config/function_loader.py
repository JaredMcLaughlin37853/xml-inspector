"""Custom validation function loading and registration."""

import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging

from ..validators.python_validator import PythonValidator
from ..types import ValidationFunction

logger = logging.getLogger(__name__)


class FunctionRegistrationError(Exception):
    """Raised when function registration fails."""
    pass


class FunctionLoader:
    """Handles loading and registering custom validation functions."""
    
    @staticmethod
    def find_config_file() -> Optional[str]:
        """
        Find configuration file using standard search order.
        
        Returns:
            Path to config file or None if not found
        """
        search_paths = [
            Path.cwd() / "xml-inspector.config.json",
            Path.home() / ".xml-inspector" / "config.json",
            Path.home() / ".config" / "xml-inspector" / "config.json"
        ]
        
        for config_path in search_paths:
            if config_path.exists():
                return str(config_path)
        
        return None
    
    @staticmethod
    def load_config_file(config_path: str) -> Dict[str, Any]:
        """
        Load and validate configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Parsed configuration dictionary
            
        Raises:
            FunctionRegistrationError: If config is invalid
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Validate required fields
            if not isinstance(config.get('validation_functions'), list):
                config['validation_functions'] = []
            
            return config
            
        except json.JSONDecodeError as e:
            raise FunctionRegistrationError(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            raise FunctionRegistrationError(f"Failed to load config file {config_path}: {e}")
    
    @staticmethod
    def import_function_from_module(module_path: str, function_name: str) -> ValidationFunction:
        """
        Import a validation function from a module.
        
        Args:
            module_path: Dotted module path or file path
            function_name: Name of the function to import
            
        Returns:
            The imported validation function
            
        Raises:
            FunctionRegistrationError: If import fails
        """
        try:
            # Handle file path modules (e.g., examples/validation-functions/adapter.py)
            if "/" in module_path or "\\\\" in module_path:
                module_file = Path(module_path)
                if not module_file.suffix:
                    module_file = module_file.with_suffix('.py')
                
                if not module_file.exists():
                    raise FunctionRegistrationError(f"Module file not found: {module_file}")
                
                spec = importlib.util.spec_from_file_location(f"custom_module_{id(module_path)}", module_file)
                if spec is None or spec.loader is None:
                    raise FunctionRegistrationError(f"Could not create module spec for {module_file}")
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Handle dotted module paths
                module = importlib.import_module(module_path)
            
            if not hasattr(module, function_name):
                raise FunctionRegistrationError(f"Function '{function_name}' not found in module '{module_path}'")
            
            function = getattr(module, function_name)
            if not callable(function):
                raise FunctionRegistrationError(f"'{function_name}' in module '{module_path}' is not callable")
            
            return function
            
        except ImportError as e:
            raise FunctionRegistrationError(f"Could not import module '{module_path}': {e}")
        except Exception as e:
            raise FunctionRegistrationError(f"Error importing function '{function_name}' from '{module_path}': {e}")
    
    @staticmethod
    def register_functions_from_config(validator: PythonValidator, config_path: str, 
                                     verbose: bool = False) -> Tuple[int, List[str]]:
        """
        Register validation functions from configuration file.
        
        Args:
            validator: PythonValidator instance to register functions with
            config_path: Path to configuration file
            verbose: Whether to show detailed loading information
            
        Returns:
            Tuple of (registered_count, error_messages)
            
        Raises:
            FunctionRegistrationError: If configuration loading fails
        """
        config = FunctionLoader.load_config_file(config_path)
        registered_count = 0
        error_messages = []
        
        if verbose:
            logger.info(f"Loading functions from config: {config_path}")
        
        # Add function paths to Python path
        function_paths = config.get('function_paths', [])
        for func_path in function_paths:
            path = Path(func_path).resolve()
            if path.exists() and str(path) not in sys.path:
                sys.path.insert(0, str(path))
                if verbose:
                    logger.info(f"Added to Python path: {path}")
        
        # Register validation functions
        validation_functions = config.get('validation_functions', [])
        for func_config in validation_functions:
            try:
                func_id = func_config['id']
                module_path = func_config['module']
                function_name = func_config['function']
                description = func_config.get('description', f'Custom validation function: {func_id}')
                severity = func_config.get('severity', 'error')
                
                if verbose:
                    logger.info(f"Loading: {func_id} from {module_path}:{function_name}")
                
                # Import and register the function
                validation_function = FunctionLoader.import_function_from_module(module_path, function_name)
                validator.register_function(func_id, description, validation_function, severity)
                registered_count += 1
                
                if verbose:
                    logger.info(f"Registered: {func_id}")
                    
            except KeyError as e:
                error_msg = f"Missing required field in function config: {e}"
                error_messages.append(error_msg)
                if verbose:
                    logger.warning(error_msg)
            except FunctionRegistrationError as e:
                error_msg = str(e)
                error_messages.append(error_msg)
                if verbose:
                    logger.warning(error_msg)
            except Exception as e:
                error_msg = f"Failed to register function {func_config.get('id', 'unknown')}: {e}"
                error_messages.append(error_msg)
                if verbose:
                    logger.warning(error_msg)
        
        return registered_count, error_messages