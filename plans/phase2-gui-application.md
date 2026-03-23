# Phase 2: GTK 4 GUI Application

## Goal

Build a graphical user interface using GTK 4 and PyGObject that provides visual PDF page composition capabilities. This GUI wraps the Phase 1 module with thumbnail sidebar, preview pane, and drag-drop interactions.

## Prerequisites

- Phase 1 module complete and tested
- `pertinax.PDFDocument` API working
- CLI tool validates core operations

## Tasks

### 1. Create Rendering Module

- Create `src/pertinax/renderer.py`
- Integrate Poppler-GObject bindings: `gi.repository.Poppler`
- Implement `render_page_thumbnail(page_reference, width, height)`:
  - Opens PDF with Poppler
  - Renders specified page to Cairo surface
  - Returns GdkPixbuf for GTK display
- Implement `render_page_preview(page_reference, scale)` for full view
- Add thumbnail cache to avoid re-rendering

**Deliverable:** Page rendering functions using Poppler

### 2. Design Application Architecture

- Create `src/pertinax_gui.py` as main entry point
- Define `PertinaxWindow(Gtk.ApplicationWindow)` main window class
- Define `PertinaxApplication(Gtk.Application)` for lifecycle
- Wire up to Phase 1 `PDFDocument` model
- Use Model-View pattern: `PDFDocument` is model, GTK widgets are views

**Deliverable:** GTK application scaffold

### 3. Build Main Window Layout

- Create `PertinaxWindow` with `GtkBox` horizontal layout:
  - Left: Thumbnail sidebar (300-400px fixed width)
  - Right: Preview pane (fills remaining space)
- Add header bar with:
  - Open button
  - Import button  
  - Export/Save As button
  - Delete button (sensitive only when selection exists)
- Add status bar showing page count

**Deliverable:** Main window layout structure

### 4. Implement Thumbnail Sidebar

- Use `GtkListView` or `GtkGridView` for thumbnail list
- Create custom list model backed by `PDFDocument.pages`
- For each page reference:
  - Render thumbnail using Phase 2.1 renderer
  - Display as `GtkImage` or `GtkPicture`
  - Show page number overlay
- Enable multi-selection mode
- Set up selection tracking

**Deliverable:** Thumbnail sidebar displaying all pages

### 5. Implement Preview Pane

- Use `GtkScrolledWindow` containing `GtkDrawingArea`
- Listen to sidebar selection changes
- When page selected:
  - Render full-resolution preview using Phase 2.1 renderer
  - Display centered in drawing area
  - Add zoom controls (optional: 50%, 100%, 150%, Fit)
- Handle empty document state (show placeholder)

**Deliverable:** Full-page preview synchronized with selection

### 6. Add File Operations UI

- **Open PDF:**
  - `GtkFileChooserDialog` with PDF filter
  - Call `document.open_pdf(path)` from Phase 1
  - Refresh thumbnail sidebar
- **Import PDF:**
  - `GtkFileChooserDialog` with PDF filter
  - Call `document.import_pdf(path)` from Phase 1
  - Update thumbnail sidebar (append new pages)
- **Export/Save As:**
  - `GtkFileChooserDialog` in save mode
  - Call `document.export_pdf(path)` from Phase 1
  - Show progress spinner during export
  - Display success notification

**Deliverable:** File menu operations working

### 7. Implement Drag-and-Drop Reordering

- Add drag source to thumbnail list items
- Add drop target to thumbnail list
- On drop:
  - Calculate new position from drop coordinates
  - Call `document.reorder_pages()` or `document.move_pages()`
  - Update thumbnail list model
- Visual feedback: drag preview, drop indicator line
- Constraint: Only within same window (no cross-window DnD)

**Deliverable:** Drag-drop page reordering

### 8. Implement Page Deletion

- Listen to Delete key press or Delete button click
- Get selected page indices from thumbnail list
- Call `document.delete_pages(indices)` from Phase 1
- Update thumbnail list model
- Update selection state after deletion
- Show confirmation dialog for large selections (>5 pages)

