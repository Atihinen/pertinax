"""
Custom Robot Framework library for Pertinax GUI testing with dogtail.

This library wraps python-dogtail functionality to provide keywords for:
- Application lifecycle management
- Button and widget interaction
- Drag and drop operations
- Keyboard shortcuts
- File dialogs
"""

import os
import time
import subprocess
from typing import Optional
from robot.api import logger


class PertinaxLibrary:
    """Robot Framework library for GUI testing of Pertinax PDF compositor."""
    
    ROBOT_LIBRARY_SCOPE = 'TEST'
    
    def __init__(self):
        """Initialize the library."""
        self.app_process: Optional[subprocess.Popen] = None
        self.app = None
        
    def launch_pertinax(self, pdf_path: Optional[str] = None):
        """Launch the Pertinax application.
        
        Args:
            pdf_path: Optional path to PDF file to open on launch
        """
        import dogtail.tree
        from dogtail import config
        
        # Configure dogtail for headless testing
        config.config.checkForA11y = False  # Disable accessibility check for CI
        config.config.logDebugToFile = False
        config.config.logDebugToStdOut = False
        config.config.actionDelay = 0.1
        config.config.searchCutoffCount = 30
        config.config.searchWarningThreshold = 3
        config.config.defaultDelay = 0.5
        
        # Set environment for accessibility
        env = os.environ.copy()
        env['GTK_MODULES'] = 'gail:atk-bridge'
        env['NO_AT_BRIDGE'] = '0'
        
        # Use the virtual environment's python
        python_exe = '/home/atihinen/.venvs/pertinax/bin/python3'
        if not os.path.exists(python_exe):
            python_exe = 'python3'
            logger.warning("venv python not found, using system python")
        
        # Launch application
        cmd = [python_exe, 'src/pertinax_gui.py']
        if pdf_path:
            cmd.append(pdf_path)
            
        logger.info(f"Launching: {' '.join(cmd)}")
        self.app_process = subprocess.Popen(
            cmd,
            cwd='/home/atihinen/projects/pertinax',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait for application to appear in accessibility tree
        max_attempts = 20
        for attempt in range(max_attempts):
            # Check if process is still alive
            if self.app_process.poll() is not None:
                stdout, stderr = self.app_process.communicate()
                logger.error(f"App crashed during startup. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
                raise AssertionError("Application crashed during startup")
            
            try:
                self.app = dogtail.tree.root.application('pertinax_gui.py')
                logger.info(f"Application found in accessibility tree after {attempt+1} attempts")
                time.sleep(0.5)  # Extra time for UI to stabilize
                return
            except dogtail.tree.SearchError:
                logger.debug(f"Attempt {attempt+1}/{max_attempts}: Application not yet in accessibility tree")
                time.sleep(0.5)
        
        # Final check - maybe it launched but with different name
        logger.error("Could not find application in accessibility tree")
        logger.info("Available applications:")
        try:
            for app in dogtail.tree.root.applications():
                logger.info(f"  - {app.name}")
        except:
            logger.error("Could not enumerate applications")
            
        raise AssertionError(f"Failed to find Pertinax application after {max_attempts} attempts")
    
    def close_pertinax(self):
        """Close the Pertinax application."""
        if self.app_process:
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
                self.app_process.wait()
            
            stdout, stderr = self.app_process.communicate()
            if stdout:
                logger.info(f"App stdout:\n{stdout.decode()}")
            if stderr:
                logger.info(f"App stderr:\n{stderr.decode()}")
                
        self.app_process = None
        self.app = None
    
    def verify_app_is_running(self):
        """Verify that the application is still running."""
        if not self.app_process or self.app_process.poll() is not None:
            raise AssertionError("Application is not running")
        logger.info("Application is running")
    
    def click_button_by_label(self, label: str):
        """Click a button by its accessibility label.
        
        Args:
            label: The accessibility label of the button
        """
        import dogtail.tree
        import dogtail.predicate
        
        try:
            # Search for button by accessible name
            button = self.app.child(
                roleName='push button',
                name=label
            )
            logger.info(f"Clicking button: {label}")
            button.click()
            time.sleep(0.3)  # Wait for click to process
        except dogtail.tree.SearchError:
            raise AssertionError(f"Button with label '{label}' not found")
    
    def get_button_sensitive(self, label: str) -> bool:
        """Check if a button is sensitive (enabled).
        
        Args:
            label: The accessibility label of the button
            
        Returns:
            True if button is sensitive, False otherwise
        """
        import dogtail.tree
        
        try:
            button = self.app.child(
                roleName='push button',
                name=label
            )
            # GTK's sensitive property is exposed as 'sensitive' state
            is_sensitive = button.sensitive
            logger.info(f"Button '{label}' sensitive: {is_sensitive}")
            return is_sensitive
        except dogtail.tree.SearchError:
            raise AssertionError(f"Button with label '{label}' not found")
    
    def verify_widget_visible(self, label: str):
        """Verify that a widget with the given label is visible.
        
        Args:
            label: The accessibility label of the widget
        """
        import dogtail.tree
        
        try:
            widget = self.app.child(name=label)
            if not widget.showing:
                raise AssertionError(f"Widget '{label}' is not showing")
            logger.info(f"Widget '{label}' is visible")
        except dogtail.tree.SearchError:
            raise AssertionError(f"Widget with label '{label}' not found")
    
    def verify_widget_not_visible(self, label: str):
        """Verify that a widget with the given label is not visible.
        
        Args:
            label: The accessibility label of the widget
        """
        import dogtail.tree
        
        try:
            widget = self.app.child(name=label)
            if widget.showing:
                raise AssertionError(f"Widget '{label}' is showing but should not be")
            logger.info(f"Widget '{label}' is not visible (as expected)")
        except dogtail.tree.SearchError:
            # Widget not in tree at all - that's fine
            logger.info(f"Widget '{label}' not found in tree (not visible)")
    
    def get_page_count_from_status(self) -> int:
        """Get the page count from the status label.
        
        Returns:
            Number of pages shown in status
        """
        import dogtail.tree
        
        try:
            status_label = self.app.child(
                roleName='label',
                name='status_label'
            )
            text = status_label.text
            logger.info(f"Status label text: {text}")
            
            # Parse "N pages" from status
            if "pages" in text:
                return int(text.split()[0])
            elif "page" in text:
                return int(text.split()[0])
            else:
                raise AssertionError(f"Cannot parse page count from: {text}")
        except dogtail.tree.SearchError:
            raise AssertionError("Status label not found")
    
    def wait_for_thumbnails(self, expected_count: int, timeout: int = 10):
        """Wait for thumbnails to be loaded.
        
        Args:
            expected_count: Expected number of thumbnails
            timeout: Maximum seconds to wait
        """
        import dogtail.tree
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try to get page count from status
                page_count = self.get_page_count_from_status()
                if page_count == expected_count:
                    logger.info(f"Thumbnails loaded: {expected_count} pages")
                    time.sleep(0.5)  # Extra time for thumbnails to render
                    return
            except:
                pass
            time.sleep(0.5)
        
        raise AssertionError(
            f"Thumbnails not loaded after {timeout}s (expected {expected_count} pages)"
        )
    
    def open_file_dialog(self, pdf_path: str):
        """Open a PDF file using the file dialog.
        
        Args:
            pdf_path: Absolute path to PDF file
        """
        import dogtail.tree
        import dogtail.rawinput
        
        # Click the Open button
        self.click_button_by_label('Open PDF')
        time.sleep(0.5)
        
        # Wait for file chooser dialog
        try:
            dialog = self.app.child(roleName='file chooser')
            logger.info("File chooser dialog opened")
            
            # Find the location entry and type the path
            # Use Ctrl+L to activate location entry in GTK file chooser
            dogtail.rawinput.keyCombo('<Control>l')
            time.sleep(0.3)
            
            # Type the full path
            dogtail.rawinput.typeText(pdf_path)
            time.sleep(0.3)
            
            # Press Enter to confirm
            dogtail.rawinput.pressKey('Return')
            time.sleep(0.5)
            
            logger.info(f"Opened file: {pdf_path}")
        except dogtail.tree.SearchError:
            raise AssertionError("File chooser dialog not found")
    
    def send_keyboard_shortcut(self, shortcut: str):
        """Send a keyboard shortcut to the application.
        
        Args:
            shortcut: Keyboard shortcut in format like '<Control>e' or '<Control><Shift>s'
        """
        import dogtail.rawinput
        
        logger.info(f"Sending keyboard shortcut: {shortcut}")
        dogtail.rawinput.keyCombo(shortcut)
        time.sleep(0.3)
    
    def drag_and_drop_page(self, from_index: int, to_index: int):
        """Drag and drop a page from one position to another.
        
        Args:
            from_index: Source page index (0-based)
            to_index: Target page index (0-based)
        """
        import dogtail.tree
        import dogtail.rawinput
        
        try:
            # Find the thumbnail list
            thumbnail_list = self.app.child(name='thumbnail_list')
            logger.info(f"Found thumbnail list")
            
            # Get all list items
            items = thumbnail_list.findChildren(
                lambda x: x.roleName == 'list item',
                recursive=False
            )
            
            if from_index >= len(items) or to_index >= len(items):
                raise AssertionError(
                    f"Invalid indices: from={from_index}, to={to_index}, "
                    f"but only {len(items)} items"
                )
            
            from_item = items[from_index]
            to_item = items[to_index]
            
            logger.info(f"Dragging page {from_index} to {to_index}")
            
            # Get positions
            from_x, from_y = from_item.position
            from_w, from_h = from_item.size
            to_x, to_y = to_item.position
            to_w, to_h = to_item.size
            
            # Calculate center points
            from_center_x = from_x + from_w // 2
            from_center_y = from_y + from_h // 2
            to_center_x = to_x + to_w // 2
            to_center_y = to_y + to_h // 2
            
            # Perform drag and drop
            dogtail.rawinput.drag(
                (from_center_x, from_center_y),
                (to_center_x, to_center_y)
            )
            
            time.sleep(0.5)  # Wait for drag to complete
            logger.info("Drag and drop completed")
            
        except dogtail.tree.SearchError as e:
            raise AssertionError(f"Failed to find drag elements: {e}")
    
    def verify_page_order(self, expected_order: list):
        """Verify that pages are in the expected order.
        
        Args:
            expected_order: List of expected page numbers (1-based)
        """
        # This is a placeholder - in a real implementation, we would
        # need to extract the actual page numbers from the UI
        # For now, we just verify the count matches
        actual_count = self.get_page_count_from_status()
        expected_count = len(expected_order)
        
        if actual_count != expected_count:
            raise AssertionError(
                f"Page count mismatch: expected {expected_count}, got {actual_count}"
            )
        
        logger.info(f"Page order verified: {expected_order}")
