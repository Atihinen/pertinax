"""
Page reference data structure for immutable PDF page references.
"""

from pathlib import Path
from typing import Tuple
from .exceptions import PDFError


class PageReference:
    """
    Immutable reference to a specific page in a PDF file.
    
    Attributes:
        file_path: Absolute path to the source PDF file
        page_index: Zero-based page index within the source PDF
    """
    
    def __init__(self, file_path: str, page_index: int):
        """
        Create a new page reference.
        
        Args:
            file_path: Path to the source PDF file
            page_index: Zero-based page index
            
        Raises:
            PDFError: If file doesn't exist or page_index is negative
        """
        path = Path(file_path)
        if not path.exists():
            raise PDFError(f"File does not exist: {file_path}")
        if not path.is_file():
            raise PDFError(f"Path is not a file: {file_path}")
        if page_index < 0:
            raise PDFError(f"Page index must be non-negative, got: {page_index}")
            
        self._file_path = str(path.resolve())
        self._page_index = page_index
    
    @property
    def file_path(self) -> str:
        """Get the absolute file path."""
        return self._file_path
    
    @property
    def page_index(self) -> int:
        """Get the zero-based page index."""
        return self._page_index
    
    def as_tuple(self) -> Tuple[str, int]:
        """Return as a tuple (file_path, page_index)."""
        return (self._file_path, self._page_index)
    
    def __repr__(self) -> str:
        """Return developer-friendly representation."""
        return f"PageReference(file_path='{self._file_path}', page_index={self._page_index})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on file path and page index."""
        if not isinstance(other, PageReference):
            return False
        return (self._file_path == other._file_path and 
                self._page_index == other._page_index)
    
    def __hash__(self) -> int:
        """Make PageReference hashable."""
        return hash((self._file_path, self._page_index))
