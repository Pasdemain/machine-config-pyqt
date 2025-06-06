"""
Form Widget Components

Advanced form input widgets with validation and modern styling.
This module demonstrates proper form design patterns in PyQt6.
"""

from typing import Optional, Callable, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QLabel, QFrame, QGroupBox, QPushButton,
    QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QValidator, QPalette
import re


class ValidatedLineEdit(QLineEdit):
    """
    Enhanced line edit with real-time validation and visual feedback.
    
    Features:
    - Real-time validation with visual feedback
    - Custom validator functions
    - Error message display
    - Auto-formatting for specific data types
    - Debounced validation for performance
    
    Usage:
        # Create a numeric input
        numeric_input = ValidatedLineEdit(
            validator_func=lambda x: x.isdigit(),
            error_message="Please enter a valid number",
            placeholder="Enter machine number"
        )
    """
    
    validation_changed = pyqtSignal(bool)  # True if valid, False if invalid
    value_changed = pyqtSignal(str)        # Emitted when value changes and is valid
    
    def __init__(self, parent=None, validator_func=None, error_message="Invalid input", 
                 placeholder="", auto_format_func=None, debounce_ms=300):
        super().__init__(parent)
        
        self.validator_func = validator_func
        self.error_message = error_message
        self.auto_format_func = auto_format_func
        self.is_valid_state = True
        
        # Setup UI
        self.setPlaceholderText(placeholder)
        
        # Debounce timer for validation
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._validate)
        self.debounce_ms = debounce_ms
        
        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply modern styling with validation states"""
        self.setStyleSheet("""
            ValidatedLineEdit {
                border: 2px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                selection-background-color: #007bff;
            }
            
            ValidatedLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            ValidatedLineEdit[valid="true"] {
                border-color: #28a745;
            }
            
            ValidatedLineEdit[valid="false"] {
                border-color: #dc3545;
                background-color: #fff5f5;
            }
            
            ValidatedLineEdit:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
                border-color: #e9ecef;
            }
        """)
    
    def _on_text_changed(self):
        """Handle text change with debouncing"""
        self.validation_timer.stop()
        self.validation_timer.start(self.debounce_ms)
    
    def _validate(self):
        """Perform validation and update visual state"""
        text = self.text().strip()
        
        # Apply auto-formatting if available
        if self.auto_format_func and text:
            formatted_text = self.auto_format_func(text)
            if formatted_text != text:
                # Temporarily disconnect to avoid recursion
                self.textChanged.disconnect(self._on_text_changed)
                self.setText(formatted_text)
                self.textChanged.connect(self._on_text_changed)
                text = formatted_text
        
        # Validate
        is_valid = True
        if self.validator_func:
            try:
                is_valid = self.validator_func(text) if text else True
            except Exception:
                is_valid = False
        
        # Update state
        self._set_validation_state(is_valid)
        
        # Emit signals
        if is_valid != self.is_valid_state:
            self.validation_changed.emit(is_valid)
        
        if is_valid and text:
            self.value_changed.emit(text)
        
        self.is_valid_state = is_valid
    
    def _set_validation_state(self, is_valid):
        """Update visual validation state"""
        self.setProperty("valid", is_valid)
        self.style().polish(self)
        
        # Update tooltip
        if is_valid or not self.text():
            self.setToolTip("")
        else:
            self.setToolTip(self.error_message)
    
    def is_valid(self):
        """Check if current input is valid"""
        return self.is_valid_state
    
    def get_validated_value(self):
        """Get the current value if valid, None otherwise"""
        return self.text().strip() if self.is_valid() else None


class LabeledInput(QWidget):
    """
    A labeled input widget combining a label with an input field.
    
    Usage:
        machine_input = LabeledInput(
            label="Machine Number:",
            input_widget=ValidatedLineEdit(placeholder="Enter machine number"),
            required=True
        )
    """
    
    value_changed = pyqtSignal(object)  # Emitted when input value changes
    
    def __init__(self, label, input_widget, required=False, 
                 help_text="", orientation="horizontal"):
        super().__init__()
        
        self.label_text = label
        self.input_widget = input_widget
        self.required = required
        self.help_text = help_text
        self.orientation = orientation
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the labeled input UI"""
        if self.orientation == "horizontal":
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
        
        # Create label
        self.label = QLabel(self.label_text)
        if self.required:
            self.label.setText(f"{self.label_text} *")
            self.label.setStyleSheet("color: #dc3545; font-weight: bold;")
        
        # Set label font
        label_font = QFont()
        label_font.setBold(True)
        self.label.setFont(label_font)
        
        # Associate label with input for accessibility
        self.label.setBuddy(self.input_widget)
        
        if self.orientation == "horizontal":
            self.label.setFixedWidth(150)
            self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(self.label)
            layout.addWidget(self.input_widget, 1)
        else:
            layout.addWidget(self.label)
            layout.addWidget(self.input_widget)
        
        # Add help text if provided
        if self.help_text:
            help_label = QLabel(self.help_text)
            help_label.setStyleSheet("color: #6c757d; font-size: 12px; font-style: italic;")
            help_label.setWordWrap(True)
            layout.addWidget(help_label)
    
    def _connect_signals(self):
        """Connect input widget signals to our signals"""
        # Connect various input widget signals based on type
        if hasattr(self.input_widget, 'textChanged'):
            self.input_widget.textChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        elif hasattr(self.input_widget, 'valueChanged'):
            self.input_widget.valueChanged.connect(lambda: self.value_changed.emit(self.get_value()))
        elif hasattr(self.input_widget, 'currentTextChanged'):
            self.input_widget.currentTextChanged.connect(lambda: self.value_changed.emit(self.get_value()))
    
    def get_value(self):
        """Get the current value from the input widget"""
        if hasattr(self.input_widget, 'get_validated_value'):
            # ValidatedLineEdit
            return self.input_widget.get_validated_value()
        elif hasattr(self.input_widget, 'text'):
            # QLineEdit, QTextEdit
            return self.input_widget.text()
        elif hasattr(self.input_widget, 'value'):
            # QSpinBox, QDoubleSpinBox
            return self.input_widget.value()
        elif hasattr(self.input_widget, 'currentText'):
            # QComboBox
            return self.input_widget.currentText()
        return None
    
    def set_value(self, value):
        """Set the value of the input widget"""
        if hasattr(self.input_widget, 'setText'):
            self.input_widget.setText(str(value) if value is not None else "")
        elif hasattr(self.input_widget, 'setValue'):
            self.input_widget.setValue(value)
        elif hasattr(self.input_widget, 'setCurrentText'):
            self.input_widget.setCurrentText(str(value) if value is not None else "")
    
    def is_valid(self):
        """Check if the input is valid"""
        if hasattr(self.input_widget, 'is_valid'):
            return self.input_widget.is_valid()
        # For non-validated widgets, consider empty required fields as invalid
        if self.required:
            value = self.get_value()
            return value is not None and str(value).strip() != ""
        return True


