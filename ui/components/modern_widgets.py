"""
Modern Widget Components

Stylish, modern replacements for standard Qt widgets.
This module demonstrates advanced styling and custom widget creation.
"""

from PyQt6.QtWidgets import (
    QPushButton, QFrame, QGroupBox, QLabel, QWidget,
    QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPen


class ModernButton(QPushButton):
    """
    A modern, styled button with hover animations and multiple variants.
    
    Features:
    - Multiple button styles (primary, secondary, success, danger, etc.)
    - Smooth hover animations
    - Loading state with spinner
    - Icon support
    - Customizable sizing
    
    Usage:
        # Primary button
        primary_btn = ModernButton("Process File", style="primary")
        
        # Success button with icon
        success_btn = ModernButton("✓ Complete", style="success")
        
        # Danger button
        danger_btn = ModernButton("✗ Cancel", style="danger")
    """
    
    def __init__(self, text="", style="primary", size="medium", parent=None):
        super().__init__(text, parent)
        
        self.style_variant = style
        self.size_variant = size
        self.is_loading = False
        
        self._setup_button()
        self._apply_styles()
    
    def _setup_button(self):
        """Setup button properties"""
        # Set font based on size
        font = QFont()
        font.setBold(True)
        
        if self.size_variant == "small":
            font.setPointSize(10)
            self.setMinimumHeight(32)
            self.setMinimumWidth(80)
        elif self.size_variant == "large":
            font.setPointSize(14)
            self.setMinimumHeight(48)
            self.setMinimumWidth(120)
        else:  # medium
            font.setPointSize(12)
            self.setMinimumHeight(40)
            self.setMinimumWidth(100)
        
        self.setFont(font)
        
        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
    
    def _apply_styles(self):
        """Apply modern styling based on variant"""
        # Base styles
        base_style = """
            ModernButton {
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                text-align: center;
            }
            
            ModernButton:disabled {
                opacity: 0.6;
            }
        """
        
        # Style variants
        style_variants = {
            "primary": """
                ModernButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #007bff, stop: 1 #0056b3);
                    color: white;
                }
                ModernButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #0056b3, stop: 1 #004085);
                }
                ModernButton:pressed {
                    background: #004085;
                }
            """,
            "secondary": """
                ModernButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #6c757d, stop: 1 #545b62);
                    color: white;
                }
                ModernButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #545b62, stop: 1 #495057);
                }
                ModernButton:pressed {
                    background: #495057;
                }
            """,
            "success": """
                ModernButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #28a745, stop: 1 #1e7e34);
                    color: white;
                }
                ModernButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #1e7e34, stop: 1 #155724);
                }
                ModernButton:pressed {
                    background: #155724;
                }
            """,
            "danger": """
                ModernButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #dc3545, stop: 1 #c82333);
                    color: white;
                }
                ModernButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #c82333, stop: 1 #bd2130);
                }
                ModernButton:pressed {
                    background: #bd2130;
                }
            """,
            "outline": """
                ModernButton {
                    background: transparent;
                    border: 2px solid #007bff;
                    color: #007bff;
                }
                ModernButton:hover {
                    background: #007bff;
                    color: white;
                }
                ModernButton:pressed {
                    background: #0056b3;
                    border-color: #0056b3;
                }
            """
        }
        
        style = base_style + style_variants.get(self.style_variant, style_variants["primary"])
        self.setStyleSheet(style)
    
    def set_loading(self, loading=True):
        """Set button loading state"""
        self.is_loading = loading
        if loading:
            self.setText("⟳ Loading...")
            self.setEnabled(False)
        else:
            self.setEnabled(True)


class ModernFrame(QFrame):
    """
    A modern frame with subtle styling and optional title.
    
    Features:
    - Clean, minimal design
    - Optional title bar
    - Subtle shadows and borders
    - Responsive padding
    
    Usage:
        frame = ModernFrame(title="Configuration Panel")
        layout = QVBoxLayout(frame)
        layout.addWidget(some_widget)
    """
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        
        self.title_text = title
        self._setup_frame()
    
    def _setup_frame(self):
        """Setup frame layout and styling"""
        self.setFrameStyle(QFrame.Shape.Box)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)
        
        # Title bar (if title provided)
        if self.title_text:
            title_frame = QFrame()
            title_layout = QHBoxLayout(title_frame)
            title_layout.setContentsMargins(15, 10, 15, 10)
            
            title_label = QLabel(self.title_text)
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(12)
            title_label.setFont(title_font)
            
            title_layout.addWidget(title_label)
            title_layout.addStretch()
            
            title_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #dee2e6;
                }
            """)
            
            main_layout.addWidget(title_frame)
        
        # Content area
        self.content_widget = QWidget()
        main_layout.addWidget(self.content_widget)
        
        # Apply styling
        self.setStyleSheet("""
            ModernFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
    
    def content_layout(self):
        """Get or create the content layout"""
        if not self.content_widget.layout():
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)
        return self.content_widget.layout()
    
    def add_widget(self, widget):
        """Add a widget to the content area"""
        self.content_layout().addWidget(widget)


