# Mission — Linux PDF Page Composer (Preview-like)

## Overview

Build a **minimal PDF page compositor for Linux (Ubuntu LTS)** similar to macOS Preview’s page management — focused **only on page organization**, not PDF editing.

The application allows users to:

- Open a PDF
- Import additional PDFs into the current working document
- Reorder and delete pages
- Preview pages
- Export a new PDF

The application **never modifies source PDFs**.

---

## Core Philosophy

This is **not** a PDF editor.

It is a:

> Page compositor using immutable page references.

Key principles:

- PDFs are treated as read-only sources
- Editing occurs only in an in-memory working document
- Export produces a brand new PDF
- No modification of original files
- Minimal UX
- Minimal architecture
- Debian-native implementation

---

## Required Features

### File Operations

#### Open PDF
- Opens a PDF into a new working document
- Expands pages into internal page references

#### Import PDF
- Appends pages from another PDF into the current working document
- No merging of PDF binaries
- Only adds page references

#### Export / Save As
- Creates a new PDF from the working document
- Only time a file is written

---

### Page Management

- Thumbnail sidebar
- Full page preview
- Drag & drop reordering **within the window only**
- Delete pages
- Multi-page selection (recommended)

---

## Explicit Non-Goals

The following features must **not** be implemented:

- Text editing
- Annotations
- Forms
- OCR
- Metadata editing
- Cloud sync
- Plugins
- Source PDF modification
- Cross-window drag & drop
- Drag & drop between application instances
- Embedded PDF editing

---

## Edit Semantics

Opening or importing PDFs:

- Create immutable page references:
  - `(file_path, page_index)`
- Working document is an in-memory list of page references
- Page operations manipulate references only

Export:

- Constructs a new PDF using referenced pages
- Source files remain untouched

---

## Technical Stack (Fixed)

### Language & UI

- Python 3 (system Python only)
- GTK 4 via PyGObject

### PDF Handling

Rendering:
- Poppler (GObject bindings)
- Read-only usage

Export:
- pikepdf (QPDF backend)

---

## Platform Constraints

Target:

- Ubuntu LTS

Packaging:

- Native `.deb` package only

Forbidden:

- Flatpak
- Snap
- AppImage

---

## Python Dependency Policy (Strict)

Allowed:

- APT-installed Python packages only

Forbidden:

- pip
- pipx
- virtualenv
- vendored wheels
- runtime downloads
- build-time network access

Interpreter:

