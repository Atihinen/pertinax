#!/usr/bin/env python3
"""
GTK 4 GUI application for Pertinax PDF compositor.
"""

import sys
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gio, GLib, GObject, Gdk  # noqa: E402

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from pertinax import PDFDocument, PDFError  # noqa: E402
from pertinax.renderer import PageRenderer  # noqa: E402

SIDEBAR_WIDTH = 350

class PageItem(GObject.Object):
    """List item representing a page in the document."""
    
    def __init__(self, page_index, page_ref):
        super().__init__()
        self.page_index = page_index
        self.page_ref = page_ref


class PertinaxWindow(Gtk.ApplicationWindow):
    """Main window for Pertinax PDF compositor."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set window properties
        self.set_title("Pertinax PDF Compositor")
        self.set_default_size(1200, 800)
        self.set_resizable(True)
        self.set_deletable(True)
        
        # Initialize document and renderer
        self.document = PDFDocument()
        self.renderer = PageRenderer()
        self.selected_indices = set()
        
        # Track rendering tasks
        self._rendering_tasks = []
        
        # Build UI
        self._build_ui()
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Create event controller for keyboard
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self._on_key_pressed)
        self.add_controller(key_controller)
    
    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press events."""
        from gi.repository import Gdk
        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        
        # Ctrl+O - Open
        if ctrl and keyval == Gdk.keyval_from_name('o'):
            self._on_open_clicked(None)
            return True
        
        # Ctrl+I - Import
        elif ctrl and keyval == Gdk.keyval_from_name('i'):
            if self.import_button.get_sensitive():
                self._on_import_clicked(None)
            return True
        
        # Ctrl+S or Ctrl+E - Export
        elif ctrl and (keyval == Gdk.keyval_from_name('s') or keyval == Gdk.keyval_from_name('e')):
            if self.export_button.get_sensitive():
                self._on_export_clicked(None)
            return True
        
        # Delete or Backspace - Delete pages
        elif keyval == Gdk.keyval_from_name('Delete') or keyval == Gdk.keyval_from_name('BackSpace'):
            if self.delete_button.get_sensitive():
                self._on_delete_clicked(None)
            return True
        
        # Ctrl+A - Select all
        elif ctrl and keyval == Gdk.keyval_from_name('a'):
            if self.document.page_count > 0:
                selection_model = self.thumbnail_view.get_model()
                selection_model.select_all()
            return True
        
        # Escape - Clear selection
        elif keyval == Gdk.keyval_from_name('Escape'):
            if self.document.page_count > 0:
                selection_model = self.thumbnail_view.get_model()
                selection_model.unselect_all()
            return True
        
        return False
        
    def _build_ui(self):
        """Build the main window UI."""
        # Create main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)
        
        # Create header bar (empty - just shows window title and controls)
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)  # Show minimize, maximize, close buttons
        header_bar.set_decoration_layout("menu:minimize,maximize,close")  # Explicitly set button layout
        self.set_titlebar(header_bar)
        
        # Create toolbar below headerbar
        toolbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        toolbar_box.set_spacing(6)
        toolbar_box.set_margin_top(6)
        toolbar_box.set_margin_bottom(6)
        toolbar_box.set_margin_start(6)
        toolbar_box.set_margin_end(6)
        
        # Open button
        self.open_button = Gtk.Button(label="Open")
        self.open_button.set_icon_name("document-open-symbolic")
        self.open_button.set_tooltip_text("Open a PDF file (Ctrl+O)")
        self.open_button.connect("clicked", self._on_open_clicked)
        toolbar_box.append(self.open_button)
        
        # Import button
        self.import_button = Gtk.Button(label="Import")
        self.import_button.set_icon_name("list-add-symbolic")
        self.import_button.set_tooltip_text("Import pages from another PDF (Ctrl+I)")
        self.import_button.connect("clicked", self._on_import_clicked)
        self.import_button.set_sensitive(False)
        toolbar_box.append(self.import_button)
        
        # Export button
        self.export_button = Gtk.Button(label="Export")
        self.export_button.set_icon_name("document-save-as-symbolic")
        self.export_button.set_tooltip_text("Export to new PDF (Ctrl+E / Ctrl+S)")
        self.export_button.connect("clicked", self._on_export_clicked)
        self.export_button.set_sensitive(False)
        self.export_button.add_css_class("suggested-action")
        toolbar_box.append(self.export_button)
        
        # Spacer to push delete button to the right
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        toolbar_box.append(spacer)
        
        # Delete button (on the right side)
        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.set_icon_name("user-trash-symbolic")
        self.delete_button.set_tooltip_text("Delete selected pages (Delete key)")
        self.delete_button.connect("clicked", self._on_delete_clicked)
        self.delete_button.set_sensitive(False)
        toolbar_box.append(self.delete_button)
        
        main_box.append(toolbar_box)
        
        # Visual separator between toolbar and content
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(separator)
        
        # Create horizontal paned layout
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_vexpand(True)
        main_box.append(paned)
        
        # Left side: Thumbnail sidebar
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.set_size_request(350, -1)
        
        sidebar_label = Gtk.Label(label="Pages")
        sidebar_label.set_margin_top(6)
        sidebar_label.set_margin_bottom(6)
        sidebar_box.append(sidebar_label)
        
        # Scrolled window for thumbnails (always visible)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # Create grid view for thumbnails
        self.thumbnail_list_store = Gio.ListStore()
        selection_model = Gtk.MultiSelection.new(self.thumbnail_list_store)
        selection_model.connect('selection-changed', self._on_selection_changed)
        
        self.thumbnail_view = Gtk.GridView(model=selection_model)
        self.thumbnail_view.set_max_columns(1)
        self.thumbnail_view.set_min_columns(1)
        
        # Create factory for rendering thumbnail items
        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self._on_thumbnail_setup)
        factory.connect('bind', self._on_thumbnail_bind)
        self.thumbnail_view.set_factory(factory)
        
        scrolled.set_child(self.thumbnail_view)
        sidebar_box.append(scrolled)
        
        paned.set_start_child(sidebar_box)
        paned.set_position(350)
        
        # Right side: Preview pane with stack for empty state and preview
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Stack for empty state and preview
        self.preview_stack = Gtk.Stack()
        self.preview_stack.set_vexpand(True)
        self.preview_stack.set_hexpand(True)
        
        # Empty state page (shown when no document)
        empty_state = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        empty_state.set_valign(Gtk.Align.CENTER)
        empty_state.set_halign(Gtk.Align.CENTER)
        empty_state.set_spacing(12)
        empty_state.set_margin_top(48)
        empty_state.set_margin_bottom(48)
        
        empty_icon = Gtk.Image.new_from_icon_name("document-open-symbolic")
        empty_icon.set_pixel_size(64)
        empty_icon.set_opacity(0.5)
        empty_state.append(empty_icon)
        
        empty_title = Gtk.Label(label="No Document Open")
        empty_title.add_css_class("title-2")
        empty_state.append(empty_title)
        
        empty_desc = Gtk.Label(label="Open a PDF file to begin composing")
        empty_desc.add_css_class("dim-label")
        empty_state.append(empty_desc)
        
        empty_open_button = Gtk.Button(label="Open PDF")
        empty_open_button.set_halign(Gtk.Align.CENTER)
        empty_open_button.add_css_class("pill")
        empty_open_button.add_css_class("suggested-action")
        empty_open_button.set_margin_top(12)
        empty_open_button.connect("clicked", self._on_open_clicked)
        empty_state.append(empty_open_button)
        
        self.preview_stack.add_named(empty_state, "empty")
        
        # Preview with scrolled window
        preview_scrolled = Gtk.ScrolledWindow()
        preview_scrolled.set_vexpand(True)
        preview_scrolled.set_hexpand(True)
        
        # Preview - use CONTAIN to fit page in viewport without stretching
        self.preview_image = Gtk.Picture()
        self.preview_image.set_content_fit(Gtk.ContentFit.CONTAIN)
        self.preview_image.set_can_shrink(True)
        preview_scrolled.set_child(self.preview_image)
        
        self.preview_stack.add_named(preview_scrolled, "preview")
        
        preview_box.append(self.preview_stack)
        
        paned.set_end_child(preview_box)
        
        # Status bar
        self.status_bar = Gtk.Label(label="No document open")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        self.status_bar.set_halign(Gtk.Align.START)
        self.status_bar.set_margin_start(12)
        main_box.append(self.status_bar)
        
    def _on_open_clicked(self, button):
        """Handle Open button click."""
        dialog = Gtk.FileDialog()
        
        # Create PDF filter
        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("PDF Files")
        pdf_filter.add_mime_type("application/pdf")
        pdf_filter.add_pattern("*.pdf")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(pdf_filter)
        dialog.set_filters(filters)
        
        dialog.open(self, None, self._on_open_response)
    
    def _on_open_response(self, dialog, result):
        """Handle file dialog response for Open."""
        try:
            file = dialog.open_finish(result)
            if file:
                file_path = file.get_path()
                try:
                    self.document.open_pdf(file_path)
                    self._update_ui()
                    self._show_message(f"Opened: {Path(file_path).name}")
                except PDFError as e:
                    self._show_error(f"Failed to open PDF: {e}")
        except GLib.Error:
            pass  # User cancelled
    
    def _on_import_clicked(self, button):
        """Handle Import button click."""
        dialog = Gtk.FileDialog()
        
        # Create PDF filter
        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("PDF Files")
        pdf_filter.add_mime_type("application/pdf")
        pdf_filter.add_pattern("*.pdf")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(pdf_filter)
        dialog.set_filters(filters)
        
        dialog.open(self, None, self._on_import_response)
    
    def _on_import_response(self, dialog, result):
        """Handle file dialog response for Import."""
        try:
            file = dialog.open_finish(result)
            if file:
                file_path = file.get_path()
                try:
                    old_count = self.document.page_count
                    self.document.import_pdf(file_path)
                    new_pages = self.document.page_count - old_count
                    self._update_ui()
                    self._show_message(
                        f"Imported {new_pages} pages from {Path(file_path).name}"
                    )
                except PDFError as e:
                    self._show_error(f"Failed to import PDF: {e}")
        except GLib.Error:
            pass  # User cancelled
    
    def _on_export_clicked(self, button):
        """Handle Export button click."""
        dialog = Gtk.FileDialog()
        dialog.set_initial_name("output.pdf")
        
        # Create PDF filter
        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("PDF Files")
        pdf_filter.add_mime_type("application/pdf")
        pdf_filter.add_pattern("*.pdf")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(pdf_filter)
        dialog.set_filters(filters)
        
        dialog.save(self, None, self._on_export_response)
    
    def _on_export_response(self, dialog, result):
        """Handle file dialog response for Export."""
        try:
            file = dialog.save_finish(result)
            if file:
                file_path = file.get_path()
                try:
                    self.document.export_pdf(file_path)
                    self._show_message(f"Exported to {Path(file_path).name}")
                except PDFError as e:
                    self._show_error(f"Failed to export PDF: {e}")
        except GLib.Error:
            pass  # User cancelled
    
    def _on_delete_clicked(self, button):
        """Handle Delete button click."""
        if not self.selected_indices:
            return
        
        count = len(self.selected_indices)
        
        # Show confirmation for large deletions
        if count > 5:
            dialog = Gtk.AlertDialog()
            dialog.set_message("Confirm Deletion")
            dialog.set_detail(f"Delete {count} pages? This cannot be undone.")
            dialog.set_buttons(["Cancel", "Delete"])
            dialog.set_cancel_button(0)
            dialog.set_default_button(0)
            dialog.choose(self, None, self._on_delete_confirm, None)
        else:
            self._do_delete_pages()
    
    def _on_delete_confirm(self, dialog, result):
        """Handle delete confirmation dialog response."""
        try:
            button = dialog.choose_finish(result)
            if button == 1:  # Delete button
                self._do_delete_pages()
        except GLib.Error:
            pass  # User cancelled
    
    def _do_delete_pages(self):
        """Actually delete the selected pages."""
        if not self.selected_indices:
            return
        
        try:
            indices = sorted(list(self.selected_indices))
            self.document.delete_pages(indices)
            self.renderer.clear_cache()  # Clear cached thumbnails
            self._update_ui()
        except Exception as e:
            self._show_error(f"Failed to delete pages: {e}")
    
    
    def _do_delete_pages(self):
        """Actually delete the selected pages."""
        if not self.selected_indices:
            return
        
        try:
            indices = sorted(list(self.selected_indices))
            self.document.delete_pages(indices)
            self.renderer.clear_cache()  # Clear cached thumbnails
            self._update_ui()
        except Exception as e:
            self._show_error(f"Failed to delete pages: {e}")
    
    def _on_thumbnail_setup(self, factory, list_item):
        """Setup thumbnail list item widget."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        # Use overlay (kept for potential future use)
        overlay = Gtk.Overlay()
        
        picture = Gtk.Picture()
        picture.set_can_shrink(True)
        picture.set_size_request(150, 200)
        overlay.set_child(picture)
        
        # Note: Page number badge is rendered directly on thumbnail by PageRenderer
        # No separate GTK Label needed
        
        box.append(overlay)
        list_item.set_child(box)
        
        # Setup drag source for this item
        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect('prepare', self._on_drag_prepare, list_item)
        drag_source.connect('drag-begin', self._on_drag_begin, list_item)
        box.add_controller(drag_source)
        
        # Setup drop target for reordering
        drop_target = Gtk.DropTarget.new(PageItem, Gdk.DragAction.MOVE)
        drop_target.connect('drop', self._on_drop, list_item)
        box.add_controller(drop_target)
    
    def _on_thumbnail_bind(self, factory, list_item):
        """Bind data to thumbnail list item."""
        page_item = list_item.get_item()
        if not page_item:
            return
        
        page_index = page_item.page_index
        page_ref = page_item.page_ref
        
        box = list_item.get_child()
        overlay = box.get_first_child()
        picture = overlay.get_child()
        
        # Render thumbnail (page number badge is drawn by PageRenderer)
        try:
            pixbuf = self.renderer.render_page_thumbnail(page_ref, 150, 200, page_index + 1)
            from gi.repository import Gdk
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            picture.set_paintable(texture)
        except Exception as e:
            print(f"Error rendering thumbnail: {e}")
    
    def _on_drag_prepare(self, source, x, y, list_item):
        """Prepare drag operation."""
        page_item = list_item.get_item()
        if not page_item:
            return None
        
        # Create drag content with the PageItem
        content = Gdk.ContentProvider.new_for_value(page_item)
        return content
    
    def _on_drag_begin(self, source, drag, list_item):
        """Called when drag begins."""
        # Set drag icon (could use thumbnail here)
        page_item = list_item.get_item()
        if page_item:
            icon = Gtk.WidgetPaintable.new(list_item.get_child())
            source.set_icon(icon, 0, 0)
    
    def _on_drop(self, target, value, x, y, list_item):
        """Handle drop operation to reorder pages."""
        if not isinstance(value, PageItem):
            return False
        
        # Get source and target page indices
        source_page_item = value
        target_page_item = list_item.get_item()
        
        if not target_page_item or source_page_item == target_page_item:
            return False
        
        source_index = source_page_item.page_index
        target_index = target_page_item.page_index
        
        try:
            # Reorder in document
            self.document.reorder_pages(source_index, target_index)
            self.renderer.clear_cache()
            self._update_ui()
            return True
        except Exception as e:
            print(f"Error during drag-drop reorder: {e}")
            return False
    
    def _on_selection_changed(self, selection, position, n_items):
        """Handle thumbnail selection change."""
        # Update selected indices
        self.selected_indices.clear()
        selection_model = self.thumbnail_view.get_model()
        
        for i in range(self.document.page_count):
            if selection_model.is_selected(i):
                self.selected_indices.add(i)
        
        # Update delete button sensitivity
        self.delete_button.set_sensitive(len(self.selected_indices) > 0)
        
        # Update preview if single selection
        if len(self.selected_indices) == 1:
            self._update_preview(next(iter(self.selected_indices)))
    
    def _update_preview(self, page_index):
        """Update preview pane with selected page."""
        if page_index < 0 or page_index >= self.document.page_count:
            return
        
        # Track which page is currently previewed
        self.preview_page_index = page_index
        
        try:
            page_ref = self.document.pages[page_index]
            
            # Render at 2x scale for high quality display
            # CONTAIN mode will fit to viewport without stretching
            scale = 2.0
            
            pixbuf = self.renderer.render_page_preview(page_ref, scale)
            from gi.repository import Gdk
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            self.preview_image.set_paintable(texture)
        except Exception as e:
            print(f"Error rendering preview: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_ui(self):
        """Update UI state based on document."""
        has_pages = self.document.page_count > 0
        
        self.import_button.set_sensitive(has_pages)
        self.export_button.set_sensitive(has_pages)
        
        # Toggle preview stack between empty state and preview
        if has_pages:
            self.preview_stack.set_visible_child_name("preview")
        else:
            self.preview_stack.set_visible_child_name("empty")
        
        # Update status bar
        if has_pages:
            self.status_bar.set_text(
                f"{self.document.page_count} page(s)"
            )
        else:
            self.status_bar.set_text("No document open")
        
        # Update thumbnail view
        self.thumbnail_list_store.remove_all()
        
        if has_pages:
            # Add items first
            for i, page_ref in enumerate(self.document.pages):
                item = PageItem(i, page_ref)
                self.thumbnail_list_store.append(item)
            
            # Render thumbnails asynchronously
            self._render_thumbnails_async()
        
        # Clear selection
        self.selected_indices.clear()
        self.delete_button.set_sensitive(False)
    
    def _show_message(self, message: str):
        """Show an informational message."""
        print(f"Info: {message}")
        # TODO: Could add a toast notification here
    
    def _show_error(self, message: str):
        """Show an error dialog."""
        dialog = Gtk.AlertDialog()
        dialog.set_message("Error")
        dialog.set_detail(message)
        dialog.set_buttons(["OK"])
        dialog.choose(self, None, None, None)
    
    def _render_thumbnails_async(self):
        """Render thumbnails asynchronously to avoid UI blocking."""
        # Cancel any pending rendering tasks
        for task_id in self._rendering_tasks:
            GLib.source_remove(task_id)
        self._rendering_tasks.clear()
        
        # Schedule rendering with idle priority
        for i in range(self.document.page_count):
            task_id = GLib.idle_add(self._render_single_thumbnail, i)
            self._rendering_tasks.append(task_id)
    
    def _render_single_thumbnail(self, index):
        """Render a single thumbnail (called from idle callback)."""
        if index >= self.document.page_count:
            return GLib.SOURCE_REMOVE
        
        # Thumbnail rendering is already cached in the renderer
        # This just ensures it happens progressively
        return GLib.SOURCE_REMOVE


class PertinaxApplication(Gtk.Application):
    """Main application class."""
    
    def __init__(self):
        super().__init__(
            application_id="org.pertinax.PDFCompositor",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
    def do_activate(self):
        """Called when the application is activated."""
        window = self.props.active_window
        if not window:
            window = PertinaxWindow(application=self)
        window.present()


def main():
    """Main entry point."""
    app = PertinaxApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
