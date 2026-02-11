"""
Unit tests for the Pertinax PDF module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pertinax import PDFDocument, PageReference, PDFError, PageNotFoundError


class TestPageReference(unittest.TestCase):
    """Tests for PageReference class."""
    
    def setUp(self):
        self.test_data_dir = Path(__file__).parent / 'data'
        self.pdf1 = str(self.test_data_dir / 'data-1.pdf')
        self.pdf2 = str(self.test_data_dir / 'data-2.pdf')
    
    def test_create_page_reference(self):
        """Test creating a valid page reference."""
        ref = PageReference(self.pdf1, 0)
        self.assertEqual(ref.page_index, 0)
        self.assertTrue(ref.file_path.endswith('data-1.pdf'))
    
    def test_page_reference_nonexistent_file(self):
        """Test that creating a reference to nonexistent file raises error."""
        with self.assertRaises(PDFError):
            PageReference('/nonexistent/file.pdf', 0)
    
    def test_page_reference_negative_index(self):
        """Test that negative page index raises error."""
        with self.assertRaises(PDFError):
            PageReference(self.pdf1, -1)
    
    def test_page_reference_equality(self):
        """Test page reference equality comparison."""
        ref1 = PageReference(self.pdf1, 0)
        ref2 = PageReference(self.pdf1, 0)
        ref3 = PageReference(self.pdf1, 1)
        
        self.assertEqual(ref1, ref2)
        self.assertNotEqual(ref1, ref3)
    
    def test_page_reference_repr(self):
        """Test page reference string representation."""
        ref = PageReference(self.pdf1, 0)
        repr_str = repr(ref)
        self.assertIn('PageReference', repr_str)
        self.assertIn('data-1.pdf', repr_str)
        self.assertIn('0', repr_str)
    
    def test_page_reference_as_tuple(self):
        """Test converting page reference to tuple."""
        ref = PageReference(self.pdf1, 2)
        file_path, page_idx = ref.as_tuple()
        self.assertTrue(file_path.endswith('data-1.pdf'))
        self.assertEqual(page_idx, 2)


class TestPDFDocument(unittest.TestCase):
    """Tests for PDFDocument class."""
    
    def setUp(self):
        self.test_data_dir = Path(__file__).parent / 'data'
        self.pdf1 = str(self.test_data_dir / 'data-1.pdf')
        self.pdf2 = str(self.test_data_dir / 'data-2.pdf')
        self.temp_dir = tempfile.mkdtemp()
        self.doc = PDFDocument()
    
    def tearDown(self):
        self.doc.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_document(self):
        """Test initial state of empty document."""
        self.assertEqual(self.doc.page_count, 0)
        self.assertEqual(len(self.doc.pages), 0)
    
    def test_open_pdf(self):
        """Test opening a PDF file."""
        self.doc.open_pdf(self.pdf1)
        self.assertGreater(self.doc.page_count, 0)
        
        # Verify all pages reference the same file
        for page_ref in self.doc.pages:
            self.assertTrue(page_ref.file_path.endswith('data-1.pdf'))
    
    def test_open_nonexistent_pdf(self):
        """Test opening a nonexistent file raises error."""
        with self.assertRaises(PDFError):
            self.doc.open_pdf('/nonexistent/file.pdf')
    
    def test_open_replaces_document(self):
        """Test that opening a PDF replaces the current document."""
        self.doc.open_pdf(self.pdf1)
        count1 = self.doc.page_count
        
        self.doc.open_pdf(self.pdf2)
        count2 = self.doc.page_count
        
        # Should have new pages only, not combined
        self.assertNotEqual(count1 + count2, self.doc.page_count)
        
        # All pages should be from pdf2
        for page_ref in self.doc.pages:
            self.assertTrue(page_ref.file_path.endswith('data-2.pdf'))
    
    def test_import_pdf(self):
        """Test importing pages from another PDF."""
        self.doc.open_pdf(self.pdf1)
        count1 = self.doc.page_count
        
        self.doc.import_pdf(self.pdf2)
        total = self.doc.page_count
        
        self.assertGreater(total, count1)
        
        # First pages should be from pdf1
        self.assertTrue(self.doc.pages[0].file_path.endswith('data-1.pdf'))
        # Last pages should be from pdf2
        self.assertTrue(self.doc.pages[-1].file_path.endswith('data-2.pdf'))
    
    def test_import_nonexistent_pdf(self):
        """Test importing a nonexistent file raises error."""
        self.doc.open_pdf(self.pdf1)
        with self.assertRaises(PDFError):
            self.doc.import_pdf('/nonexistent/file.pdf')
    
    def test_delete_pages(self):
        """Test deleting pages."""
        self.doc.open_pdf(self.pdf1)
        initial_count = self.doc.page_count
        
        # Delete first and last page
        self.doc.delete_pages([0, initial_count - 1])
        
        self.assertEqual(self.doc.page_count, initial_count - 2)
    
    def test_delete_invalid_index(self):
        """Test deleting invalid page index raises error."""
        self.doc.open_pdf(self.pdf1)
        
        with self.assertRaises(PageNotFoundError):
            self.doc.delete_pages([999])
    
    def test_delete_negative_index(self):
        """Test deleting negative index raises error."""
        self.doc.open_pdf(self.pdf1)
        
        with self.assertRaises(PageNotFoundError):
            self.doc.delete_pages([-1])
    
    def test_reorder_pages(self):
        """Test reordering pages."""
        self.doc.open_pdf(self.pdf1)
        
        if self.doc.page_count < 2:
            self.skipTest("Need at least 2 pages for reorder test")
        
        # Get original first page
        original_first = self.doc.pages[0]
        
        # Move first page to second position
        self.doc.reorder_pages(0, 1)
        
        # First page should now be at index 1
        self.assertEqual(self.doc.pages[1], original_first)
    
    def test_reorder_invalid_index(self):
        """Test reordering with invalid index raises error."""
        self.doc.open_pdf(self.pdf1)
        
        with self.assertRaises(PageNotFoundError):
            self.doc.reorder_pages(0, 999)
    
    def test_move_pages(self):
        """Test moving multiple pages."""
        self.doc.open_pdf(self.pdf1)
        
        if self.doc.page_count < 4:
            self.skipTest("Need at least 4 pages for move test")
        
        # Get original pages
        page0 = self.doc.pages[0]
        page2 = self.doc.pages[2]
        
        # Move pages 0 and 2 to position 1
        self.doc.move_pages([0, 2], 1)
        
        # After moving [0, 2] to position 1:
        # - Remove pages at 0 and 2
        # - Insert them at adjusted position (0, since we removed index 0 before target 1)
        # Result should be: [page0, page2, original_page1, original_page3, ...]
        self.assertEqual(self.doc.pages[0], page0)
        self.assertEqual(self.doc.pages[1], page2)
    
    def test_move_pages_invalid_index(self):
        """Test moving pages with invalid index raises error."""
        self.doc.open_pdf(self.pdf1)
        
        with self.assertRaises(PageNotFoundError):
            self.doc.move_pages([0, 999], 1)
    
    def test_export_pdf(self):
        """Test exporting to a new PDF file."""
        self.doc.open_pdf(self.pdf1)
        output_path = Path(self.temp_dir) / 'output.pdf'
        
        self.doc.export_pdf(str(output_path))
        
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)
    
    def test_export_empty_document(self):
        """Test that exporting empty document raises error."""
        with self.assertRaises(PDFError):
            self.doc.export_pdf('/tmp/output.pdf')
    
    def test_export_combined_pdf(self):
        """Test exporting after combining multiple PDFs."""
        self.doc.open_pdf(self.pdf1)
        
        self.doc.import_pdf(self.pdf2)
        total = self.doc.page_count
        
        output_path = Path(self.temp_dir) / 'combined.pdf'
        self.doc.export_pdf(str(output_path))
        
        self.assertTrue(output_path.exists())
        
        # Verify the exported PDF has the correct number of pages
        from pypdf import PdfReader
        reader = PdfReader(str(output_path))
        self.assertEqual(len(reader.pages), total)
    
    def test_get_page_info(self):
        """Test getting page metadata."""
        self.doc.open_pdf(self.pdf1)
        
        info = self.doc.get_page_info(0)
        
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('rotation', info)
        self.assertIn('source_file', info)
        self.assertIn('source_page', info)
        
        self.assertGreater(info['width'], 0)
        self.assertGreater(info['height'], 0)
        self.assertEqual(info['source_page'], 1)  # 1-based
    
    def test_get_page_info_invalid_index(self):
        """Test getting info for invalid page raises error."""
        self.doc.open_pdf(self.pdf1)
        
        with self.assertRaises(PageNotFoundError):
            self.doc.get_page_info(999)
    
    def test_source_pdfs_unchanged_after_operations(self):
        """Test that source PDFs remain unmodified after all operations."""
        # Get original file sizes and modification times
        pdf1_path = Path(self.pdf1)
        pdf2_path = Path(self.pdf2)
        
        pdf1_size_before = pdf1_path.stat().st_size
        pdf2_size_before = pdf2_path.stat().st_size
        pdf1_mtime_before = pdf1_path.stat().st_mtime
        pdf2_mtime_before = pdf2_path.stat().st_mtime
        
        # Perform operations
        self.doc.open_pdf(self.pdf1)
        self.doc.import_pdf(self.pdf2)
        
        if self.doc.page_count > 2:
            self.doc.delete_pages([1])
        if self.doc.page_count > 1:
            self.doc.reorder_pages(0, 1)
        
        output_path = Path(self.temp_dir) / 'result.pdf'
        self.doc.export_pdf(str(output_path))
        
        # Verify source files unchanged
        pdf1_size_after = pdf1_path.stat().st_size
        pdf2_size_after = pdf2_path.stat().st_size
        pdf1_mtime_after = pdf1_path.stat().st_mtime
        pdf2_mtime_after = pdf2_path.stat().st_mtime
        
        self.assertEqual(pdf1_size_before, pdf1_size_after)
        self.assertEqual(pdf2_size_before, pdf2_size_after)
        self.assertEqual(pdf1_mtime_before, pdf1_mtime_after)
        self.assertEqual(pdf2_mtime_before, pdf2_mtime_after)


class TestComplexOperations(unittest.TestCase):
    """Tests for complex multi-step operations."""
    
    def setUp(self):
        self.test_data_dir = Path(__file__).parent / 'data'
        self.pdf1 = str(self.test_data_dir / 'data-1.pdf')
        self.pdf2 = str(self.test_data_dir / 'data-2.pdf')
        self.temp_dir = tempfile.mkdtemp()
        self.doc = PDFDocument()
    
    def tearDown(self):
        self.doc.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_open_import_delete_export(self):
        """Test complete workflow: open, import, delete, export."""
        # Open first PDF
        self.doc.open_pdf(self.pdf1)
        
        # Import second PDF
        self.doc.import_pdf(self.pdf2)
        count_total = self.doc.page_count
        
        # Delete some pages
        if count_total > 2:
            self.doc.delete_pages([0, count_total - 1])
        
        # Export
        output_path = Path(self.temp_dir) / 'workflow.pdf'
        self.doc.export_pdf(str(output_path))
        
        self.assertTrue(output_path.exists())
    
    def test_multiple_imports(self):
        """Test importing the same file multiple times."""
        self.doc.open_pdf(self.pdf1)
        count1 = self.doc.page_count
        
        self.doc.import_pdf(self.pdf1)
        self.doc.import_pdf(self.pdf1)
        
        # Should have 3x the pages
        self.assertEqual(self.doc.page_count, count1 * 3)
    
    def test_delete_all_then_import(self):
        """Test deleting all pages then importing new ones."""
        self.doc.open_pdf(self.pdf1)
        
        # Delete all pages
        all_indices = list(range(self.doc.page_count))
        self.doc.delete_pages(all_indices)
        
        self.assertEqual(self.doc.page_count, 0)
        
        # Import new pages
        self.doc.import_pdf(self.pdf2)
        self.assertGreater(self.doc.page_count, 0)


if __name__ == '__main__':
    unittest.main()
