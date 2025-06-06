#!/usr/bin/env python3
"""
Machine Configuration PyQt Interface
Main application entry point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MachineConfigWindow

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Machine Configuration Manager")
    app.setOrganizationName("MachineConfig")
    
    # Apply modern styling
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MachineConfigWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
