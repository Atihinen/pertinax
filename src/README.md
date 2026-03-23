# Pertinax PDF Module (Phase 1)

A minimal PDF page compositor module for Linux that operates on immutable page references.

## Features

- **Immutable page references**: PDFs are treated as read-only sources
- **Page composition**: Open, import, reorder, delete, and combine PDF pages
- **Export only**: Creates new PDFs without modifying source files
- **CLI tool**: Test all functionality from the command line

## Installation

Requires Python 3 and pypdf:

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt install python3 python3-pypdf

# Or with pip in a virtual environment
pip install pypdf
```

## Usage

### As a Python Module

```python
from pertinax import PDFDocument

# Create a new document
doc = PDFDocument()

# Open a PDF
doc.open_pdf('document1.pdf')

# Import pages from another PDF
doc.import_pdf('document2.pdf')

# Delete specific pages
doc.delete_pages([0, 5, 10])

# Reorder pages
doc.reorder_pages(old_index=2, new_index=0)

# Move multiple pages
doc.move_pages(indices=[1, 3, 5], target_index=10)

# Get page information
info = doc.get_page_info(0)
print(f"Page size: {info['width']} x {info['height']}")

# Export to new PDF
doc.export_pdf('output.pdf')
```

### CLI Tool

```bash
# Interactive mode
python3 src/pertinax_cli.py

# Single command
python3 src/pertinax_cli.py open document.pdf
```

CLI commands:
- `open <file>` - Open a PDF file
- `import <file>` - Import pages from another PDF
- `list` - List all pages in the working document
- `info <index>` - Show detailed page information
- `delete <indices>` - Delete pages (e.g., "1,3,5")
- `move <from> <to>` - Move a page to a new position
- `export <file>` - Save working document to new PDF
- `help` - Show available commands
- `quit` - Exit

## Architecture

### Core Classes

**PageReference** (`src/pertinax/page_reference.py`)
- Immutable reference to a PDF page: `(file_path, page_index)`
- Validates file existence and page indices

**PDFDocument** (`src/pertinax/document.py`)
- Main document class that manages page references
- All operations manipulate in-memory references only
- Export creates new PDF from references

**Exceptions** (`src/pertinax/exceptions.py`)
- `PDFError` - Base exception for PDF operations
- `PageNotFoundError` - Invalid page index errors

### Key Operations

1. **open_pdf(file_path)** - Clears document and loads pages from a PDF
2. **import_pdf(file_path)** - Appends pages from another PDF
3. **delete_pages(indices)** - Removes pages at specified indices
4. **reorder_pages(old_index, new_index)** - Moves a single page
5. **move_pages(indices, target_index)** - Moves multiple pages
6. **export_pdf(output_path)** - Writes new PDF from page references
7. **get_page_info(index)** - Returns page metadata (size, rotation, source)

## Testing

Run the test suite:

```bash
python3 -m unittest tests.test_document -v
```

Test coverage includes:
- Page reference creation and validation
- All document operations (open, import, delete, reorder, move, export)
- Error handling for invalid inputs
- Verification that source PDFs remain unmodified
- Complex multi-step workflows

## Success Criteria

✅ Can open a PDF and create page references  
✅ Can import additional PDFs  
✅ Can delete and reorder pages via CLI  
✅ Can export new PDF successfully  
✅ Source PDFs are never modified  
✅ All operations work without GUI dependencies  
✅ Module uses only pypdf (APT-installable)  
✅ Comprehensive test suite with 28 tests  
✅ CLI tool for testing all functionality  

## Next Steps

Phase 2 will add a GTK 4 GUI application on top of this module.
