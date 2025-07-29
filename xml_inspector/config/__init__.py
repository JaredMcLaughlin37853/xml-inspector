"""Configuration management for XML Inspector."""

from .function_loader import FunctionLoader, FunctionRegistrationError

__all__ = ["FunctionLoader", "FunctionRegistrationError"]