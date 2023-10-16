import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, WebKit2

class PDFViewer(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="PDF Viewer")
        self.set_default_size(800, 600)

        self.pdf_view = Gtk.ScrolledWindow()
        self.add(self.pdf_view)

        self.webview = WebKit2.WebView()
        self.pdf_view.add(self.webview)

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
