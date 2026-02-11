# UI Improvement Directives — Pertinax PDF Compositor

## 1. Structural Architecture (The Two-Pane Layout)
The current grid-only view is inefficient for page management. Move to a classic "Sidebar + Main Preview" structure using `Gtk.Paned`.

* **Left Pane (The Composer):** A narrow, vertically scrollable column of thumbnails. This is the **primary interaction zone** for reordering (DND) and deleting pages.
* **Right Pane (The Viewer):** A large, high-fidelity preview area for the currently selected page.
* **Logical Benefit:** Reordering in a single vertical column is more intuitive than a wrapping grid for establishing document flow.

## 2. HeaderBar & Toolbar Optimization
Clean up the redundant secondary toolbar to reclaim vertical real estate.

* **Consolidate Titles:** Remove the duplicate "Pertinax PDF Compositor" label from the inner window.
* **Primary Actions (Left):** Place "Open" and "Import (+)" buttons together.
* **Secondary Actions (Right):** Place the "Delete" (Trash) icon here. It should only be sensitive (`set_sensitive(True)`) when a thumbnail is selected.
* **Final Action:** Style the "Export" button with the `.suggested-action` CSS class (Ubuntu blue) to highlight the end goal.

## 3. Sidebar Thumbnail Design
* **Selection State:** Use standard GTK selection styling (blue outline/background) so users know exactly which page they are viewing in the right pane.
* **Page Labels:** Move "Page X" text from under the image to a small, semi-transparent overlay badge on the top-left of the thumbnail to save vertical space.
* **Multi-Selection:** Enable `Gtk.SelectionModel` to allow `Ctrl+Click` for batch deletions.

## 4. Performance & Rendering Directives
To ensure the GTK 4 interface remains responsive during PDF processing:

* **Asynchronous Rendering:** Use background threads or `GLib.idle_add` to render Poppler surfaces. The UI must not "stutter" when a 100-page PDF is imported.
* **Thumbnail Caching:** Cache the low-resolution Cairo surfaces for the sidebar to ensure scrolling is smooth.
* **Empty State:** Implement a `Gtk.StatusPage` with a "Welcome" icon and an "Open PDF" button to be displayed when no document is loaded.

## 5. Keyboard Shortcuts
Map the following for a native feel:
* `Delete` / `Backspace`: Remove selected page reference.
* `Ctrl + O`: Open PDF.
* `Ctrl + I`: Import PDF.
* `Ctrl + E`: Export PDF.