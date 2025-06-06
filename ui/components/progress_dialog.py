"""
Progress Dialog Component

A modern progress dialog with cancel support and status updates.
This component demonstrates proper modal dialog implementation in PyQt6.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """
    Modern progress dialog with cancel functionality.
    
    Features:
    - Progress bar with percentage display
    - Status message updates
    - Optional detailed log view
    - Cancel button with confirmation
    - Non-modal option for background operations
    
    Usage:
        dialog = ProgressDialog(parent, "Processing File")
        dialog.show_progress(50, "Processing stations...")
        dialog.cancelled.connect(processor.cancel)
    """
    
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None, title="Progress", show_details=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200 if not show_details else 350)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        self._setup_ui(show_details)
        self._apply_styles()
        
        # Center on parent
        if parent:
            self.move(
                parent.x() + (parent.width() - self.width()) // 2,
                parent.y() + (parent.height() - self.height()) // 2
            )
    
    def _setup_ui(self, show_details):
        """Setup the dialog UI layout"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        self.title_label = QLabel("Processing...")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Progress bar with percentage
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(progress_layout)
        
        # Details section (optional)
        if show_details:
            self.details_text = QTextEdit()
            self.details_text.setMaximumHeight(100)
            self.details_text.setReadOnly(True)
            layout.addWidget(self.details_text)
        else:
            self.details_text = None
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _apply_styles(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QLabel {
                color: #212529;
                background: transparent;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                text-align: center;
                background-color: #e9ecef;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #007bff, stop: 1 #0056b3
                );
                border-radius: 3px;
            }
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """)
    
    def show_progress(self, percentage, status_message=""):
        """
        Update progress display.
        
        Args:
            percentage: Progress percentage (0-100)
            status_message: Current operation status
        """
        self.progress_bar.setValue(max(0, min(100, percentage)))
        
        if status_message:
            self.status_label.setText(status_message)
            
            # Add to details if available
            if self.details_text:
                self.details_text.append(f"[{percentage:3d}%] {status_message}")
                # Auto-scroll to bottom
                scrollbar = self.details_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
    
    def set_title(self, title):
        """Update the dialog title"""
        self.title_label.setText(title)
    
    def complete_progress(self, final_message="Completed successfully!"):
        """
        Mark progress as complete.
        
        Args:
            final_message: Final status message
        """
        self.progress_bar.setValue(100)
        self.status_label.setText(final_message)
        self.cancel_button.setText("Close")
        
        # Change button style to indicate completion
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
    
    def show_error(self, error_message):
        """
        Display error state.
        
        Args:
            error_message: Error description
        """
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        self.cancel_button.setText("Close")
        
        # Change button style to indicate error
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
    
    def _on_cancel(self):
        """Handle cancel button click"""
        if self.cancel_button.text() == "Cancel":
            # Emit cancelled signal for active operations
            self.cancelled.emit()
        
        # Close dialog
        self.accept()
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.cancel_button.text() == "Cancel":
            self.cancelled.emit()
        event.accept()


# Template Usage Example:
"""
Here's how to use the ProgressDialog component:

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = ExcelProcessor()
        
        # Connect processor signals
        self.processor.progress_updated.connect(self.update_progress)
        self.processor.status_updated.connect(self.update_status)
        self.processor.processing_completed.connect(self.on_processing_done)
        self.processor.processing_failed.connect(self.on_processing_error)
    
    def start_processing(self, file_path):
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog(self, "Processing Excel File", show_details=True)
        self.progress_dialog.cancelled.connect(self.processor.cancel_processing)
        self.progress_dialog.show()
        
        # Start processing
        self.processor.process_file(file_path)
    
    def update_progress(self, percentage):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.show_progress(percentage)
    
    def update_status(self, message):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.show_progress(self.progress_dialog.progress_bar.value(), message)
    
    def on_processing_done(self, machine_data):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.complete_progress("File processed successfully!")
        # Handle the machine_data...
    
    def on_processing_error(self, error_message):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.show_error(error_message)
"""
