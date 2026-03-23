"""
Custom exceptions for Pertinax PDF operations.
"""


class PDFError(Exception):
    """Base exception for PDF-related errors."""
    pass


class PageNotFoundError(PDFError):
    """Raised when a page index is invalid or out of range."""
    pass
