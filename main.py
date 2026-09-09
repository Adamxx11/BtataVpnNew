#!/usr/bin/env python3
"""
Batata VPN - Simple VPN Client for Windows 10/11

Entry point for the application.
Auto-elevates to administrator if needed.
"""

import sys
import os
from pathlib import Path
import ctypes

# Auto-elevate to administrator on Windows
try:
    import pyuac
    if not pyuac.isUserAdmin():
        # Re-run this script with administrator privileges
        pyuac.runAsAdmin()
        sys.exit()
except (ImportError, AttributeError):
    # pyuac not installed or failed, use alternative method
    try:
        if not ctypes.windll.shell.IsUserAnAdmin():
            ctypes.windll.shell.ShellExecuteEx(
                lpVerb='runas',
                lpFile=sys.executable,
                lpParameters=f'"{__file__}"',
                lpDirectory=str(Path(__file__).parent)
            )
            sys.exit()
    except Exception as e:
        print(f"Warning: Could not elevate to admin: {e}")
        pass

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """
    Start the Batata VPN application.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
