# Phase 1: PDF Module (Core Logic)

## Goal

Build a standalone Python module for PDF page composition that uses pypdf for manipulation and generation. This module operates on immutable page references and provides all core PDF operations without any GUI dependencies.

## Tasks

### 1. Create Module Structure

- Create `src/pertinax/` package directory
- Add `src/pertinax/__init__.py` to export public API
- Create `src/pertinax/document.py` for main document class
- Create `src/pertinax/page_reference.py` for page reference data structure

**Deliverable:** Basic package structure that can be imported

### 2. Implement Page Reference Model

- Define `PageReference` class with `(file_path, page_index)` attributes
- Add validation to ensure file exists and page index is valid
- Implement `__repr__` and `__eq__` for debugging and testing

**Deliverable:** Immutable page reference object

### 3. Build PDFDocument Class

- Create `PDFDocument` class in `document.py`
- Initialize with empty list of page references: `self.pages = []`
- Track source PDF files opened: `self.source_files = {}`
- Add property to get total page count

**Deliverable:** Core document container

### 4. Implement open_pdf() Operation

- `open_pdf(file_path)` method that:
  - Opens PDF using pypdf's `PdfReader`
  - Clears current working document
  - Creates page references for all pages: `[(file_path, 0), (file_path, 1), ...]`
  - Stores file handle in `source_files` dict
- Validate PDF is readable before creating references

**Deliverable:** Ability to open a PDF into working document

### 5. Implement import_pdf() Operation

- `import_pdf(file_path)` method that:
  - Opens PDF using pypdf's `PdfReader`
  - Appends page references to existing `self.pages` list
  - Stores file handle in `source_files` dict
- Does not modify or merge existing pages

**Deliverable:** Ability to append pages from additional PDFs

### 6. Implement Page Manipulation Operations

- `delete_pages(indices)` - Remove pages at specified indices
- `reorder_pages(old_index, new_index)` - Move page to new position
- `move_pages(indices, target_index)` - Move multiple pages to target position
- All operations modify `self.pages` list only, never source files

**Deliverable:** Complete page manipulation API

### 7. Implement export_pdf() Operation

- `export_pdf(output_path)` method that:
  - Creates new `PdfWriter` from pypdf
  - Iterates through `self.pages` references
  - For each reference, opens source PDF and reads specified page
  - Adds page to writer
  - Writes final PDF to `output_path`
- Never modifies source PDFs

**Deliverable:** Ability to generate new PDF from page references

### 8. Add Page Metadata Access

- `get_page_info(index)` method returning:
  - Width and height (from pypdf page object)
  - Rotation angle
  - Source file path
  - Original page number
- Useful for GUI thumbnail rendering in Phase 2

**Deliverable:** Page metadata API for future GUI needs

### 9. Create CLI Testing Tool

- Create `src/pertinax_cli.py` script
- Implement commands:
  - `open <pdf>` - Open PDF
  - `import <pdf>` - Import additional PDF
  - `delete <indices>` - Delete pages (e.g., "1,3,5")
  - `move <from> <to>` - Reorder page
  - `list` - Show current page references
  - `export <output>` - Save to new PDF
- Use argparse or simple command loop

**Deliverable:** CLI tool to test module without GUI

### 10. Add Error Handling

- Handle file not found errors
- Handle invalid page indices
- Handle corrupted PDFs
- Add proper exception types: `PDFError`, `PageNotFoundError`
- Close file handles properly

**Deliverable:** Robust error handling

### 11. Write Unit Tests

- Create `tests/test_document.py`
- Create test data directory `tests/data/`
- Use `tests/data/data-1.pdf` and `tests/data/data-2.pdf` as test fixtures
- Test all operations with these sample PDFs:
  - Open data-1.pdf
  - Import data-2.pdf
  - Delete, reorder, and move operations
  - Export combined PDF
- Test error conditions
- Verify source PDFs (`data-1.pdf`, `data-2.pdf`) remain unmodified after all operations

**Deliverable:** Test suite for core module with dedicated test PDF files

## Success Criteria

- [ ] Can open a PDF and see page references
- [ ] Can import additional PDFs
- [ ] Can delete and reorder pages via CLI
- [ ] Can export new PDF successfully
- [ ] Source PDFs are never modified
- [ ] All operations work without GUI dependencies
- [ ] Module uses only pypdf (APT-installable)

## Dependencies

- `python3-pypdf` (or `python3-pypdf2`) from Ubuntu LTS repos
- Standard library only (pathlib, typing, etc.)

## Output

A complete `pertinax` Python module that can be imported and used programmatically or via CLI, ready for GUI integration in Phase 2.
