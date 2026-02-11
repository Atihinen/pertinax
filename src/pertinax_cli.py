#!/usr/bin/env python3
"""
Command-line interface for testing the Pertinax PDF module.
"""

import sys
import argparse
from pathlib import Path

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from pertinax import PDFDocument, PDFError, PageNotFoundError


class PertinaxCLI:
    """Interactive CLI for PDF page composition."""
    
    def __init__(self):
        self.doc = PDFDocument()
        self.current_file = None
    
    def cmd_open(self, args):
        """Open a PDF file."""
        if len(args) < 1:
            print("Error: open requires a file path")
            return
        
        file_path = args[0]
        try:
            self.doc.open_pdf(file_path)
            self.current_file = file_path
            print(f"Opened: {file_path}")
            print(f"Pages: {self.doc.page_count}")
        except PDFError as e:
            print(f"Error: {e}")
    
    def cmd_import(self, args):
        """Import pages from another PDF."""
        if len(args) < 1:
            print("Error: import requires a file path")
            return
        
        file_path = args[0]
        try:
            old_count = self.doc.page_count
            self.doc.import_pdf(file_path)
            new_pages = self.doc.page_count - old_count
            print(f"Imported: {file_path}")
            print(f"Added {new_pages} pages (total: {self.doc.page_count})")
        except PDFError as e:
            print(f"Error: {e}")
    
    def cmd_list(self, args):
        """List all pages in the working document."""
        if self.doc.page_count == 0:
            print("Document is empty")
            return
        
        print(f"Document has {self.doc.page_count} pages:")
        for i, page_ref in enumerate(self.doc.pages):
            file_name = Path(page_ref.file_path).name
            print(f"  {i}: {file_name} [page {page_ref.page_index + 1}]")
    
    def cmd_info(self, args):
        """Show detailed info for a specific page."""
        if len(args) < 1:
            print("Error: info requires a page index")
            return
        
        try:
            index = int(args[0])
            info = self.doc.get_page_info(index)
            print(f"Page {index}:")
            print(f"  Source: {Path(info['source_file']).name}")
            print(f"  Original page: {info['source_page']}")
            print(f"  Size: {info['width']:.1f} x {info['height']:.1f} points")
            print(f"  Rotation: {info['rotation']}°")
        except (ValueError, PageNotFoundError) as e:
            print(f"Error: {e}")
    
    def cmd_delete(self, args):
        """Delete pages by index (comma-separated or space-separated)."""
        if len(args) < 1:
            print("Error: delete requires page indices")
            return
        
        try:
            # Parse indices (support both "1,3,5" and "1 3 5")
            indices_str = ' '.join(args)
            indices = []
            for part in indices_str.replace(',', ' ').split():
                indices.append(int(part))
            
            self.doc.delete_pages(indices)
            print(f"Deleted {len(indices)} page(s)")
            print(f"Remaining: {self.doc.page_count} pages")
        except (ValueError, PageNotFoundError) as e:
            print(f"Error: {e}")
    
    def cmd_move(self, args):
        """Move a page from one index to another."""
        if len(args) < 2:
            print("Error: move requires <from_index> <to_index>")
            return
        
        try:
            old_index = int(args[0])
            new_index = int(args[1])
            self.doc.reorder_pages(old_index, new_index)
            print(f"Moved page {old_index} to position {new_index}")
        except (ValueError, PageNotFoundError) as e:
            print(f"Error: {e}")
    
    def cmd_export(self, args):
        """Export the working document to a new PDF."""
        if len(args) < 1:
            print("Error: export requires an output file path")
            return
        
        output_path = args[0]
        try:
            self.doc.export_pdf(output_path)
            print(f"Exported to: {output_path}")
        except PDFError as e:
            print(f"Error: {e}")
    
    def cmd_help(self, args):
        """Show available commands."""
        print("Available commands:")
        print("  open <file>           - Open a PDF file")
        print("  import <file>         - Import pages from another PDF")
        print("  list                  - List all pages")
        print("  info <index>          - Show page details")
        print("  delete <indices>      - Delete pages (e.g., '1,3,5' or '1 3 5')")
        print("  move <from> <to>      - Move page to new position")
        print("  export <file>         - Save to new PDF")
        print("  help                  - Show this help")
        print("  quit                  - Exit")
    
    def cmd_quit(self, args):
        """Exit the CLI."""
        print("Goodbye!")
        sys.exit(0)
    
    def run_command(self, line: str):
        """Parse and execute a command."""
        parts = line.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        commands = {
            'open': self.cmd_open,
            'import': self.cmd_import,
            'list': self.cmd_list,
            'info': self.cmd_info,
            'delete': self.cmd_delete,
            'move': self.cmd_move,
            'export': self.cmd_export,
            'help': self.cmd_help,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }
        
        if cmd in commands:
            commands[cmd](args)
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")
    
    def interactive(self):
        """Run in interactive mode."""
        print("Pertinax PDF Compositor CLI")
        print("Type 'help' for available commands")
        print()
        
        while True:
            try:
                line = input("pertinax> ")
                self.run_command(line)
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Pertinax PDF Compositor - CLI tool for testing'
    )
    parser.add_argument(
        'command',
        nargs='*',
        help='Command to execute (or omit for interactive mode)'
    )
    
    args = parser.parse_args()
    cli = PertinaxCLI()
    
    if args.command:
        # Execute single command and exit
        cli.run_command(' '.join(args.command))
    else:
        # Run in interactive mode
        cli.interactive()


if __name__ == '__main__':
    main()
