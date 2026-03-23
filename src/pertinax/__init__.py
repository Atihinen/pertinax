"""
Pertinax - PDF Page Compositor

A minimal PDF page compositor for Linux that operates on immutable page references.
"""

from .document import PDFDocument
from .page_reference import PageReference
from .exceptions import PDFError, PageNotFoundError

__all__ = ['PDFDocument', 'PageReference', 'PDFError', 'PageNotFoundError']
__version__ = '0.1.0'
