# Pertinax PDF Compositor - User Guide

## Overview

Pertinax is a minimal PDF page compositor for Linux (Ubuntu LTS) that allows you to organize PDF pages without editing the source files. It's similar to macOS Preview's page management features but focused exclusively on page organization.

## Installation

### From .deb Package

```bash
sudo dpkg -i pertinax_*.deb
sudo apt-get install -f  # Install dependencies if needed
```

### System Requirements

- Ubuntu 22.04 LTS or 24.04 LTS
- GTK 4
- Poppler (for PDF rendering)
- Python 3.10 or newer

## Getting Started

### Launching Pertinax

- **GUI Application**: Search for "Pertinax PDF Compositor" in your application menu, or run `pertinax` from terminal
- **CLI Tool**: Run `pertinax-cli` from terminal for command-line interface

## Basic Operations

### Opening a PDF

1. Click the **Open** button in the header bar (or press `Ctrl+O`)
2. Select a PDF file from the file chooser dialog
3. The PDF pages will appear as thumbnails in the left sidebar

### Importing Pages from Another PDF

1. Click the **Import** button (or press `Ctrl+I`)
2. Select another PDF file
3. All pages from the selected PDF will be appended to your current document

### Viewing Pages

- **Thumbnail Sidebar**: Shows all pages as small previews with page numbers
- **Preview Pane**: Click any thumbnail to view the full-size page on the right
- **Zoom Controls**: Use the zoom dropdown to adjust preview size (Fit, 50%, 100%, 150%, 200%)

### Selecting Pages

- **Single Selection**: Click a thumbnail to select it
- **Multiple Selection**: Hold `Ctrl` and click multiple thumbnails
- **Select All**: Press `Ctrl+A` to select all pages
- **Clear Selection**: Press `Escape` to deselect all pages

### Reordering Pages

Currently, page reordering is done through the CLI tool:

```bash
pertinax-cli
> open file.pdf
> move 0 5  # Move page 0 to position 5
> list      # View current page order
```

### Deleting Pages

1. Select one or more pages in the thumbnail sidebar
2. Click the **Delete** button or press `Delete` key
3. For large deletions (>5 pages), you'll be asked to confirm

**Note**: Deletions only affect your working document, not the source PDF files.

### Exporting the Result

1. Click the **Export** button (or press `Ctrl+S`)
2. Choose a location and filename for the new PDF
3. A new PDF will be created with your page arrangement

**Important**: The original source PDF files are never modified.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF |
| `Ctrl+I` | Import PDF |
| `Ctrl+S` | Export/Save As |
| `Ctrl+A` | Select all pages |
| `Delete` | Delete selected pages |
| `Escape` | Clear selection |
| Arrow keys | Navigate thumbnails |

## Understanding How Pertinax Works

### Page References

Pertinax uses an **immutable page reference** system:

- Opening or importing a PDF creates references like `(file_path, page_index)`
- Your working document is a list of these references
- Operations (delete, reorder) only modify the reference list
- Source PDFs remain completely untouched
- Export creates a brand new PDF from the references

### What Pertinax Does NOT Do

Pertinax is intentionally minimal and does **not** support:

- Text editing
- Annotations or comments
- Form filling
- OCR (text recognition)
- Metadata editing
- PDF encryption/decryption
- Page rotation or cropping
- Cloud synchronization
- Plugins or extensions

If you need these features, consider tools like PDF-Shuffler, PDFtk, or commercial PDF editors.

## Command-Line Interface

The `pertinax-cli` tool provides an interactive command-line interface:

```bash
$ pertinax-cli

Commands:
  open <pdf>      - Open a PDF file
  import <pdf>    - Import pages from another PDF
  list            - Show all pages
  info <index>    - Show details for a specific page
  delete <indices> - Delete pages (e.g., "1,3,5" or "1 3 5")
  move <from> <to> - Move a page to new position
  export <output>  - Save to new PDF file
  help            - Show command help
  quit            - Exit
```

Example session:

```bash
$ pertinax-cli
> open document.pdf
Opened: document.pdf
Pages: 10

> list
Document has 10 pages:
  0: document.pdf [page 1]
  1: document.pdf [page 2]
  ...

> delete 2,5,7
Deleted 3 page(s)
Remaining: 7 pages

> move 0 6
Moved page from index 0 to 6

> export output.pdf
Exported to output.pdf

> quit
```

## Troubleshooting

### Application Won't Launch

- Check that GTK 4 is installed: `apt list --installed | grep gtk-4`
- Verify dependencies: `apt-cache depends pertinax`
- Run from terminal to see error messages: `pertinax`

### PDF Won't Open

- Ensure the PDF is not corrupted (try opening in another viewer)
- Check file permissions: `ls -l yourfile.pdf`
- Some encrypted PDFs may not be supported

### Thumbnails Not Showing

- Verify Poppler is installed: `apt list --installed | grep poppler`
- Try a different PDF file to isolate the issue

### Export Fails

- Ensure you have write permissions to the destination folder
- Check available disk space: `df -h`
- Verify source PDFs are still accessible

## Support and Contributing

- **Bug Reports**: Submit issues on GitHub
- **Feature Requests**: Pertinax is intentionally minimal - complex features may not be added
- **Documentation**: This guide is available at [GitHub repository URL]

## License

Pertinax is released under [LICENSE] - see LICENSE file for details.