class FormSection(QGroupBox):
    """
    A styled form section that groups related inputs.
    
    Usage:
        machine_section = FormSection("Machine Configuration")
        machine_section.add_input("Machine Number", machine_number_input)
        machine_section.add_input("WPH", wph_input)
    """
    
    def __init__(self, title, collapsible=False):
        super().__init__(title)
        self.collapsible = collapsible
        self.labeled_inputs = []
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup the form section UI"""
        self.form_layout = QFormLayout(self)
        self.form_layout.setSpacing(10)
        self.form_layout.setContentsMargins(15, 20, 15, 15)
        
        # Set label alignment
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    def _apply_styles(self):
        """Apply modern section styling"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 5px;
                background-color: #f8f9fa;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
                color: #212529;
            }
        """)
    
    def add_input(self, label, input_widget, required=False, help_text=""):
        """
        Add a labeled input to the form section.
        
        Args:
            label: Label text for the input
            input_widget: The input widget (QLineEdit, QSpinBox, etc.)
            required: Whether this field is required
            help_text: Optional help text
        """
        labeled_input = LabeledInput(
            label=label,
            input_widget=input_widget,
            required=required,
            help_text=help_text,
            orientation="horizontal"
        )
        
        self.labeled_inputs.append(labeled_input)
        self.form_layout.addRow(labeled_input)
        
        return labeled_input
    
    def add_widget(self, widget):
        """Add a custom widget to the form section"""
        self.form_layout.addRow(widget)
    
    def get_values(self):
        """Get all values from the form section as a dictionary"""
        values = {}
        for labeled_input in self.labeled_inputs:
            label = labeled_input.label_text.rstrip(': *')
            values[label] = labeled_input.get_value()
        return values
    
    def set_values(self, values_dict):
        """Set values for inputs in the form section"""
        for labeled_input in self.labeled_inputs:
            label = labeled_input.label_text.rstrip(': *')
            if label in values_dict:
                labeled_input.set_value(values_dict[label])
    
    def validate_all(self):
        """Validate all inputs in the section"""
        all_valid = True
        for labeled_input in self.labeled_inputs:
            if not labeled_input.is_valid():
                all_valid = False
        return all_valid
    
    def get_invalid_fields(self):
        """Get list of invalid field labels"""
        invalid_fields = []
        for labeled_input in self.labeled_inputs:
            if not labeled_input.is_valid():
                label = labeled_input.label_text.rstrip(': *')
                invalid_fields.append(label)
        return invalid_fields


# Validation Helper Functions
def create_numeric_validator(min_value=None, max_value=None, allow_decimal=False):
    """Create a numeric validator function"""
    def validator(text):
        if not text:
            return True
        try:
            value = float(text) if allow_decimal else int(text)
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True
        except ValueError:
            return False
    return validator


def create_text_validator(min_length=0, max_length=None, pattern=None):
    """Create a text validator function"""
    def validator(text):
        if len(text) < min_length:
            return False
        if max_length and len(text) > max_length:
            return False
        if pattern and not re.match(pattern, text):
            return False
        return True
    return validator


def machine_number_formatter(text):
    """Auto-format machine number to uppercase"""
    return text.upper().strip()
