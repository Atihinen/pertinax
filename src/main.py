import gi
import math
import cairo
gi.require_version('Gtk', '3.0')
gi.require_version('Poppler', '0.18')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Poppler, WebKit2, GdkPixbuf, Gdk

class PDFViewer(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="PDF Viewer")
        self.set_default_size(800, 600)

        self.thumbnail_mode = False  # Flag to track thumbnail view mode
        self.pdf_document = None  # Poppler PDF document object
        self.thumbnail_pixbufs = []  # List to store thumbnail pixbufs

        # Create a vertical box to hold the UI
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Create a menu bar
        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)  # Position at the top

        # Create a horizontal box to hold the PDF view and thumbnail view
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(hbox, True, True, 0)

        # Create a scrolled window to display the PDF
        self.pdf_view = Gtk.ScrolledWindow()
        self.pdf_view.set_vexpand(True)
        self.pdf_view.set_hexpand(True)
        hbox.pack_end(self.pdf_view, True, True, 0)

        # Create a WebKit2WebView to display the PDF
        self.webview = WebKit2.WebView()
        self.pdf_view.add(self.webview)

        # Create a scrolled window for the thumbnail view
        self.thumbnail_view = Gtk.ScrolledWindow()
        self.thumbnail_view.set_vexpand(True)
        self.thumbnail_view.set_hexpand(False)
        self.thumbnail_view.set_min_content_width(200)
        hbox.pack_start(self.thumbnail_view, False, False, 0)

        # Create a box to hold the thumbnails
        self.thumbnail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.thumbnail_view.add(self.thumbnail_box)

        # Create a "File" menu
        file_menu = Gtk.Menu()
        file_menu_item = Gtk.MenuItem(label="File")
        file_menu_item.set_submenu(file_menu)
        menubar.append(file_menu_item)

        # Create an "Open" option in the "File" menu
        open_item = Gtk.MenuItem(label="Open")
        open_item.connect("activate", self.on_open_item_activate)
        file_menu.append(open_item)

        # Create a "View" menu
        view_menu = Gtk.Menu()
        view_menu_item = Gtk.MenuItem(label="View")
        view_menu_item.set_submenu(view_menu)
        menubar.append(view_menu_item)

        # Create a "Thumbnail" option in the "View" menu
        thumbnail_item = Gtk.CheckMenuItem(label="Thumbnail")
        thumbnail_item.connect("toggled", self.on_thumbnail_toggled)
        view_menu.append(thumbnail_item)

    def on_open_item_activate(self, menu_item):
        dialog = Gtk.FileChooserDialog(
            "Open PDF File", None,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_default_response(Gtk.ResponseType.OK)

        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF Files")
        filter_pdf.add_mime_type("application/pdf")
        dialog.add_filter(filter_pdf)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.load_pdf(filename)
        
        dialog.destroy()

    def on_thumbnail_toggled(self, menu_item):
        print("Thumbnail toggled")
        self.thumbnail_mode = menu_item.get_active()
        self.show_thumbnail_view()  # Call show_thumbnail_view when toggling the thumbnail mode

    def create_thumbnail(self, page_num):
        # Get the page at the specified page number
        page = self.pdf_document.get_page(page_num)
        if page is not None:
            # Get the page size (assuming a standard page size of 100x100)
            thumbnail_size = 200
            page_rect = page.get_size()
            aspect_ratio = page_rect[0] / page_rect[1]
            width = thumbnail_size
            height = int(thumbnail_size / aspect_ratio)

            # Render the page to a pixbuf using Cairo
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(surface)
            cr.set_source_rgb(1.0, 1.0, 1.0)  # White background
            cr.paint()
            cr.scale(width / page_rect[0], height / page_rect[1])
            page.render(cr)
            cr.stroke()
            cr.show_page()

            # Convert the surface to a pixbuf
            data = surface.get_data()
            stride = surface.get_stride()
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                data, GdkPixbuf.Colorspace.RGB, False, 8, width, height, stride
            )

            # Create an image widget to display the thumbnail
            thumbnail = Gtk.Image.new_from_pixbuf(pixbuf)

            # Create an event box to wrap the thumbnail image and handle events
            event_box = Gtk.EventBox()
            event_box.add(thumbnail)

            # Connect a callback to handle thumbnail clicks
            event_box.connect("button-press-event", self.on_thumbnail_clicked, page_num)

            # Create a label to display the page number
            page_number_label = Gtk.Label(label=str(page_num + 1))  # Page numbers start from 1
            page_number_label.set_valign(Gtk.Align.START)
            page_number_label.set_margin_top(10)  # Adjust the top margin as needed
            page_number_label.set_margin_left(10)

            # Pack the thumbnail and page number label into the thumbnail box
            thumbnail_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            thumbnail_box.pack_start(page_number_label, False, False, 0)
            thumbnail_box.pack_end(event_box, False, False, 0)

            return thumbnail_box
        else:
            return None

    def on_thumbnail_clicked(self, widget, event, page_num):
        print("Clicked thumbnail", page_num)  # Change this line

        # Handle thumbnail click event
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            # Left mouse button (BUTTON1) click
            print(f"Thumbnail clicked! Page number: {page_num + 1}")

            # Load the specified page in the PDF
            self.load_pdf_page(page_num)

    def show_thumbnail_view(self):
        print("Showing thumbnail view")
        print("Number of thumbnails added:", len(self.thumbnail_box.get_children()))

        # Remove any existing thumbnails
        for widget in self.thumbnail_box.get_children():
            self.thumbnail_box.remove(widget)

        # Hide or show the PDF view based on the thumbnail mode
        if self.thumbnail_mode:
            self.pdf_view.hide()
            self.thumbnail_view.show()
            # Set a light gray background color for the thumbnail view
            rgba = Gdk.RGBA()
            rgba.parse("rgb(220, 220, 220)")
            self.thumbnail_view.override_background_color(Gtk.StateFlags.NORMAL, rgba)
        else:
            self.pdf_view.show()
            self.thumbnail_view.hide()

        # Create thumbnails for each page and add them to the thumbnail box
        if self.pdf_document is not None:
            num_pages = self.pdf_document.get_n_pages()
            print("Number of pages:", num_pages)
            for page_num in range(num_pages):
                thumbnail_box = self.create_thumbnail(page_num)
                thumbnail_box.set_margin_bottom(10)
                # Connect the thumbnail click event handler
                thumbnail_box.connect("button-press-event", self.on_thumbnail_clicked, page_num)
                self.thumbnail_box.add(thumbnail_box)
                thumbnail_box.show_all()  # Ensure the thumbnail and page number are visible
        else:
            print("No PDF document loaded")

        self.thumbnail_box.show_all()  # Show all thumbnails in the box

        # Ensure the PDF view is always visible
        self.pdf_view.show()

    def load_pdf(self, pdf_path):
        # Store the PDF path
        self.pdf_path = pdf_path

        # Load the specified PDF file into the WebView
        self.webview.load_uri(f"file://{pdf_path}")

        # Load the PDF document using Poppler
        self.pdf_document = Poppler.Document.new_from_file(f"file://{pdf_path}")

    def load_pdf_page(self, page_num):
        if self.pdf_document is not None and page_num >= 0 and page_num < self.pdf_document.get_n_pages():
            # Load the specified page in the PDF
            self.scroll_pdf_page(page_num)

    def scroll_pdf_page(self, page_num):
        if self.pdf_document is not None and page_num >= 0 and page_num < self.pdf_document.get_n_pages():
            # Scroll to the specified page using JavaScript
            self.webview.run_javascript(f"pdfViewer.currentPageNumber = {page_num};", None, None, None)

            print(f"Scrolling to PDF page {page_num + 1}")





if __name__ == "__main__":
    window = PDFViewer()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
