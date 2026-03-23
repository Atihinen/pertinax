"""
Main document class for PDF page composition.
"""

from pathlib import Path
from typing import List, Dict
from pypdf import PdfReader, PdfWriter

from .page_reference import PageReference
from .exceptions import PDFError, PageNotFoundError


class PDFDocument:
    """
    PDF page compositor that operates on immutable page references.
    
    This class maintains an in-memory list of page references and provides
    operations to manipulate them without modifying source PDF files.
    """
    
    def __init__(self):
        """Initialize an empty PDF document."""
        self.pages: List[PageReference] = []
        self.source_files: Dict[str, PdfReader] = {}
    
    @property
    def page_count(self) -> int:
        """Get the total number of pages in the working document."""
        return len(self.pages)
    
    def open_pdf(self, file_path: str) -> None:
        """
        Open a PDF and replace the current working document with its pages.
        
        Args:
            file_path: Path to the PDF file to open
            
        Raises:
            PDFError: If the file cannot be opened or read
        """
        path = Path(file_path)
        if not path.exists():
            raise PDFError(f"File does not exist: {file_path}")
        if not path.is_file():
            raise PDFError(f"Path is not a file: {file_path}")
        
        try:
            reader = PdfReader(str(path))
            num_pages = len(reader.pages)
        except Exception as e:
            raise PDFError(f"Failed to open PDF: {e}")
        
        # Clear current document
        self.pages = []
        self.source_files = {}
        
        # Create page references for all pages
        abs_path = str(path.resolve())
        self.source_files[abs_path] = reader
        
        for page_idx in range(num_pages):
            self.pages.append(PageReference(abs_path, page_idx))
    
    def import_pdf(self, file_path: str) -> None:
        """
        Import pages from another PDF into the current working document.
        
        Args:
            file_path: Path to the PDF file to import
            
        Raises:
            PDFError: If the file cannot be opened or read
        """
        path = Path(file_path)
        if not path.exists():
            raise PDFError(f"File does not exist: {file_path}")
        if not path.is_file():
            raise PDFError(f"Path is not a file: {file_path}")
        
        try:
            reader = PdfReader(str(path))
            num_pages = len(reader.pages)
        except Exception as e:
            raise PDFError(f"Failed to open PDF: {e}")
        
        # Store reader for this file
        abs_path = str(path.resolve())
        if abs_path not in self.source_files:
            self.source_files[abs_path] = reader
        
        # Append page references
        for page_idx in range(num_pages):
            self.pages.append(PageReference(abs_path, page_idx))
    
    def delete_pages(self, indices: List[int]) -> None:
        """
        Delete pages at the specified indices.
        
        Args:
            indices: List of zero-based page indices to delete
            
        Raises:
            PageNotFoundError: If any index is out of range
        """
        if not indices:
            return
        
        # Validate all indices first
        for idx in indices:
            if idx < 0 or idx >= len(self.pages):
                raise PageNotFoundError(
                    f"Page index {idx} out of range (0-{len(self.pages)-1})"
                )
        
        # Remove pages in reverse order to maintain correct indices
        for idx in sorted(set(indices), reverse=True):
            del self.pages[idx]
    
    def reorder_pages(self, old_index: int, new_index: int) -> None:
        """
        Move a page from old_index to new_index.
        
        Args:
            old_index: Current zero-based index of the page
            new_index: Target zero-based index for the page
            
        Raises:
            PageNotFoundError: If either index is out of range
        """
        if old_index < 0 or old_index >= len(self.pages):
            raise PageNotFoundError(
                f"Source index {old_index} out of range (0-{len(self.pages)-1})"
            )
        if new_index < 0 or new_index >= len(self.pages):
            raise PageNotFoundError(
                f"Target index {new_index} out of range (0-{len(self.pages)-1})"
            )
        
        page = self.pages.pop(old_index)
        self.pages.insert(new_index, page)
    
    def move_pages(self, indices: List[int], target_index: int) -> None:
        """
        Move multiple pages to a target position.
        
        Args:
            indices: List of zero-based page indices to move
            target_index: Zero-based index where pages should be inserted
            
        Raises:
            PageNotFoundError: If any index is out of range
        """
        if not indices:
            return
        
        # Validate all indices
        for idx in indices:
            if idx < 0 or idx >= len(self.pages):
                raise PageNotFoundError(
                    f"Page index {idx} out of range (0-{len(self.pages)-1})"
                )
        
        if target_index < 0 or target_index > len(self.pages):
            raise PageNotFoundError(
                f"Target index {target_index} out of range (0-{len(self.pages)})"
            )
        
        # Extract pages to move
        pages_to_move = [self.pages[idx] for idx in sorted(set(indices))]
        
        # Remove pages in reverse order
        for idx in sorted(set(indices), reverse=True):
            del self.pages[idx]
        
        # Adjust target index if needed
        adjusted_target = target_index
        for idx in sorted(set(indices)):
            if idx < target_index:
                adjusted_target -= 1
        
        # Insert pages at target position
        for i, page in enumerate(pages_to_move):
            self.pages.insert(adjusted_target + i, page)
    
    def export_pdf(self, output_path: str) -> None:
        """
        Export the working document to a new PDF file.
        
        Args:
            output_path: Path where the new PDF should be saved
            
        Raises:
            PDFError: If export fails
        """
        if not self.pages:
            raise PDFError("Cannot export empty document")
        
        try:
            writer = PdfWriter()
            
            # Add each page from references
            for page_ref in self.pages:
                reader = self.source_files.get(page_ref.file_path)
                if reader is None:
                    # File not in cache, open it
                    reader = PdfReader(page_ref.file_path)
                    self.source_files[page_ref.file_path] = reader
                
                # Add the specific page
                writer.add_page(reader.pages[page_ref.page_index])
            
            # Write to output file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
        except Exception as e:
            raise PDFError(f"Failed to export PDF: {e}")
    
    def get_page_info(self, index: int) -> Dict[str, any]:
        """
        Get metadata for a specific page.
        
        Args:
            index: Zero-based page index
            
        Returns:
            Dictionary containing page metadata:
                - width: Page width in points
                - height: Page height in points
                - rotation: Rotation angle in degrees
                - source_file: Path to source PDF
                - source_page: Original page number (1-based)
                
        Raises:
            PageNotFoundError: If index is out of range
        """
        if index < 0 or index >= len(self.pages):
            raise PageNotFoundError(
                f"Page index {index} out of range (0-{len(self.pages)-1})"
            )
        
        page_ref = self.pages[index]
        
        # Get the PDF reader
        reader = self.source_files.get(page_ref.file_path)
        if reader is None:
            reader = PdfReader(page_ref.file_path)
            self.source_files[page_ref.file_path] = reader
        
        # Get the page object
        page = reader.pages[page_ref.page_index]
        
        # Extract page properties
        mediabox = page.mediabox
        rotation = page.get('/Rotate', 0)
        
        return {
            'width': float(mediabox.width),
            'height': float(mediabox.height),
            'rotation': int(rotation),
            'source_file': page_ref.file_path,
            'source_page': page_ref.page_index + 1  # 1-based for display
        }
    
    def close(self) -> None:
        """Close all open PDF readers and clear the document."""
        self.source_files.clear()
        self.pages.clear()