**Deliverable:** Multi-page deletion

### 9. Add Keyboard Shortcuts

- `Ctrl+O` - Open PDF
- `Ctrl+I` - Import PDF
- `Ctrl+S` / `Ctrl+Shift+S` - Export PDF
- `Delete` - Delete selected pages
- `Ctrl+A` - Select all pages
- Arrow keys - Navigate thumbnails
- `Esc` - Clear selection

**Deliverable:** Keyboard navigation

### 10. Implement Reactive UI Updates

- Connect `PDFDocument` changes to GTK signals
- When document changes:
  - Update thumbnail list (add/remove/reorder)
  - Update preview if needed
  - Update status bar page count
  - Enable/disable buttons based on state
- Add "modified" indicator in title bar

**Deliverable:** Reactive UI synchronized with model

### 11. Add Error Handling UI

- Catch exceptions from Phase 1 module
- Display `GtkMessageDialog` for errors:
  - File not found
  - Invalid PDF
  - Export failures
- Add logging to stderr
- Graceful degradation (continue running after error)

**Deliverable:** User-friendly error messages

### 12. Polish UI/UX

- Add application icon
- Improve thumbnail rendering quality
- Add loading indicators for slow operations
- Add empty state messaging ("No PDF open")
- Improve spacing and padding
- Add tooltips to buttons
- Test with various PDF sizes

**Deliverable:** Polished user experience

### 13. Create Desktop Integration

- Create `pertinax.desktop` file:
  - Name: "Pertinax PDF Compositor"
  - Categories: Office, Viewer
  - MIME types: application/pdf
- Add application icon in standard sizes
- Set up to appear in application menu

**Deliverable:** Desktop file for launcher integration

### 14. Build Debian Package

- Create `debian/` directory structure:
  - `debian/control` - Dependencies and package metadata
  - `debian/rules` - Build instructions
  - `debian/install` - File installation rules
  - `debian/copyright` - License information
  - `debian/changelog` - Version history
- Specify APT dependencies:
  - `python3` (>= 3.10)
  - `python3-gi`
  - `gir1.2-gtk-4.0` (or fallback to `gir1.2-gtk-3.0`)
  - `gir1.2-poppler-0.18`
  - `python3-pypdf` (or `python3-pypdf2`)
- Install both CLI and GUI entry points:
  - `/usr/bin/pertinax` - GUI launcher
  - `/usr/bin/pertinax-cli` - CLI tool
- Package module under `/usr/lib/python3/dist-packages/pertinax/`

**Deliverable:** Working `.deb` package

### 15. Test on Ubuntu LTS

- Install `.deb` on clean Ubuntu LTS system
- Verify all dependencies install correctly
- Test application launch from menu
- Test all operations with real PDFs
- Verify source PDFs remain unmodified
- Test with large PDFs (100+ pages)

**Deliverable:** Validated package on target platform

## Success Criteria

- [ ] GUI launches and shows empty document state
- [ ] Can open PDF and see thumbnails
- [ ] Can import additional PDFs
- [ ] Thumbnails accurately represent pages
- [ ] Preview pane shows selected page clearly
- [ ] Can drag-drop reorder pages smoothly
- [ ] Can multi-select and delete pages
- [ ] Can export new PDF successfully
- [ ] Keyboard shortcuts work
- [ ] No crashes or hangs with typical PDFs
- [ ] `.deb` package installs and runs on Ubuntu LTS

## Dependencies

- `python3-gi` - PyGObject bindings
- `gir1.2-gtk-4.0` - GTK 4 (or `gir1.2-gtk-3.0` as fallback)
- `gir1.2-poppler-0.18` - Poppler GObject bindings
- Phase 1 module dependencies

## Output

A complete GTK 4 application packaged as `.deb` that provides visual PDF page composition on Ubuntu LTS, using the Phase 1 module for all PDF operations.
