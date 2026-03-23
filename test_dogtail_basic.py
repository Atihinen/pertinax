#!/usr/bin/env python3
"""
Basic test to verify dogtail and accessibility infrastructure works.
Run with: xvfb-run -a python3 test_dogtail_basic.py
"""

import sys
import time
import subprocess
import os

def test_import():
    """Test if dogtail can be imported."""
    print("Testing dogtail import...")
    
    # Enable accessibility before importing dogtail
    print("Enabling accessibility...")
    try:
        import gi
        gi.require_version('Atspi', '2.0')
        from gi.repository import Atspi
        print("✓ AT-SPI available")
    except Exception as e:
        print(f"! Warning: Could not load AT-SPI: {e}")
    
    # Set environment
    os.environ['GTK_MODULES'] = 'gail:atk-bridge'
    os.environ['NO_AT_BRIDGE'] = '0'
    
    try:
        import dogtail.tree
        from dogtail import config
        
        # Disable accessibility check for headless testing
        config.config.checkForA11y = False
        
        print("✓ Dogtail imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import dogtail: {e}")
        return False

def test_accessibility_tree():
    """Test if we can access the accessibility tree."""
    print("\nTesting accessibility tree access...")
    try:
        import dogtail.tree
        root = dogtail.tree.root
        print(f"✓ Accessibility root accessible: {root}")
        
        # List available applications
        print("\nAvailable applications:")
        apps = list(root.applications())
        if apps:
            for app in apps:
                print(f"  - {app.name} (role: {app.roleName})")
        else:
            print("  (no applications in accessibility tree)")
        
        return True
    except Exception as e:
        print(f"✗ Failed to access accessibility tree: {e}")
        return False

def test_launch_app():
    """Test launching Pertinax and finding it in accessibility tree."""
    print("\nTesting application launch...")
    try:
        import dogtail.tree
        from dogtail import config
        
        # Configure dogtail for headless testing
        config.config.checkForA11y = False
        config.config.searchCutoffCount = 20
        config.config.defaultDelay = 0.3
        
        # Set environment for accessibility
        env = os.environ.copy()
        env['GTK_MODULES'] = 'gail:atk-bridge'
        env['NO_AT_BRIDGE'] = '0'
        
        # Launch app
        print("Launching pertinax_gui.py...")
        
        # Use the virtual environment's python
        python_exe = '/home/atihinen/.venvs/pertinax/bin/python3'
        if not os.path.exists(python_exe):
            python_exe = 'python3'
            print(f"Warning: venv python not found, using system python")
        else:
            print(f"Using venv python: {python_exe}")
        
        proc = subprocess.Popen(
            [python_exe, 'src/pertinax_gui.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait for it to appear
        print("Waiting for app to appear in accessibility tree...")
        for attempt in range(15):
            time.sleep(0.5)
            
            # Check if process crashed
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                print(f"✗ App crashed during startup")
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
                return False
            
            # Try to find it
            try:
                # Try multiple possible names
                app = None
                for name in ['pertinax_gui.py', 'Pertinax PDF Compositor', 'python3', 'pertinax']:
                    try:
                        app = dogtail.tree.root.application(name)
                        print(f"✓ Found application as '{name}' in accessibility tree after {attempt+1} attempts")
                        break
                    except dogtail.tree.SearchError:
                        continue
                
                if app:
                    print(f"  Name: {app.name}")
                    print(f"  Role: {app.roleName}")
                    
                    # Try to enumerate children
                    children = list(app.children)
                    print(f"  Children: {len(children)}")
                    
                    # Clean up
                    proc.terminate()
                    proc.wait(timeout=2)
                    return True
                else:
                    print(f"  Attempt {attempt+1}/15: not found with any expected name...")
                    continue
            except dogtail.tree.SearchError:
                print(f"  Attempt {attempt+1}/15: not found yet...")
                continue
        
        print("✗ Failed to find app in accessibility tree after 15 attempts")
        
        # Check what apps are available
        print("\nApplications visible in tree:")
        for app in dogtail.tree.root.applications():
            print(f"  - {app.name}")
        
        proc.terminate()
        proc.wait(timeout=2)
        return False
        
    except Exception as e:
        print(f"✗ Exception during app launch test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Dogtail Basic Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Import", test_import()))
    results.append(("Accessibility Tree", test_accessibility_tree()))
    results.append(("Launch App", test_launch_app()))
    
    print("\n" + "=" * 60)
    print("Results:")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:25s} {status}")
    
    all_passed = all(r for _, r in results)
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed"))
    sys.exit(0 if all_passed else 1)
