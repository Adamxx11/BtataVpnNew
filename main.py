#!/usr/bin/env python3
"""
Batata VPN - Simple VPN Client for Windows 10/11

Entry point for the application.
Auto-elevates to administrator if needed.
"""

import sys
import os
from pathlib import Path

# Auto-elevate to administrator on Windows
try:
    import pyuac
    if not pyuac.isUserAdmin():
        # Re-run this script with administrator privileges
        pyuac.runAsAdmin()
        sys.exit()
except ImportError:
    # pyuac not installed, continue anyway
    # (Will show warning in GUI if not admin)
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
