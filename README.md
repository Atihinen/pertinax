# Pertinax PDF Compositor

A minimal PDF page compositor for Linux (Ubuntu LTS) that allows you to organize PDF pages without modifying source files. Similar to macOS Preview's page management features.

## Features

- **Open and Import PDFs** - Load multiple PDF files into one working document
- **Thumbnail Sidebar** - Visual grid of all pages with page numbers
- **Preview Pane** - Full-size page preview with zoom controls
- **Page Deletion** - Remove unwanted pages (with confirmation for large deletions)
- **Page Reordering** - Rearrange pages via CLI (GUI drag-drop in development)
- **Export** - Save your organized document as a new PDF
- **Immutable Sources** - Original PDF files are never modified
- **Keyboard Shortcuts** - Ctrl+O/I/S, Delete, Ctrl+A, Escape

## What Pertinax is NOT

Pertinax is **intentionally minimal** and does NOT provide:
- Text editing, annotations, forms
- OCR, metadata editing, encryption
- Page rotation or cropping (yet)
- Cloud sync, plugins

## Installation

### Prerequisites

Ubuntu 22.04 LTS or 24.04 LTS with:

```bash
sudo apt-get install -y \
    python3 \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-poppler-0.18 \
    python3-pypdf \
    python3-cairo
```

### From Source

```bash
git clone https://github.com/example/pertinax
cd pertinax

# Create venv with system site-packages (for GTK access)
python3 -m venv --system-site-packages ~/.venvs/pertinax
source ~/.venvs/pertinax/bin/activate
pip install pypdf

# Run GUI
python3 src/pertinax_gui.py

# Or run CLI
python3 src/pertinax_cli.py
```

### From .deb Package

```bash
sudo dpkg -i pertinax_*.deb
sudo apt-get install -f  # Install dependencies

# Launch from application menu or:
pertinax          # GUI
pertinax-cli      # CLI
```

## Quick Start

### GUI Application

1. Click **Open** to load a PDF
2. Click **Import** to add pages from another PDF
3. Select pages in the thumbnail sidebar
4. Press **Delete** to remove unwanted pages
5. Click **Export** to save your organized PDF

### CLI Tool

```bash
$ pertinax-cli
> open document.pdf
Opened: document.pdf
Pages: 10

> import extra.pdf
Imported: extra.pdf
Added 5 pages (total: 15)

> list
Document has 15 pages:
  0: document.pdf [page 1]
  1: document.pdf [page 2]
  ...

> delete 2,5,7
Deleted 3 page(s)

> move 0 5
Moved page from index 0 to 5

> export result.pdf
Exported to result.pdf
```

## Documentation

- [User Guide](docs/user-guide.md) - Complete usage instructions
- [Developer Guide](docs/developer-guide.md) - Architecture and API documentation

## Development

### Setup

```bash
# Create venv with system-site-packages
python3 -m venv --system-site-packages ~/.venvs/pertinax
source ~/.venvs/pertinax/bin/activate
pip install pypdf ruff pytest pytest-timeout
```

### Running Tests

```bash
# Core module tests (35 tests)
python3 tests/test_document.py
python3 tests/test_renderer.py

# Linting
ruff check src/ tests/

# GUI automated tests (currently not working in headless mode)
# See tests/gui/README.md for details and workarounds
# ./run_gui_tests.sh  # Requires real X11 display, not Xvfb
```

**Note:** GUI tests using Robot Framework + dogtail cannot run in Xvfb/headless mode due to GTK 4 not registering with AT-SPI accessibility tree. Use manual testing or real X11 display. See [tests/gui/README.md](tests/gui/README.md) for details.

### Manual GUI Testing

Critical test cases to verify manually:
1. **Empty State**: Launch app, verify empty state with "Open a PDF" message
2. **Button States**: Verify Export/Insert/Delete disabled when no PDF loaded  
3. **Open PDF**: Load a multi-page PDF, verify thumbnails appear with page numbers
4. **Drag and Drop**: Drag page thumbnail to new position - **app must not crash**
5. **Keyboard Shortcuts**: Ctrl+O (open), Ctrl+E (export), Escape (close dialogs)

### Project Structure

```
src/
├── pertinax/           # Core module
│   ├── document.py     # PDFDocument class
│   ├── page_reference.py
│   ├── renderer.py     # Poppler rendering
│   └── exceptions.py
├── pertinax_gui.py     # GTK 4 GUI
└── pertinax_cli.py     # CLI tool

tests/
├── data/               # Test PDF fixtures
├── test_document.py
└── test_renderer.py

debian/                 # Packaging
docs/                   # Documentation
```

## Architecture

Pertinax uses an **immutable page reference** system:

1. Opening/importing creates references: `(file_path, page_index)`
2. Working document = list of references
3. Operations (delete, reorder) modify the reference list only
4. Export creates a new PDF from references
5. Source PDFs remain untouched

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF |
| `Ctrl+I` | Import PDF |
| `Ctrl+S` | Export/Save As |
| `Delete` | Delete selected pages |
| `Ctrl+A` | Select all |
| `Escape` | Clear selection |

## Requirements

- Ubuntu 22.04 LTS or 24.04 LTS
- Python 3.10+
- GTK 4
- Poppler
- pypdf

## License

MIT License - see [LICENSE](LICENSE) file

## Contributing

See [Developer Guide](docs/developer-guide.md) for architecture details.

## Project Status

- ✅ Phase 1: Core PDF module with CLI
- ✅ Phase 2: GTK 4 GUI application  
- 🚧 Phase 3: Drag-drop reordering, polishing

## Support

- Bug reports: GitHub Issues
- Documentation: See `docs/` directory
- This is a minimal tool by design - complex features may not be added
