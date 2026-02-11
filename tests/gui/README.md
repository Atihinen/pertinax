# GUI Testing Status

## Current Issues

### AT-SPI Accessibility in Xvfb
GTK 4 applications do not automatically register with the AT-SPI accessibility tree when running in Xvfb (headless mode). This prevents dogtail from finding and interacting with the application.

**Root Cause:**
- GTK 4 requires a full D-Bus session with proper AT-SPI registry
- Xvfb provides no accessibility services by default
- `dbus-run-session` creates a session bus but GTK 4 apps don't auto-register

**Attempted Solutions:**
1. ✗ `dbus-run-session` + `xvfb-run` - App launches but not in accessibility tree
2. ✗ `config.config.checkForA11y = False` - Bypasses check but doesn't expose app
3. ✗ Setting GTK_MODULES=gail:atk-bridge - No effect in headless mode
4. ✗ Using multiple app name variations - App never appears in tree

**Working Alternatives:**
1. ✓ Run tests on real X11 display (e.g., VNC server, actual desktop)
2. ✓ Manual GUI testing with documented test cases
3. ✓ Unit tests for core logic (already implemented)

## Current Test Status

### Unit Tests ✓
- [test_document.py](../test_document.py) - 28 tests, all passing
- [test_renderer.py](../test_renderer.py) - 7 tests, all passing

### GUI Tests ✗  
- Robot Framework tests created but cannot run in CI/headless mode
- Dogtail cannot find GTK 4 apps in Xvfb accessibility tree
- Tests are syntactically valid (pass `robot --dryrun`)

## Running GUI Tests

### Option 1: Manual Testing (Recommended)
Follow the test cases in the `.robot` files manually:
```bash
# Launch the app
python3 src/pertinax_gui.py

# Then manually verify:
# - Empty state displays when no PDF loaded
# - Buttons have correct enabled/disabled states
# - Open PDF button works
# - Drag and drop doesn't crash the app
# - Keyboard shortcuts work (Ctrl+O, Ctrl+E)
```

### Option 2: With Real X11 Display
If you have a real X11 display (not WSL, not headless):
```bash
# Install dogtail
sudo apt-get install python3-dogtail

# Run tests
robot --outputdir tests/reports tests/gui/
```

### Option 3: VNC Server (For CI)
Set up a VNC server for true X11 display:
```bash
sudo apt-get install tigervnc-standalone-server
vncserver :1 -geometry 1920x1080 -depth 24
export DISPLAY=:1
robot --outputdir tests/reports tests/gui/
```

## Future Improvements

1. Investigate GTK 4 + AT-SPI + Xvfb compatibility
2. Consider alternative GUI testing frameworks:
   - LDTP (Linux Desktop Testing Project)
   - PyAutoGUI (image-based, no accessibility needed)
   - Selenium-like approach with GTK inspector protocol
3. Focus on unit test coverage for critical drag-drop bug
4. Document manual test procedures

## Test Files

- [test_basic_operations.robot](test_basic_operations.robot) - Launch, empty state, buttons
- [test_drag_drop.robot](test_drag_drop.robot) - Critical drag-drop crash test
- [test_keyboard.robot](test_keyboard.robot) - Keyboard shortcuts
- [resources.robot](resources.robot) - Common keywords
- [PertinaxLibrary.py](PertinaxLibrary.py) - Python test library
- [test_dogtail_basic.py](../../test_dogtail_basic.py) - Diagnostic test