class ModernGroupBox(QGroupBox):
    """
    A modern group box with enhanced styling.
    
    Features:
    - Clean, modern appearance
    - Improved typography
    - Subtle borders and backgrounds
    - Collapsible functionality (optional)
    
    Usage:
        group = ModernGroupBox("Station Configuration")
        layout = QVBoxLayout(group)
        layout.addWidget(some_widget)
    """
    
    def __init__(self, title="", collapsible=False, parent=None):
        super().__init__(title, parent)
        
        self.collapsible = collapsible
        self.is_collapsed = False
        
        self._setup_groupbox()
    
    def _setup_groupbox(self):
        """Setup group box styling and behavior"""
        # Apply modern styling
        self.setStyleSheet("""
            ModernGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: #ffffff;
            }
            
            ModernGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: #ffffff;
                color: #212529;
                border-radius: 4px;
            }
        """)
        
        # Setup collapsible functionality if enabled
        if self.collapsible:
            self.setCheckable(True)
            self.setChecked(True)
            self.toggled.connect(self._on_toggle)
    
    def _on_toggle(self, checked):
        """Handle group box toggle for collapsible functionality"""
        self.is_collapsed = not checked
        
        # Hide/show child widgets
        for child in self.findChildren(QWidget):
            if child != self:
                child.setVisible(checked)
        
        # Animate height change (simplified)
        if checked:
            self.setMaximumHeight(16777215)  # Reset max height
        else:
            self.setMaximumHeight(30)  # Collapse to title height


class StatusIndicator(QLabel):
    """
    A modern status indicator with colored badges.
    
    Features:
    - Multiple status types (success, warning, error, info)
    - Animated transitions
    - Icon support
    - Customizable styling
    
    Usage:
        status = StatusIndicator()
        status.set_status("success", "File loaded successfully")
        status.set_status("error", "Failed to process file")
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_status = "info"
        self._setup_indicator()
    
    def _setup_indicator(self):
        """Setup status indicator styling"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumHeight(32)
        
        # Base styling
        self.setStyleSheet("""
            StatusIndicator {
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
    
    def set_status(self, status_type, message):
        """
        Set the status indicator state.
        
        Args:
            status_type: 'success', 'warning', 'error', 'info'
            message: Status message to display
        """
        self.current_status = status_type
        self.setText(message)
        
        # Status-specific styling
        status_styles = {
            "success": """
                StatusIndicator {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
            """,
            "warning": """
                StatusIndicator {
                    background-color: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeeba;
                }
            """,
            "error": """
                StatusIndicator {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
            """,
            "info": """
                StatusIndicator {
                    background-color: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
            """
        }
        
        base_style = """
            StatusIndicator {
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
        """
        
        full_style = base_style + status_styles.get(status_type, status_styles["info"])
        self.setStyleSheet(full_style)
    
    def clear_status(self):
        """Clear the status indicator"""
        self.setText("")
        self.setStyleSheet("""
            StatusIndicator {
                background: transparent;
                border: none;
            }
        """)


class SearchBox(QWidget):
    """
    A modern search box with search icon and clear functionality.
    
    Features:
    - Search icon
    - Clear button
    - Placeholder text
    - Real-time search signals
    - Modern styling
    
    Usage:
        search_box = SearchBox(placeholder="Search stations...")
        search_box.search_changed.connect(self.filter_data)
    """
    
    search_changed = pyqtSignal(str)  # Emitted when search text changes
    search_cleared = pyqtSignal()     # Emitted when search is cleared
    
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        
        self.placeholder_text = placeholder
        self._setup_search_box()
    
    def _setup_search_box(self):
        """Setup search box layout and styling"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create search input
        from PyQt6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.placeholder_text)
        self.search_input.textChanged.connect(self._on_text_changed)
        
        # Create clear button
        self.clear_button = QPushButton("✕")
        self.clear_button.setFixedSize(24, 24)
        self.clear_button.clicked.connect(self._clear_search)
        self.clear_button.setVisible(False)
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.clear_button)
        
        # Apply styling
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                margin-left: 4px;
            }
            
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
    
    def _on_text_changed(self, text):
        """Handle search text changes"""
        # Show/hide clear button
        self.clear_button.setVisible(bool(text))
        
        # Emit search signal
        self.search_changed.emit(text)
    
    def _clear_search(self):
        """Clear the search input"""
        self.search_input.clear()
        self.search_cleared.emit()
    
    def get_text(self):
        """Get current search text"""
        return self.search_input.text()
    
    def set_text(self, text):
        """Set search text"""
        self.search_input.setText(text)


# Template Usage Example:
"""
Here's how to use the modern widget components:

class ModernInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Modern frame with title
        config_frame = ModernFrame("Machine Configuration")
        
        # Add widgets to frame
        config_frame.add_widget(QLabel("Configuration settings..."))
        
        # Modern buttons
        button_layout = QHBoxLayout()
        
        primary_btn = ModernButton("Process", style="primary")
        secondary_btn = ModernButton("Cancel", style="secondary")
        success_btn = ModernButton("✓ Complete", style="success")
        
        button_layout.addWidget(primary_btn)
        button_layout.addWidget(secondary_btn)
        button_layout.addWidget(success_btn)
        
        config_frame.add_widget(QWidget())  # Spacer
        config_frame.content_layout().addLayout(button_layout)
        
        # Search box
        search_box = SearchBox("Search configurations...")
        search_box.search_changed.connect(self.handle_search)
        
        # Status indicator
        status = StatusIndicator()
        status.set_status("info", "Ready to process files")
        
        # Add to main layout
        layout.addWidget(search_box)
        layout.addWidget(config_frame)
        layout.addWidget(status)
    
    def handle_search(self, text):
        print(f"Search: {text}")
"""
