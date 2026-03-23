# Pertinax PDF Compositor - Developer Guide

## Architecture Overview

Pertinax follows a clean Model-View architecture with three main layers:

1. **Core Module** (`src/pertinax/`) - PDF manipulation logic
2. **GUI Application** (`src/pertinax_gui.py`) - GTK 4 interface
3. **CLI Tool** (`src/pertinax_cli.py`) - Command-line interface

### Design Principles

- **Immutable source files**: PDFs are never modified
- **Page references**: Working document is a list of `(file_path, page_index)` tuples
- **No pip dependencies**: Only APT-installable packages
- **Minimal scope**: Focus on page organization only

## Module Structure

```
src/
├── pertinax/
│   ├── __init__.py           # Public API exports
│   ├── document.py           # PDFDocument class (core logic)
│   ├── page_reference.py     # PageReference data structure
│   ├── exceptions.py         # Custom exceptions
│   └── renderer.py           # Page rendering with Poppler
├── pertinax_gui.py           # GTK 4 GUI application
└── pertinax_cli.py           # CLI tool

tests/
├── data/                     # Test PDF fixtures
│   ├── data-1.pdf
│   └── data-2.pdf
├── test_document.py          # Unit tests for core module
└── test_renderer.py          # Unit tests for renderer
```

## Core Module API

### PDFDocument Class

Main document container that manages page references.

```python
from pertinax import PDFDocument

doc = PDFDocument()

# Open a PDF (clears existing document)
doc.open_pdf("input.pdf")

# Import additional pages
doc.import_pdf("other.pdf")

# Manipulate pages
doc.delete_pages([0, 2, 5])
doc.reorder_pages(old_index=3, new_index=0)
doc.move_pages(indices=[1, 2, 3], target_index=7)

# Export result
doc.export_pdf("output.pdf")

# Access page info
info = doc.get_page_info(0)
# Returns: {width, height, rotation, source_file, source_page}

# Properties
page_count = doc.page_count
page_list = doc.pages  # List[PageReference]

# Cleanup
doc.close()
```

### PageReference Class

Immutable reference to a specific page in a source PDF.

```python
from pertinax import PageReference

ref = PageReference(file_path="/path/to/file.pdf", page_index=0)

# Properties
ref.file_path    # Absolute path to source PDF
ref.page_index   # Zero-based page index

# Convert to tuple
file_path, page_idx = ref.as_tuple()
```

### PageRenderer Class

Renders PDF pages to GdkPixbuf using Poppler (GUI only).

```python
from pertinax.renderer import PageRenderer

renderer = PageRenderer()

# Render thumbnail
pixbuf = renderer.render_page_thumbnail(
    page_ref, 
    width=150, 
    height=200
)

# Render preview at scale
pixbuf = renderer.render_page_preview(
    page_ref,
    scale=1.0  # 1.0 = 100%, 1.5 = 150%, etc.
)

# Cache management
renderer.clear_cache()
renderer.close()
```

## GTK 4 GUI Architecture

### Application Structure

```
PertinaxApplication (Gtk.Application)
└── PertinaxWindow (Gtk.ApplicationWindow)
    ├── HeaderBar
    │   ├── Open Button
    │   ├── Import Button
    │   ├── Export Button
    │   └── Delete Button
    ├── Main Layout (Paned)
    │   ├── Thumbnail Sidebar (GridView)
    │   └── Preview Pane (Picture + Zoom)
    └── Status Bar
```

### Key Components

**PertinaxWindow** maintains:
- `self.document` - PDFDocument instance (model)
- `self.renderer` - PageRenderer instance
- `self.selected_indices` - Set of selected page indices
- `self.thumbnail_list_store` - Gio.ListStore for GridView

**PageItem** - GObject wrapper for list items:
```python
class PageItem(GObject.Object):
    def __init__(self, page_index, page_ref):
        self.page_index = page_index  # Display number
        self.page_ref = page_ref      # PageReference object
```

### Event Flow

1. **File Open**: FileDialog → `document.open_pdf()` → `_update_ui()` → render thumbnails
2. **Selection**: GridView selection changed → update `selected_indices` → render preview
3. **Delete**: Delete button → confirmation dialog → `document.delete_pages()` → `_update_ui()`
4. **Export**: FileDialog → `document.export_pdf()` → show success message

## Development Setup

### Prerequisites

Ubuntu 24.04 or 22.04 LTS with:

```bash
sudo apt-get install -y \
    python3 \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-poppler-0.18 \
    python3-cairo \
    xvfb
```

### Virtual Environment

Create venv with system site-packages to access GTK:

```bash
python3 -m venv --system-site-packages ~/.venvs/pertinax
source ~/.venvs/pertinax/bin/activate
pip install pypdf ruff pytest pytest-timeout
```

### Running Tests

```bash
# Core module tests
python3 tests/test_document.py

# Renderer tests (requires X display)
timeout 30 xvfb-run -a python3 tests/test_renderer.py

# With ruff linting
ruff check src/
```

