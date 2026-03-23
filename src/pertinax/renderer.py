"""
PDF page rendering module using Poppler.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional
import gi

gi.require_version('Poppler', '0.18')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Poppler, GdkPixbuf, Gdk  # noqa: E402
import cairo  # noqa: E402

from .page_reference import PageReference  # noqa: E402
from .exceptions import PDFError  # noqa: E402


class PageRenderer:
    """
    Renders PDF pages to GdkPixbuf using Poppler.
    
    Maintains a cache of rendered thumbnails to avoid re-rendering.
    """
    
    def __init__(self):
        """Initialize renderer with empty cache."""
        self._thumbnail_cache: Dict[Tuple[str, int, int, int, Optional[int]], GdkPixbuf.Pixbuf] = {}
        self._poppler_docs: Dict[str, Poppler.Document] = {}
    
    def _get_poppler_document(self, file_path: str) -> Poppler.Document:
        """
        Get or create a Poppler document for the given file.
        
        Args:
            file_path: Absolute path to PDF file
            
        Returns:
            Poppler.Document instance
            
        Raises:
            PDFError: If document cannot be opened
        """
        if file_path not in self._poppler_docs:
            try:
                uri = Path(file_path).as_uri()
                doc = Poppler.Document.new_from_file(uri, None)
                if doc is None:
                    raise PDFError(f"Failed to open PDF: {file_path}")
                self._poppler_docs[file_path] = doc
            except Exception as e:
                raise PDFError(f"Failed to open PDF with Poppler: {e}")
        
        return self._poppler_docs[file_path]
    
    def render_page_thumbnail(
        self,
        page_ref: PageReference,
        width: int,
        height: int,
        page_number: int = None
    ) -> GdkPixbuf.Pixbuf:
        """
        Render a page as a thumbnail.
        
        Args:
            page_ref: Page reference to render
            width: Target thumbnail width in pixels
            height: Target thumbnail height in pixels
            page_number: Optional page number to display as overlay badge
            
        Returns:
            GdkPixbuf containing rendered thumbnail
            
        Raises:
            PDFError: If rendering fails
        """
        # Check cache (including page_number in key for unique caching)
        cache_key = (page_ref.file_path, page_ref.page_index, width, height, page_number)
        if cache_key in self._thumbnail_cache:
            return self._thumbnail_cache[cache_key]
        
        try:
            # Get Poppler document and page
            doc = self._get_poppler_document(page_ref.file_path)
            page = doc.get_page(page_ref.page_index)
            
            if page is None:
                raise PDFError(
                    f"Page {page_ref.page_index} not found in {page_ref.file_path}"
                )
            
            # Get page dimensions
            page_width, page_height = page.get_size()
            
            # Calculate scaling to fit within thumbnail bounds
            scale_x = width / page_width
            scale_y = height / page_height
            scale = min(scale_x, scale_y)
            
            # Calculate actual thumbnail dimensions
            thumb_width = int(page_width * scale)
            thumb_height = int(page_height * scale)
            
            # Create Cairo surface
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                thumb_width,
                thumb_height
            )
            ctx = cairo.Context(surface)
            
            # White background
            ctx.set_source_rgb(1, 1, 1)
            ctx.paint()
            
            # Scale and render page
            ctx.scale(scale, scale)
            page.render(ctx)
            
            # Draw page number badge if provided
            if page_number is not None:
                # Reset scaling for badge
                ctx.identity_matrix()
                
                # Prepare text
                page_text = str(page_number)
                ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                ctx.set_font_size(16)
                
                # Get text dimensions
                text_extents = ctx.text_extents(page_text)
                text_width = text_extents.width
                text_height = text_extents.height
                
                # Badge dimensions with padding
                padding = 6
                badge_width = text_width + 2 * padding
                badge_height = text_height + 2 * padding
                badge_x = 8
                badge_y = 8
                
                # Draw semi-transparent dark background
                ctx.set_source_rgba(0, 0, 0, 0.7)
                ctx.rectangle(badge_x, badge_y, badge_width, badge_height)
                ctx.fill()
                
                # Draw white text
                ctx.set_source_rgb(1, 1, 1)
                ctx.move_to(
                    badge_x + padding - text_extents.x_bearing,
                    badge_y + padding - text_extents.y_bearing
                )
                ctx.show_text(page_text)
            
            # Convert Cairo surface to GdkPixbuf using gdk-pixbuf's built-in method
            pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, thumb_width, thumb_height)
            
            # Cache the result
            self._thumbnail_cache[cache_key] = pixbuf
            
            return pixbuf
            
        except Exception as e:
            raise PDFError(f"Failed to render thumbnail: {e}")
    
    def render_page_preview(
        self,
        page_ref: PageReference,
        scale: float = 1.0
    ) -> GdkPixbuf.Pixbuf:
        """
        Render a page at full resolution for preview.
        
        Args:
            page_ref: Page reference to render
            scale: Scaling factor (1.0 = 100%, 1.5 = 150%, etc.)
            
        Returns:
            GdkPixbuf containing rendered page
            
        Raises:
            PDFError: If rendering fails
        """
        try:
            # Get Poppler document and page
            doc = self._get_poppler_document(page_ref.file_path)
            page = doc.get_page(page_ref.page_index)
            
            if page is None:
                raise PDFError(
                    f"Page {page_ref.page_index} not found in {page_ref.file_path}"
                )
            
            # Get page dimensions
            page_width, page_height = page.get_size()
            
            # Calculate scaled dimensions
            width = int(page_width * scale)
            height = int(page_height * scale)
            
            # Create Cairo surface
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)
            
            # White background
            ctx.set_source_rgb(1, 1, 1)
            ctx.paint()
            
            # Scale and render page
            ctx.scale(scale, scale)
            page.render(ctx)
            
            # Convert Cairo surface to GdkPixbuf using gdk-pixbuf's built-in method
            pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
            
            return pixbuf
            
        except Exception as e:
            raise PDFError(f"Failed to render preview: {e}")
    
    def clear_cache(self) -> None:
        """Clear the thumbnail cache."""
        self._thumbnail_cache.clear()
    
    def close(self) -> None:
        """Close all Poppler documents and clear cache."""
        self._poppler_docs.clear()
        self._thumbnail_cache.clear()
