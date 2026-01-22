"""
Custom exceptions for Vibe Coding Platform
"""

from typing import Any


class VibeException(Exception):
    """Base exception for Vibe Coding Platform"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(VibeException):
    """Raised when validation fails"""

    pass


class SchemaException(VibeException):
    """Raised when schema operations fail"""

    pass


class SafetyException(VibeException):
    """Raised when safety checks fail"""

    pass


class AuthenticationException(VibeException):
    """Raised when authentication fails"""

    pass


class AuthorizationException(VibeException):
    """Raised when authorization fails"""

    pass


class HasuraException(VibeException):
    """Raised when Hasura operations fail"""

    pass


class NotFoundException(VibeException):
    """Raised when a resource is not found"""

    pass


class ConflictException(VibeException):
    """Raised when a resource conflicts with existing data"""

    pass