### Running the GUI

```bash
# In X11 environment
python3 src/pertinax_gui.py

# In WSL/headless with X forwarding
export DISPLAY=:0
python3 src/pertinax_gui.py

# In xvfb for testing
xvfb-run -a python3 src/pertinax_gui.py
```

## Testing Strategy

### Unit Tests

- **test_document.py**: Tests all PDFDocument operations
  - Uses `tests/data/data-1.pdf` and `tests/data/data-2.pdf` fixtures
  - Verifies source PDFs remain unmodified
  - Tests error handling

- **test_renderer.py**: Tests page rendering
  - Requires X display (use xvfb-run)
  - Tests thumbnail and preview rendering
  - Tests caching behavior
  - All tests have 10-second timeout decorators

### Running Tests with Timeout

Always use bash-level timeout to prevent hanging:

```bash
timeout 30 xvfb-run -a python3 tests/test_renderer.py
```

### Manual Testing Checklist

- [ ] Open PDF with multiple pages
- [ ] Import second PDF
- [ ] Select and view different pages
- [ ] Multi-select with Ctrl+click
- [ ] Delete pages (single and multiple)
- [ ] Confirm large deletion dialog (>5 pages)
- [ ] Export to new PDF and verify
- [ ] Verify source PDFs unchanged
- [ ] Test keyboard shortcuts
- [ ] Test with large PDFs (100+ pages)

## Code Style

### Linting

```bash
ruff check src/ tests/
```

### Import Organization

```python
# Standard library
import sys
from pathlib import Path

# Third-party (system packages)
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk  # noqa: E402

# Local modules
from pertinax import PDFDocument  # noqa: E402
```

Note: `# noqa: E402` is required for gi.require_version pattern.

### Type Hints

Use type hints for function signatures:

```python
def delete_pages(self, indices: List[int]) -> None:
    """Delete pages at specified indices."""
    ...
```

## Packaging

### Debian Package Structure

```
debian/
├── control          # Dependencies and metadata
├── rules            # Build instructions
├── install          # File installation mapping
├── copyright        # License information
└── changelog        # Version history
```

### Dependencies

System packages required:
- `python3` (>= 3.10)
- `python3-gi`
- `python3-gi-cairo`
- `gir1.2-gtk-4.0`
- `gir1.2-poppler-0.18`
- `python3-pypdf` or `python3-pypdf2`
- `python3-cairo`

### Installation Paths

- `/usr/bin/pertinax` - GUI launcher script
- `/usr/bin/pertinax-cli` - CLI tool
- `/usr/lib/python3/dist-packages/pertinax/` - Python module
- `/usr/share/applications/pertinax.desktop` - Desktop entry
- `/usr/share/icons/hicolor/*/apps/pertinax.png` - Application icon

## Contributing

### Adding Features

Before implementing new features, consider:

1. **Does it fit the minimal scope?** Pertinax intentionally avoids complex PDF editing
2. **Can it be done without pip dependencies?** All dependencies must be APT-installable
3. **Does it maintain immutability?** Source PDFs must never be modified

### Pull Request Process

1. Write unit tests for new functionality
2. Run ruff linting
3. Test with actual PDF files
4. Update documentation
5. Ensure backward compatibility

### Known Limitations

- No cross-window drag-and-drop (by design)
- No PDF rotation (consider adding to Phase 3)
- No page cropping (out of scope)
- Limited to Ubuntu LTS (Debian derivatives may work)

## Troubleshooting Development Issues

### GTK Import Errors

If `import gi` fails, venv was created without `--system-site-packages`:

```bash
rm -rf ~/.venvs/pertinax
python3 -m venv --system-site-packages ~/.venvs/pertinax
```

### Poppler Rendering Errors

Check Poppler version compatibility:

```bash
pkg-config --modversion poppler-glib
```

Ensure gir1.2-poppler-0.18 is installed.

### xvfb Tests Timeout

Always use bash `timeout` command:

```bash
timeout 30 xvfb-run -a python3 tests/test_renderer.py
```

If tests hang immediately, check for pytest issues - use unittest directly:

```bash
python3 tests/test_renderer.py
```

## API Stability

### Public API (Stable)

- `PDFDocument` class and all its methods
- `PageReference` class
- `PDFError` and `PageNotFoundError` exceptions

### Internal API (May Change)

- `PageRenderer` implementation details
- GUI widget structure
- Cache implementation

## Future Enhancements

Potential Phase 3 features:

- Drag-and-drop page reordering in GUI
- Page rotation support
- Thumbnail quality settings
- Memory usage optimization for large PDFs
- Progress bars for slow operations
- Undo/redo functionality

## Resources

- GTK 4 Documentation: https://docs.gtk.org/gtk4/
- Poppler Documentation: https://poppler.freedesktop.org/
- PyGObject Guide: https://pygobject.readthedocs.io/
- pypdf Documentation: https://pypdf.readthedocs.io/
