# Machine Configuration PyQt Interface

A modern PyQt6-based application for managing machine configuration data from Excel files.

## Features

✅ **Implemented and Working:**
- Modern PyQt6 interface with optimized components
- Excel file processing with threading and progress tracking
- Hierarchical data visualization with interactive tables
- Real-time search and filtering capabilities
- Form validation with visual feedback
- Drag & drop file support
- JSON and CSV export functionality
- Professional styling and responsive design
- Well-documented components for learning and reuse

## Installation

```bash
# Clone the repository
git clone https://github.com/Pasdemain/machine-config-pyqt.git
cd machine-config-pyqt

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
python main.py
```

## Project Structure

```
machine-config-pyqt/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── models/                     # Data models and processing
│   ├── __init__.py
│   ├── machine_data.py        # Core data structures with PyQt signals
│   └── excel_processor.py     # Threaded Excel file processing
├── ui/                        # User interface components
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   └── components/            # Reusable UI components
│       ├── __init__.py
│       ├── progress_dialog.py # Modern progress dialog with cancel
│       ├── file_selector.py   # File selector with drag & drop
│       ├── data_tables.py     # Advanced table models and views
│       ├── form_widgets.py    # Validated form inputs
│       └── modern_widgets.py  # Styled modern widgets
└── README.md
```

## Key Components and Learning Resources

### 1. Data Models (`models/`)
- **MachineData**: Main data container with PyQt signals for reactive UI
- **ExcelProcessor**: Threaded file processing with progress tracking
- **Station/Actuator**: Well-structured data classes with validation

### 2. UI Components (`ui/components/`)

#### Progress Dialog (`progress_dialog.py`)
```python
# Modern progress dialog with cancel support
dialog = ProgressDialog(parent, "Processing File", show_details=True)
dialog.cancelled.connect(processor.cancel)
dialog.show_progress(50, "Processing stations...")
```

#### File Selector (`file_selector.py`)
```python
# File selector with drag & drop and validation
selector = FileSelector(
    title="Select Excel File",
    file_filter="Excel files (*.xlsx *.xls *.xlsm)",
    allowed_extensions=[".xlsx", ".xls", ".xlsm"]
)
selector.file_selected.connect(self.handle_file_selection)
```

#### Data Tables (`data_tables.py`)
```python
# Custom table models with sorting and filtering
station_model = StationTableModel()
proxy_model = SearchableTableModel()
proxy_model.setSourceModel(station_model)

table_view = DataTableView(enable_sorting=True)
table_view.setModel(proxy_model)
```

#### Form Widgets (`form_widgets.py`)
```python
# Validated input with real-time feedback
validated_input = ValidatedLineEdit(
    validator_func=lambda x: x.isdigit() and int(x) > 0,
    placeholder="Enter machine number",
    error_message="Must be a positive number"
)

# Form sections for organization
form_section = FormSection("Machine Configuration")
form_section.add_input("Machine Number:", validated_input, required=True)
```

#### Modern Widgets (`modern_widgets.py`)
```python
# Styled modern buttons
primary_btn = ModernButton("Process File", style="primary")
success_btn = ModernButton("✓ Complete", style="success")

# Modern frames with titles
frame = ModernFrame("Configuration Panel")
frame.add_widget(some_widget)

# Status indicators
status = StatusIndicator()
status.set_status("success", "File loaded successfully")
```

## Architecture Highlights

### 1. **Model-View Architecture**
- Proper separation between data models and UI components
- Custom QAbstractTableModel implementations for optimal performance
- Proxy models for search/filtering without modifying source data

### 2. **Threading and Progress Tracking**
- Non-blocking Excel file processing using QThread
- Real-time progress updates with cancellation support
- Proper resource cleanup and error handling

### 3. **Signal-Slot Communication**
- Reactive UI updates through PyQt signals
- Loose coupling between components
- Event-driven architecture for better maintainability

### 4. **Modern UI Design**
- Professional styling with CSS-like syntax
- Responsive layouts that adapt to window resizing
- Consistent visual hierarchy and spacing

### 5. **Data Validation**
- Real-time input validation with visual feedback
- Custom validator functions for different data types
- Form-level validation with error reporting

## Excel File Format

The application expects Excel files with the following structure:

### Info Sheet
- Cell B2: Machine number

### Station Sheets (ST01, ST02, etc.)
- Row 1, Column B: Station name
- Row 4, Column B: Upstream number  
- Row 8+: Actuator data with columns:
  - Column A: Actuator number
  - Column B: Actuator name
  - Column C: Total tracks
  - Column D: Upstream numbering

## Usage Examples

### Basic File Processing
1. **Import File**: Use File → Import Excel File or drag & drop
2. **View Data**: Browse stations in left table, actuators in right table
3. **Search**: Use search boxes to filter data in real-time
4. **Validate**: Click "Validate Configuration" to check data completeness
5. **Export**: Choose File → Export or use Export Data button

### Programming Examples

#### Creating a Custom Validator
```python
def create_machine_id_validator():
    """Custom validator for machine IDs"""
    def validator(text):
        # Must be 3-10 characters, alphanumeric
        if not text:
            return True  # Allow empty for optional fields
        return (3 <= len(text) <= 10 and 
                text.replace('-', '').replace('_', '').isalnum())
    return validator

# Use in form
machine_input = ValidatedLineEdit(
    validator_func=create_machine_id_validator(),
    error_message="Machine ID must be 3-10 alphanumeric characters"
)
```

#### Custom Table Model
```python
class CustomTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        return 3  # Adjust based on your columns
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return QVariant()
```

## Performance Optimizations

1. **Table Views**: Uniform row heights and efficient scrolling
2. **Threading**: Background processing for file operations  
3. **Proxy Models**: Efficient filtering without data duplication
4. **Memory Management**: Proper cleanup of threads and dialogs
5. **Lazy Loading**: Tables only render visible rows

## Extending the Application

### Adding New Components
1. Create new component in `ui/components/`
2. Follow existing patterns for styling and signals
3. Add comprehensive docstrings and usage examples
4. Include the component in `ui/components/__init__.py`

### Adding New Data Types
1. Extend `MachineData` class with new properties
2. Add corresponding UI form fields
3. Update Excel processor if needed
4. Add validation rules

### Custom Styling
```python
# Override component styles
component.setStyleSheet("""
    QWidget {
        background-color: #custom-color;
        border-radius: 8px;
    }
""")
```

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Excel File Not Loading**: Check file format and sheet structure
   - Ensure 'Info' sheet exists
   - Station sheets must start with 'ST'

3. **Performance Issues**: For large files (1000+ stations)
   - Consider implementing pagination
   - Use virtual scrolling for tables

4. **Styling Issues**: Check that stylesheets are properly applied
   - Use `component.style().polish(component)` to refresh

## Contributing

This project demonstrates modern PyQt6 development patterns. Key areas for enhancement:

- **Database Integration**: Add SQLite support for data persistence
- **Advanced Filtering**: Multi-column filtering with saved filter sets
- **Data Visualization**: Charts and graphs for configuration analysis
- **Internationalization**: Multi-language support
- **Plugin System**: Extensible architecture for custom processors

## Learning Resources

Each component includes detailed docstrings and usage examples. The codebase demonstrates:

- **PyQt6 Best Practices**: Modern signal/slot usage, proper threading
- **Design Patterns**: Model-View, Observer, Command patterns
- **Performance Optimization**: Efficient data handling and UI updates
- **User Experience**: Progressive disclosure, visual feedback, error handling

## License

This project is designed as a learning resource and template for PyQt6 applications.
