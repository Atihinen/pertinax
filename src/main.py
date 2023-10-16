import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Poppler', '0.18')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Poppler, WebKit2

class PDFViewer(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="PDF Viewer")
        self.set_default_size(800, 600)

        # Create a vertical box to hold the UI
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Create a menu bar
        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)

        # Create a "File" menu
        file_menu = Gtk.Menu()
        file_menu_item = Gtk.MenuItem("File")
        file_menu_item.set_submenu(file_menu)
        menubar.append(file_menu_item)

        # Create an "Open" option in the "File" menu
        open_item = Gtk.MenuItem("Open")
        open_item.connect("activate", self.on_open_item_activate)
        file_menu.append(open_item)

        # Create a scrolled window to display the PDF
        self.pdf_view = Gtk.ScrolledWindow()
        self.pdf_view.set_vexpand(True)
        self.pdf_view.set_hexpand(True)
        vbox.pack_start(self.pdf_view, True, True, 0)

        # Create a WebKit2WebView to display the PDF
        self.webview = WebKit2.WebView()
        self.pdf_view.add(self.webview)

    def on_open_item_activate(self, menu_item):
        # Create a FileChooserDialog to choose a PDF file
        file_dialog = Gtk.FileChooserDialog("Open PDF", self,
                                            Gtk.FileChooserAction.OPEN,
                                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        file_filter = Gtk.FileFilter()
        file_filter.set_name("PDF files")
        file_filter.add_mime_type("application/pdf")
        file_dialog.add_filter(file_filter)

        response = file_dialog.run()

        if response == Gtk.ResponseType.OK:
            file_path = file_dialog.get_filename()
            self.load_pdf(file_path)

        file_dialog.destroy()

    def load_pdf(self, file_path):
        try:
            self.webview.load_uri('file://' + file_path)
        except Exception as e:
            print(f"Error loading PDF: {e}")

if __name__ == "__main__":
    window = PDFViewer()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
