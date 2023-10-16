import gi
import math
import cairo 
gi.require_version('Gtk', '3.0')
gi.require_version('Poppler', '0.18')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Poppler, WebKit2, GdkPixbuf

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
        vbox.pack_start(menubar, False, False, 0)

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
        thumbnail_item.connect("toggled", self.on_thumbnail_toggled)  # Connect the signal here
        view_menu.append(thumbnail_item)

        # Create a box to hold the PDF view and thumbnail view
        self.view_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(self.view_box, True, True, 0)

        # Create a scrolled window to display the PDF
        self.pdf_view = Gtk.ScrolledWindow()
        self.pdf_view.set_vexpand(True)
        self.pdf_view.set_hexpand(True)
        self.view_box.pack_start(self.pdf_view, True, True, 0)

        # Create a WebKit2WebView to display the PDF
        self.webview = WebKit2.WebView()
        self.pdf_view.add(self.webview)

        # Create a scrolled window for the thumbnail view
        self.thumbnail_view = Gtk.ScrolledWindow()
        self.thumbnail_view.set_vexpand(True)
        self.thumbnail_view.set_hexpand(False)
        self.view_box.pack_start(self.thumbnail_view, False, False, 0)

        # Create a box to hold the thumbnails
        self.thumbnail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.thumbnail_view.add(self.thumbnail_box)

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
        self.update_view()

    def update_view(self):
        if self.thumbnail_mode:
            self.pdf_view.hide()
            self.thumbnail_view.show()
            self.show_thumbnail_view()
        else:
            self.thumbnail_view.hide()
            self.pdf_view.show()

    def create_thumbnail(self, page_num):
        # Get the page at the specified page number
        page = self.pdf_document.get_page(page_num)
        if page is not None:
            # Get the page size (assuming a standard page size of 100x100)
            thumbnail_size = 100
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
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                data, GdkPixbuf.Colorspace.RGB, False, 8, width, height, width * 4
            )

            # Create an image widget to display the thumbnail
            thumbnail = Gtk.Image.new_from_pixbuf(pixbuf)
            return thumbnail
        else:
            return None

    def show_thumbnail_view(self):
        print("Showing thumbnail view")
        print("Number of thumbnails added:", len(self.thumbnail_box.get_children()))

        # Remove any existing thumbnails
        for widget in self.thumbnail_box.get_children():
            self.thumbnail_box.remove(widget)

        # Create thumbnails for each page and add them to the thumbnail box
        if self.pdf_document is not None:
            num_pages = self.pdf_document.get_n_pages()
            print("Number of pages:", num_pages)
            for page_num in range(num_pages):
                thumbnail = self.create_thumbnail(page_num)
                self.thumbnail_box.add(thumbnail)
                thumbnail.show()  # Ensure the thumbnail is visible
        else:
            print("No PDF document loaded")

        self.thumbnail_box.show_all()  # Show all thumbnails in the box

    def load_pdf(self, pdf_path):
        # Load the specified PDF file into the WebView
        self.webview.load_uri("file://" + pdf_path)

        # Load the PDF document using Poppler
        self.pdf_document = Poppler.Document.new_from_file("file://" + pdf_path)

if __name__ == "__main__":
    window = PDFViewer()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
