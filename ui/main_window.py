"""
Main Application Window

The primary application window that orchestrates all components.
This module demonstrates proper application architecture and component integration.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QMessageBox, QApplication,
    QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence
import json
import csv
from pathlib import Path

from models.machine_data import MachineData
from models.excel_processor import ExcelProcessor

from .components.file_selector import FileSelector
from .components.progress_dialog import ProgressDialog
from .components.data_tables import (
    StationTableModel, ActuatorTableModel, DataTableView, SearchableTableModel
)
from .components.form_widgets import (
    FormSection, ValidatedLineEdit,
    create_numeric_validator, machine_number_formatter
)
from .components.modern_widgets import (
    ModernButton, ModernFrame, StatusIndicator, SearchBox
)


class MachineConfigWindow(QMainWindow):
    """
    Main application window for machine configuration management.
    
    Features:
    - File import with drag & drop support
    - Real-time data validation
    - Interactive station/actuator browsing
    - Search and filtering capabilities
    - Export functionality
    - Modern, professional styling
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize data models
        self.machine_data = MachineData()
        self.excel_processor = ExcelProcessor()
        
        # Initialize UI components
        self.progress_dialog = None
        self.current_file_path = None
        
        self._setup_window()
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
        self._connect_signals()
        self._apply_global_styles()
        
        # Set initial state
        self._update_ui_state()
    
    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Machine Configuration Manager")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        x = (screen.width() - window_geometry.width()) // 2
        y = (screen.height() - window_geometry.height()) // 2
        self.move(x, y)
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Import action
        import_action = QAction("&Import Excel File...", self)
        import_action.setShortcut(QKeySequence.StandardKey.Open)
        import_action.triggered.connect(self._trigger_file_import)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Export actions
        export_json_action = QAction("Export as &JSON...", self)
        export_json_action.triggered.connect(self._export_json)
        file_menu.addAction(export_json_action)
        
        export_csv_action = QAction("Export as &CSV...", self)
        export_csv_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_csv_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_central_widget(self):
        """Create the main central widget layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # File import section
        import_frame = self._create_import_section()
        main_layout.addWidget(import_frame)
        
        # Configuration form section
        config_frame = self._create_configuration_section()
        main_layout.addWidget(config_frame)
        
        # Data display section (main content)
        data_splitter = self._create_data_section()
        main_layout.addWidget(data_splitter, 1)  # Stretch factor
        
        # Action buttons
        button_frame = self._create_action_buttons()
        main_layout.addWidget(button_frame)
    
    def _create_import_section(self):
        """Create file import section"""
        import_frame = ModernFrame("File Import")
        
        # File selector
        self.file_selector = FileSelector(
            title="Select Machine Configuration File",
            file_filter="Excel files (*.xlsx *.xls *.xlsm)",
            allowed_extensions=[".xlsx", ".xls", ".xlsm"]
        )
        
        import_frame.add_widget(self.file_selector)
        
        return import_frame
    
    def _create_configuration_section(self):
        """Create machine configuration form section"""
        config_frame = ModernFrame("Machine Configuration")
        
        # Create horizontal layout for form sections
        form_layout = QHBoxLayout()
        
        # Left column - Machine parameters
        self.machine_form = FormSection("Machine Parameters")
        
        # Machine number input
        self.machine_number_input = ValidatedLineEdit(
            validator_func=lambda x: len(x.strip()) > 0,
            auto_format_func=machine_number_formatter,
            placeholder="Enter machine identifier",
            error_message="Machine number is required"
        )
        self.machine_form.add_input(
            "Machine Number:", self.machine_number_input, required=True
        )
        
        # WPH input
        self.wph_input = ValidatedLineEdit(
            validator_func=create_numeric_validator(min_value=1, max_value=10000),
            placeholder="Enter WPH value",
            error_message="WPH must be a number between 1 and 10000"
        )
        self.machine_form.add_input("WPH:", self.wph_input, required=True)
        
        # Transport type combo
        self.transport_combo = QComboBox()
        self.transport_combo.addItems(["Conveyor", "Indexing", "Continuous", "Manual", "Other"])
        self.transport_combo.setEditable(True)
        self.machine_form.add_input("Transport Type:", self.transport_combo)
        
        form_layout.addWidget(self.machine_form)
        
        # Right column - Summary information
        self.summary_form = FormSection("Configuration Summary")
        
        # Summary labels (read-only)
        self.total_stations_label = ValidatedLineEdit()
        self.total_stations_label.setReadOnly(True)
        self.summary_form.add_input("Total Stations:", self.total_stations_label)
        
        self.total_actuators_label = ValidatedLineEdit()
        self.total_actuators_label.setReadOnly(True)
        self.summary_form.add_input("Total Actuators:", self.total_actuators_label)
        
        self.file_status_label = ValidatedLineEdit()
        self.file_status_label.setReadOnly(True)
        self.summary_form.add_input("File Status:", self.file_status_label)
        
        form_layout.addWidget(self.summary_form)
        
        # Add form layout to frame
        config_frame.content_layout().addLayout(form_layout)
        
        return config_frame
    
    def _create_data_section(self):
        """Create the main data display section with tables"""
        # Create horizontal splitter for side-by-side tables
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Stations
        stations_frame = ModernFrame("Stations")
        
        # Search box for stations
        self.station_search = SearchBox("Search stations...")
        stations_frame.add_widget(self.station_search)
        
        # Station table setup
        self.station_model = StationTableModel()
        self.station_proxy = SearchableTableModel()
        self.station_proxy.setSourceModel(self.station_model)
        
        self.station_table = DataTableView(enable_sorting=True)
        self.station_table.setModel(self.station_proxy)
        stations_frame.add_widget(self.station_table)
        
        splitter.addWidget(stations_frame)
        
        # Right panel - Actuators
        actuators_frame = ModernFrame("Actuators")
        
        # Search box for actuators
        self.actuator_search = SearchBox("Search actuators...")
        actuators_frame.add_widget(self.actuator_search)
        
        # Actuator table setup
        self.actuator_model = ActuatorTableModel()
        self.actuator_proxy = SearchableTableModel()
        self.actuator_proxy.setSourceModel(self.actuator_model)
        
        self.actuator_table = DataTableView(enable_sorting=True)
        self.actuator_table.setModel(self.actuator_proxy)
        actuators_frame.add_widget(self.actuator_table)
        
        splitter.addWidget(actuators_frame)
        
        # Set splitter proportions (60% stations, 40% actuators)
        splitter.setSizes([600, 400])
        
        return splitter
    
    def _create_action_buttons(self):
        """Create action button section"""
        button_frame = ModernFrame()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Status indicator
        self.status_indicator = StatusIndicator()
        self.status_indicator.set_status("info", "Ready to import configuration file")
        button_layout.addWidget(self.status_indicator, 1)
        
        # Action buttons
        self.validate_button = ModernButton("Validate Configuration", style="primary")
        self.validate_button.clicked.connect(self._validate_configuration)
        button_layout.addWidget(self.validate_button)
        
        self.export_button = ModernButton("Export Data", style="secondary")
        self.export_button.clicked.connect(self._export_json)
        button_layout.addWidget(self.export_button)
        
        self.clear_button = ModernButton("Clear All", style="outline")
        self.clear_button.clicked.connect(self._clear_all_data)
        button_layout.addWidget(self.clear_button)
        
        button_frame.content_layout().addLayout(button_layout)
        
        return button_frame
    
    def _create_status_bar(self):
        """Create application status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect component signals to handlers"""
        # File selector signals
        self.file_selector.file_selected.connect(self._on_file_selected)
        self.file_selector.file_cleared.connect(self._on_file_cleared)
        
        # Excel processor signals
        self.excel_processor.progress_updated.connect(self._on_progress_updated)
        self.excel_processor.status_updated.connect(self._on_status_updated)
        self.excel_processor.processing_completed.connect(self._on_processing_completed)
        self.excel_processor.processing_failed.connect(self._on_processing_failed)
        
        # Machine data signals
        self.machine_data.data_changed.connect(self._update_summary_display)
        
        # Form input signals
        self.machine_number_input.value_changed.connect(self._on_machine_number_changed)
        self.wph_input.value_changed.connect(self._on_wph_changed)
        self.transport_combo.currentTextChanged.connect(self._on_transport_type_changed)
        
        # Table selection signals
        self.station_table.selectionModel().currentRowChanged.connect(self._on_station_selected)
        
        # Search signals
        self.station_search.search_changed.connect(self.station_proxy.set_filter_text)
        self.actuator_search.search_changed.connect(self.actuator_proxy.set_filter_text)
    
    def _apply_global_styles(self):
        """Apply global application styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }
            
            QMenuBar::item {
                padding: 8px 12px;
                background: transparent;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #e9ecef;
            }
            
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
            }
        """)
    
    # Event Handlers
    
    def _trigger_file_import(self):
        """Trigger file import via menu"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", 
            "Excel files (*.xlsx *.xls *.xlsm)"
        )
        if file_path:
            self.file_selector.set_file_path(file_path)
    
    @pyqtSlot(str)
    def _on_file_selected(self, file_path):
        """Handle file selection"""
        self.current_file_path = file_path
        self.status_bar.showMessage(f"Processing file: {Path(file_path).name}")
        
        # Show progress dialog
        self.progress_dialog = ProgressDialog(
            self, "Processing Excel File", show_details=True
        )
        self.progress_dialog.cancelled.connect(self.excel_processor.cancel_processing)
        self.progress_dialog.show()
        
        # Start processing
        self.excel_processor.process_file(file_path)
    
    @pyqtSlot()
    def _on_file_cleared(self):
        """Handle file selection cleared"""
        self.current_file_path = None
        self.status_bar.showMessage("Ready")
        self.status_indicator.set_status("info", "Ready to import configuration file")
    
    @pyqtSlot(int)
    def _on_progress_updated(self, percentage):
        """Handle progress updates"""
        if self.progress_dialog:
            self.progress_dialog.show_progress(percentage)
    
    @pyqtSlot(str)
    def _on_status_updated(self, message):
        """Handle status updates"""
        if self.progress_dialog:
            current_progress = self.progress_dialog.progress_bar.value()
            self.progress_dialog.show_progress(current_progress, message)
        self.status_bar.showMessage(message)
    
    @pyqtSlot(object)
    def _on_processing_completed(self, machine_data):
        """Handle successful file processing"""
        if self.progress_dialog:
            self.progress_dialog.complete_progress("File processed successfully!")
        
        # Update machine data
        self.machine_data = machine_data
        self._populate_ui_from_data()
        self._update_ui_state()
        
        self.status_bar.showMessage(f"Successfully loaded {machine_data.get_station_count()} stations")
        self.status_indicator.set_status(
            "success", 
            f"Loaded {machine_data.get_station_count()} stations with {machine_data.get_total_actuator_count()} actuators"
        )
    
    @pyqtSlot(str)
    def _on_processing_failed(self, error_message):
        """Handle processing failure"""
        if self.progress_dialog:
            self.progress_dialog.show_error(error_message)
        
        self.status_bar.showMessage("File processing failed")
        self.status_indicator.set_status("error", f"Processing failed: {error_message}")
        
        # Show error dialog
        QMessageBox.critical(
            self, "Processing Error", 
            f"Failed to process the Excel file:\n\n{error_message}"
        )
    
    @pyqtSlot(str)
    def _on_machine_number_changed(self, value):
        """Handle machine number input changes"""
        if value:
            self.machine_data.machine_num = value
    
    @pyqtSlot(str)
    def _on_wph_changed(self, value):
        """Handle WPH input changes"""
        if value and value.isdigit():
            self.machine_data.wph = float(value)
    
    @pyqtSlot(str)
    def _on_transport_type_changed(self, value):
        """Handle transport type changes"""
        if value:
            self.machine_data.transport_type = value
    
    @pyqtSlot(object, object)
    def _on_station_selected(self, current, previous):
        """Handle station selection changes"""
        if current.isValid():
            # Map proxy index to source index
            source_index = self.station_proxy.mapToSource(current)
            station = self.station_model.get_station(source_index.row())
            
            if station:
                # Update actuator table
                self.actuator_model.set_actuators(station.actuators, station.name)
                self.actuator_table.auto_resize_columns()
                
                # Update status
                self.status_bar.showMessage(
                    f"Selected station {station.nb}: {station.name} ({len(station.actuators)} actuators)"
                )
    
    # UI Update Methods
    
    def _populate_ui_from_data(self):
        """Populate UI controls from machine data"""
        # Update form fields
        if self.machine_data.machine_num:
            self.machine_number_input.setText(self.machine_data.machine_num)
        
        if self.machine_data.wph:
            self.wph_input.setText(str(int(self.machine_data.wph)))
        
        if self.machine_data.transport_type:
            self.transport_combo.setCurrentText(self.machine_data.transport_type)
        
        # Update station table
        stations = list(self.machine_data.stations.values())
        self.station_model.set_stations(stations)
        self.station_table.auto_resize_columns()
        
        # Clear actuator table
        self.actuator_model.set_actuators([], "")
        
        # Update summary
        self._update_summary_display()
    
    def _update_summary_display(self):
        """Update the summary information display"""
        self.total_stations_label.setText(str(self.machine_data.get_station_count()))
        self.total_actuators_label.setText(str(self.machine_data.get_total_actuator_count()))
        
        if self.current_file_path:
            self.file_status_label.setText(f"Loaded: {Path(self.current_file_path).name}")
        else:
            self.file_status_label.setText("No file loaded")
    
    def _update_ui_state(self):
        """Update UI component enabled states"""
        has_data = self.machine_data.get_station_count() > 0
        
        # Enable/disable export buttons
        self.export_button.setEnabled(has_data)
        self.validate_button.setEnabled(has_data)
        self.clear_button.setEnabled(has_data)
    
    # Action Methods
    
    def _validate_configuration(self):
        """Validate the current configuration"""
        # Validate form inputs
        machine_form_valid = self.machine_form.validate_all()
        
        # Check for data completeness
        has_stations = self.machine_data.get_station_count() > 0
        has_actuators = self.machine_data.get_total_actuator_count() > 0
        
        if machine_form_valid and has_stations and has_actuators:
            self.status_indicator.set_status("success", "Configuration is valid and complete")
            QMessageBox.information(
                self, "Validation Successful", 
                "The machine configuration is valid and complete."
            )
        else:
            issues = []
            if not machine_form_valid:
                invalid_fields = self.machine_form.get_invalid_fields()
                issues.append(f"Invalid fields: {', '.join(invalid_fields)}")
            if not has_stations:
                issues.append("No stations loaded")
            if not has_actuators:
                issues.append("No actuators found")
            
            self.status_indicator.set_status("error", "Configuration validation failed")
            QMessageBox.warning(
                self, "Validation Failed", 
                "Configuration validation failed:\n\n" + "\n".join(issues)
            )
    
    def _export_json(self):
        """Export configuration to JSON format"""
        if self.machine_data.get_station_count() == 0:
            QMessageBox.warning(self, "Export Error", "No data to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", "machine_config.json", "JSON files (*.json)"
        )
        
        if file_path:
            try:
                data = self.machine_data.to_dict()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"Exported to {Path(file_path).name}")
                self.status_indicator.set_status("success", "Data exported successfully")
                
                QMessageBox.information(
                    self, "Export Successful", 
                    f"Configuration exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", 
                    f"Failed to export JSON:\n{str(e)}"
                )
    
    def _export_csv(self):
        """Export station data to CSV format"""
        if self.machine_data.get_station_count() == 0:
            QMessageBox.warning(self, "Export Error", "No data to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "stations.csv", "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow([
                        'Station Number', 'Station Name', 'Tag Name', 
                        'Upstream Number', 'Actuator Count', 
                        'Actuator Number', 'Actuator Name', 'Actuator Tag'
                    ])
                    
                    # Write station and actuator data
                    for station in self.machine_data.stations.values():
                        if station.actuators:
                            for actuator in station.actuators:
                                writer.writerow([
                                    station.nb, station.name, station.tag_name,
                                    station.up_num, len(station.actuators),
                                    actuator.act_number, actuator.act_name, actuator.act_tagname
                                ])
                        else:
                            # Station with no actuators
                            writer.writerow([
                                station.nb, station.name, station.tag_name,
                                station.up_num, 0, "", "", ""
                            ])
                
                self.status_bar.showMessage(f"Exported to {Path(file_path).name}")
                self.status_indicator.set_status("success", "Data exported successfully")
                
                QMessageBox.information(
                    self, "Export Successful", 
                    f"Station data exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", 
                    f"Failed to export CSV:\n{str(e)}"
                )
    
    def _clear_all_data(self):
        """Clear all loaded data"""
        reply = QMessageBox.question(
            self, "Clear All Data", 
            "Are you sure you want to clear all loaded data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.machine_data.clear()
            self.station_model.set_stations([])
            self.actuator_model.set_actuators([], "")
            self.file_selector.clear()
            
            # Clear form inputs
            self.machine_number_input.clear()
            self.wph_input.clear()
            self.transport_combo.setCurrentIndex(0)
            
            self._update_ui_state()
            self.status_indicator.set_status("info", "Ready to import configuration file")
            self.status_bar.showMessage("Data cleared")
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Machine Configuration Manager",
            """
            <h3>Machine Configuration Manager</h3>
            <p>A modern PyQt6 application for managing machine configuration data from Excel files.</p>
            
            <p><b>Features:</b></p>
            <ul>
            <li>Excel file processing with threading</li>
            <li>Interactive station and actuator browsing</li>
            <li>Real-time search and filtering</li>
            <li>Data validation and export capabilities</li>
            <li>Modern, responsive user interface</li>
            </ul>
            
            <p><b>Built with:</b> PyQt6, pandas, numpy</p>
            """
        )
