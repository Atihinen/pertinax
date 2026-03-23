"""
Unit tests for the page renderer module.
"""

import unittest
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pertinax.renderer import PageRenderer
from pertinax import PageReference


class TestPageRenderer(unittest.TestCase):
    """Tests for PageRenderer class."""
    
    def setUp(self):
        self.test_data_dir = Path(__file__).parent / 'data'
        self.pdf1 = str(self.test_data_dir / 'data-1.pdf')
        self.pdf2 = str(self.test_data_dir / 'data-2.pdf')
        self.renderer = PageRenderer()
    
    def tearDown(self):
        self.renderer.close()
    
    @pytest.mark.timeout(10)
    def test_render_thumbnail(self):
        """Test rendering a page thumbnail."""
        ref = PageReference(self.pdf1, 0)
        pixbuf = self.renderer.render_page_thumbnail(ref, 150, 200)
        
        # Check pixbuf dimensions
        self.assertIsNotNone(pixbuf)
        self.assertLessEqual(pixbuf.get_width(), 150)
        self.assertLessEqual(pixbuf.get_height(), 200)
        self.assertGreater(pixbuf.get_width(), 0)
        self.assertGreater(pixbuf.get_height(), 0)
    
    @pytest.mark.timeout(10)
    def test_render_preview(self):
        """Test rendering a full page preview."""
        ref = PageReference(self.pdf1, 0)
        pixbuf = self.renderer.render_page_preview(ref, 1.0)
        
        # Check pixbuf exists and has reasonable dimensions
        self.assertIsNotNone(pixbuf)
        self.assertGreater(pixbuf.get_width(), 100)
        self.assertGreater(pixbuf.get_height(), 100)
    
    @pytest.mark.timeout(10)
    def test_thumbnail_cache(self):
        """Test that thumbnails are cached."""
        ref = PageReference(self.pdf1, 0)
        
        # First render
        pixbuf1 = self.renderer.render_page_thumbnail(ref, 150, 200)
        
        # Second render should return cached version
        pixbuf2 = self.renderer.render_page_thumbnail(ref, 150, 200)
        
        # Should be the same object from cache
        self.assertIs(pixbuf1, pixbuf2)
    
    @pytest.mark.timeout(10)
    def test_clear_cache(self):
        """Test clearing the thumbnail cache."""
        ref = PageReference(self.pdf1, 0)
        
        # Render and cache
        pixbuf1 = self.renderer.render_page_thumbnail(ref, 150, 200)
        
        # Clear cache
        self.renderer.clear_cache()
        
        # Render again - should be different object
        pixbuf2 = self.renderer.render_page_thumbnail(ref, 150, 200)
        
        self.assertIsNot(pixbuf1, pixbuf2)
    
    @pytest.mark.timeout(10)
    def test_render_different_scales(self):
        """Test rendering at different scales."""
        ref = PageReference(self.pdf1, 0)
        
        pixbuf_50 = self.renderer.render_page_preview(ref, 0.5)
        pixbuf_100 = self.renderer.render_page_preview(ref, 1.0)
        pixbuf_150 = self.renderer.render_page_preview(ref, 1.5)
        
        # 150% should be larger than 100%, which should be larger than 50%
        self.assertLess(pixbuf_50.get_width(), pixbuf_100.get_width())
        self.assertLess(pixbuf_100.get_width(), pixbuf_150.get_width())
    
    @pytest.mark.timeout(10)
    def test_render_multiple_pages(self):
        """Test rendering different pages from same PDF."""
        ref0 = PageReference(self.pdf1, 0)
        ref1 = PageReference(self.pdf1, 1) if Path(self.pdf1).exists() else ref0
        
        pixbuf0 = self.renderer.render_page_thumbnail(ref0, 150, 200)
        pixbuf1 = self.renderer.render_page_thumbnail(ref1, 150, 200)
        
        self.assertIsNotNone(pixbuf0)
        self.assertIsNotNone(pixbuf1)
    
    @pytest.mark.timeout(10)
    def test_render_from_different_pdfs(self):
        """Test rendering pages from different PDF files."""
        ref1 = PageReference(self.pdf1, 0)
        ref2 = PageReference(self.pdf2, 0)
        
        pixbuf1 = self.renderer.render_page_thumbnail(ref1, 150, 200)
        pixbuf2 = self.renderer.render_page_thumbnail(ref2, 150, 200)
        
        self.assertIsNotNone(pixbuf1)
        self.assertIsNotNone(pixbuf2)
        # Should be different cached objects
        self.assertIsNot(pixbuf1, pixbuf2)


if __name__ == '__main__':
    unittest.main()
