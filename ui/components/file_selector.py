"""
File Selector Component

A modern file selection widget with drag-and-drop support and validation.
This component demonstrates advanced file handling in PyQt6.
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QLineEdit, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette


class FileSelector(QFrame):
    """
    Advanced file selector with drag-and-drop support.
    
    Features:
    - Browse button for file selection
    - Drag and drop file support
    - File validation (extensions, existence)
    - Visual feedback for valid/invalid files
    - Clear functionality
    - Path display with tooltip
    
    Signals:
        file_selected: Emitted when a valid file is selected
        file_cleared: Emitted when file selection is cleared
    
    Usage:
        selector = FileSelector(
            title="Select Excel File",
            file_filter="Excel files (*.xlsx *.xls *.xlsm)",
            allowed_extensions=[".xlsx", ".xls", ".xlsm"]
        )
        selector.file_selected.connect(self.handle_file_selection)
    """
    
    file_selected = pyqtSignal(str)  # file_path
    file_cleared = pyqtSignal()
    
    def __init__(self, parent=None, title="Select File", 
                 file_filter="All files (*.*)", allowed_extensions=None):
        super().__init__(parent)
        
        self.title = title
        self.file_filter = file_filter
        self.allowed_extensions = allowed_extensions or []
        self.current_file = None
        
        self._setup_ui()
        self._apply_styles()
        self._enable_drag_drop()
    
    def _setup_ui(self):
        """Setup the file selector UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Title label
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # File selection row
        file_layout = QHBoxLayout()
        
        # File path display
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("No file selected (click Browse or drag & drop)")
        self.path_edit.setReadOnly(True)
        file_layout.addWidget(self.path_edit, 1)
        
        # Browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_button)
        
        # Clear button
        self.clear_button = QPushButton("×")
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.clicked.connect(self._clear_file)
        self.clear_button.setEnabled(False)
        file_layout.addWidget(self.clear_button)
        
        layout.addLayout(file_layout)
        
        # Status/info label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Drag and drop area indicator
        self.drop_area = QLabel("Drag & Drop files here")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setMinimumHeight(60)
        layout.addWidget(self.drop_area)
    
    def _apply_styles(self):
        """Apply modern styling"""
        self.setStyleSheet("""
            FileSelector {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            
            QLabel {
                color: #495057;
                background: transparent;
            }
            
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: monospace;
            }
            
            QLineEdit[readOnly="true"] {
                background-color: #f8f9fa;
                color: #6c757d;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004085;
            }
            
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
            
            QLabel#drop_area {
                border: 2px dashed #ced4da;
                border-radius: 4px;
                color: #6c757d;
                background-color: #f8f9fa;
                font-style: italic;
            }
        """)
        
        # Set object name for drop area styling
        self.drop_area.setObjectName("drop_area")
    
    def _enable_drag_drop(self):
        """Enable drag and drop functionality"""
        self.setAcceptDrops(True)
        self.drop_area.setAcceptDrops(True)
    
    def _browse_file(self):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, self.title, "", self.file_filter
        )
        
        if file_path:
            self._set_file(file_path)
    
    def _clear_file(self):
        """Clear current file selection"""
        self.current_file = None
        self.path_edit.clear()
        self.path_edit.setPlaceholderText("No file selected (click Browse or drag & drop)")
        self.clear_button.setEnabled(False)
        self.status_label.clear()
        self._update_drop_area_style(False)
        self.file_cleared.emit()
    
    def _set_file(self, file_path):
        """Set the selected file and validate it"""
        file_path = str(file_path).strip()
        
        # Validate file
        if not self._validate_file(file_path):
            return
        
        self.current_file = file_path
        
        # Display shortened path if too long
        display_path = self._get_display_path(file_path)
        self.path_edit.setText(display_path)
        self.path_edit.setToolTip(file_path)
        
        self.clear_button.setEnabled(True)
        
        # Update status
        file_size = os.path.getsize(file_path)
        self.status_label.setText(
            f"File: {os.path.basename(file_path)} ({self._format_file_size(file_size)})"
        )
        
        self._update_drop_area_style(True)
        self.file_selected.emit(file_path)
    
    def _validate_file(self, file_path):
        """Validate the selected file"""
        # Check if file exists
        if not os.path.isfile(file_path):
            self.status_label.setText("Error: File does not exist")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            return False
        
        # Check file extension if specified
        if self.allowed_extensions:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in [ext.lower() for ext in self.allowed_extensions]:
                allowed = ", ".join(self.allowed_extensions)
                self.status_label.setText(f"Error: Invalid file type. Allowed: {allowed}")
                self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
                return False
        
        # Clear any previous error styling
        self.status_label.setStyleSheet("")
        return True
    
    def _get_display_path(self, file_path, max_length=50):
        """Get a shortened display path if the full path is too long"""
        if len(file_path) <= max_length:
            return file_path
        
        # Show start and end of path
        start_length = max_length // 2 - 2
        end_length = max_length - start_length - 3
        
        return f"{file_path[:start_length]}...{file_path[-end_length:]}"
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _update_drop_area_style(self, has_file):
        """Update drop area visual style based on file state"""
        if has_file:
            self.drop_area.setText("✓ File loaded successfully")
            self.drop_area.setStyleSheet("""
                QLabel#drop_area {
                    border: 2px solid #28a745;
                    background-color: #d4edda;
                    color: #155724;
                }
            """)
        else:
            self.drop_area.setText("Drag & Drop files here")
            self.drop_area.setStyleSheet("""
                QLabel#drop_area {
                    border: 2px dashed #ced4da;
                    background-color: #f8f9fa;
                    color: #6c757d;
                }
            """)
    
    # Drag and Drop Event Handlers
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Visual feedback for drag over
            self.drop_area.setStyleSheet("""
                QLabel#drop_area {
                    border: 2px solid #007bff;
                    background-color: #e3f2fd;
                    color: #0277bd;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        # Restore normal style
        self._update_drop_area_style(self.current_file is not None)
    
    def dropEvent(self, event: QDropEvent):
        """Handle file drop event"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self._set_file(file_path)
        
        event.acceptProposedAction()
    
    # Public Methods
    
    def get_file_path(self):
        """Get the currently selected file path"""
        return self.current_file
    
    def set_file_path(self, file_path):
        """Programmatically set the file path"""
        if file_path and os.path.isfile(file_path):
            self._set_file(file_path)
    
    def clear(self):
        """Clear the current selection"""
        self._clear_file()
    
    def is_file_selected(self):
        """Check if a file is currently selected"""
        return self.current_file is not None


# Template Usage Example:
"""
Here's how to use the FileSelector component:

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create file selector
        self.file_selector = FileSelector(
            title="Select Machine Configuration File",
            file_filter="Excel files (*.xlsx *.xls *.xlsm)",
            allowed_extensions=[".xlsx", ".xls", ".xlsm"]
        )
        
        # Connect signals
        self.file_selector.file_selected.connect(self.on_file_selected)
        self.file_selector.file_cleared.connect(self.on_file_cleared)
        
        # Add to layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.file_selector)
        self.setCentralWidget(central_widget)
    
    def on_file_selected(self, file_path):
        print(f"File selected: {file_path}")
        # Process the file...
    
    def on_file_cleared(self):
        print("File selection cleared")
        # Clear any related data...
"""
