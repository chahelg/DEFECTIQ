"""
Core exceptions for the application
"""


class DefectIQException(Exception):
    """Base exception for DefectIQ"""
    pass


class DatabaseException(DefectIQException):
    """Database-related errors"""
    pass


class ValidationException(DefectIQException):
    """Data validation errors"""
    pass


class AuthenticationException(DefectIQException):
    """Authentication errors"""
    pass


class AuthorizationException(DefectIQException):
    """Authorization errors"""
    pass


class NotFoundError(DefectIQException):
    """Resource not found"""
    pass


class ConflictError(DefectIQException):
    """Resource conflict (e.g., duplicate)"""
    pass


class MLModelException(DefectIQException):
    """ML model errors"""
    pass


class NLPException(DefectIQException):
    """NLP processing errors"""
    pass


class ExternalServiceException(DefectIQException):
    """External service errors (OpenAI, etc.)"""
    pass


class FileUploadException(DefectIQException):
    """File upload errors"""
    pass

