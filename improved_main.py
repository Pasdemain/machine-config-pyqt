#!/usr/bin/env python3
"""
Improved Machine Configuration PyQt6 Interface
Enhanced version with better layout and proportions
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QProgressDialog, QGroupBox, QGridLayout,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class ExcelProcessor(QThread):
    """Excel processor thread"""
    progress_updated = pyqtSignal(int, str)
    processing_completed = pyqtSignal(dict)
    processing_failed = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress_updated.emit(10, "Opening Excel file...")
            
            xls = pd.ExcelFile(self.file_path)
            dict_info = {}
            
            self.progress_updated.emit(20, "Reading machine information...")
            
            # Get machine number from Info sheet
            df = pd.read_excel(self.file_path, sheet_name='Info')
            dict_info['machine_num'] = df.iloc[1, 1]
            stations = {}
            
            # Process station sheets
            station_sheets = [name for name in xls.sheet_names if name.startswith('ST')]
            
            for i, sheet_name in enumerate(station_sheets):
                progress = 30 + int((i / len(station_sheets)) * 60)
                self.progress_updated.emit(progress, f"Processing {sheet_name}...")
                
                station_number = str(sheet_name[2:]).zfill(2)
                station = {}
                
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                station['nb'] = station_number
                station['name'] = df.iloc[0, 1]
                station['tag_name'] = df.iloc[0, 1]
                station['up_num'] = df.iloc[3, 1]
                station['actuators'] = []
                
                # Skip "Free" stations
                if str(station['name']).lower() == 'free':
                    continue
                
                # Process actuators
                for _, row in df.iloc[7:-1].iterrows():
                    if not pd.isna(row.iloc[0]):
                        act_number = str(int(row.iloc[0])).zfill(2)
                        act_name = row.iloc[1]
                        act_total_track = float(row.iloc[2]) if not pd.isna(row.iloc[2]) else 1.0
                        act_up_numbering = row.iloc[3]
                        
                        # Handle tagname properly - check for NaN values
                        if pd.isna(row.iloc[3]):
                            act_tagname = ""
                        else:
                            act_tagname = str(row.iloc[3])
                        
                        if act_total_track <= 1:
                            station['actuators'].append({
                                "act_number": act_number,
                                "act_name": act_name,
                                "act_tagname": act_tagname,
                            })
                        else:
                            tracks = str(act_up_numbering).split(';')
                            for t in tracks:
                                station['actuators'].append({
                                    "act_number": t + act_number,
                                    "act_name": act_name,
                                    "act_tagname": t,  # Use track as tagname for multi-track
                                })
                
                stations[station_number] = station
            
            dict_info['stations'] = stations
            
            self.progress_updated.emit(100, "Processing completed!")
            self.processing_completed.emit(dict_info)
            
        except Exception as e:
            self.processing_failed.emit(str(e))


class MachineConfigWindow(QMainWindow):
    """Improved machine configuration window with better layout"""
    
    def __init__(self):
        super().__init__()
        self.machine_data = {}
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Setup the user interface with improved layout"""
        self.setWindowTitle("Machine Configuration Manager")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Import section (in a group box)
        import_group = QGroupBox("File Import")
        import_layout = QHBoxLayout(import_group)
        
        import_layout.addWidget(QLabel("Backbone File:"))
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666; font-style: italic;")
        import_layout.addWidget(self.file_label, 1)  # Stretch factor
        
        self.import_button = QPushButton("Browse...")
        self.import_button.setFixedWidth(100)
        self.import_button.clicked.connect(self.import_backbone)
        import_layout.addWidget(self.import_button)
        
        main_layout.addWidget(import_group)
        
        # Machine configuration section (in a group box with grid layout)
        machine_group = QGroupBox("Machine Configuration")
        machine_layout = QGridLayout(machine_group)
        
        # Row 0
        machine_layout.addWidget(QLabel("Machine Number:"), 0, 0)
        self.machine_num_entry = QLineEdit()
        self.machine_num_entry.setFixedWidth(150)
        machine_layout.addWidget(self.machine_num_entry, 0, 1)
        
        machine_layout.addWidget(QLabel("WPH:"), 0, 2)
        self.wph_entry = QLineEdit()
        self.wph_entry.setFixedWidth(150)
        machine_layout.addWidget(self.wph_entry, 0, 3)
        
        # Row 1
        machine_layout.addWidget(QLabel("Nest by WPH:"), 1, 0)
        self.nest_wph_entry = QLineEdit()
        self.nest_wph_entry.setFixedWidth(150)
        machine_layout.addWidget(self.nest_wph_entry, 1, 1)
        
        machine_layout.addWidget(QLabel("Transport Type:"), 1, 2)
        self.transport_entry = QLineEdit()
        self.transport_entry.setFixedWidth(150)
        machine_layout.addWidget(self.transport_entry, 1, 3)
        
        # Add stretch to push everything to the left
        machine_layout.setColumnStretch(4, 1)
        
        main_layout.addWidget(machine_group)
        
        # Data section with splitter
        data_group = QGroupBox("Configuration Data")
        data_layout = QVBoxLayout(data_group)
        
        # Create splitter for resizable tables
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Stations section
        stations_widget = QWidget()
        stations_layout = QVBoxLayout(stations_widget)
        stations_layout.setContentsMargins(5, 5, 5, 5)
        
        stations_label = QLabel("Stations")
        stations_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        stations_layout.addWidget(stations_label)
        
        self.stations_tree = QTreeWidget()
        self.stations_tree.setHeaderLabels(['#', 'Station Name', 'Tag Name', 'Upstream'])
        self.stations_tree.itemClicked.connect(self.on_station_selected)
        
        # Set column widths
        self.stations_tree.setColumnWidth(0, 40)
        self.stations_tree.setColumnWidth(1, 150)
        self.stations_tree.setColumnWidth(2, 150)
        self.stations_tree.setColumnWidth(3, 80)
        
        stations_layout.addWidget(self.stations_tree)
        splitter.addWidget(stations_widget)
        
        # Actuators section
        actuators_widget = QWidget()
        actuators_layout = QVBoxLayout(actuators_widget)
        actuators_layout.setContentsMargins(5, 5, 5, 5)
        
        actuators_label = QLabel("Actuators")
        actuators_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        actuators_layout.addWidget(actuators_label)
        
        self.actuators_tree = QTreeWidget()
        # Added the missing "Tag Name" column
        self.actuators_tree.setHeaderLabels(['Actuator #', 'Actuator Name', 'Tag Name'])
        
        # Set column widths for the new 3-column layout
        self.actuators_tree.setColumnWidth(0, 100)
        self.actuators_tree.setColumnWidth(1, 200)
        self.actuators_tree.setColumnWidth(2, 150)
        
        actuators_layout.addWidget(self.actuators_tree)
        splitter.addWidget(actuators_widget)
        
        # Set splitter proportions (60% stations, 40% actuators)
        splitter.setSizes([600, 400])
        
        data_layout.addWidget(splitter)
        main_layout.addWidget(data_group, 1)  # Give this section stretch
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right
        
        self.validate_button = QPushButton("Validate Configuration")
        self.validate_button.setFixedWidth(180)
        button_layout.addWidget(self.validate_button)
        
        main_layout.addLayout(button_layout)
    
    def apply_styles(self):
        """Apply modern styling to the interface"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
            
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            
            QTreeWidget::item:hover {
                background-color: #e8f5e8;
            }
            
            QLabel {
                color: #333;
            }
            
            QSplitter::handle {
                background-color: #ddd;
                width: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #4CAF50;
            }
        """)
    
    def import_backbone(self):
        """Import Excel backbone file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select backbone file", "",
            "Excel files (*.xlsx *.xls *.xlsm)"
        )
        
        if file_path:
            self.file_label.setText(Path(file_path).name)
            self.file_label.setStyleSheet("color: #333; font-weight: bold;")
            
            # Show progress dialog
            self.progress_dialog = QProgressDialog("Processing file...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setWindowTitle("Loading")
            self.progress_dialog.show()
            
            # Start processing
            self.processor = ExcelProcessor(file_path)
            self.processor.progress_updated.connect(self.update_progress)
            self.processor.processing_completed.connect(self.on_processing_completed)
            self.processor.processing_failed.connect(self.on_processing_failed)
            self.processor.start()
    
    def update_progress(self, value, message):
        """Update progress dialog"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(message)
    
    def on_processing_completed(self, machine_data):
        """Handle successful processing"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        self.machine_data = machine_data
        self.update_info()
        
        # Show success message with statistics
        station_count = len(machine_data.get('stations', {}))
        total_actuators = sum(len(station.get('actuators', [])) 
                            for station in machine_data.get('stations', {}).values())
        
        QMessageBox.information(
            self, "Import Successful", 
            f"File processed successfully!\n\n"
            f"• Stations loaded: {station_count}\n"
            f"• Total actuators: {total_actuators}\n"
            f"• Free stations skipped automatically"
        )
    
    def on_processing_failed(self, error_message):
        """Handle processing failure"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        QMessageBox.critical(self, "Import Error", f"Processing failed:\n\n{error_message}")
    
    def update_info(self):
        """Update UI with machine data"""
        # Update machine number
        if 'machine_num' in self.machine_data:
            self.machine_num_entry.setText(str(self.machine_data['machine_num']))
        
        # Update stations tree
        self.stations_tree.clear()
        if 'stations' in self.machine_data:
            for station_key, station in self.machine_data['stations'].items():
                item = QTreeWidgetItem([
                    station['nb'],
                    station['name'],
                    station['tag_name'],
                    str(station['up_num'])
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, station)
                self.stations_tree.addTopLevelItem(item)
        
        # Auto-resize columns
        for i in range(self.stations_tree.columnCount()):
            self.stations_tree.resizeColumnToContents(i)
    
    def on_station_selected(self, item):
        """Handle station selection"""
        station = item.data(0, Qt.ItemDataRole.UserRole)
        if station:
            # Update actuators tree with the new 3-column layout
            self.actuators_tree.clear()
            for actuator in station['actuators']:
                # Convert all values to strings and handle NaN/None values
                tag_name = actuator.get('act_tagname', '')
                if pd.isna(tag_name) or tag_name is None:
                    tag_name = ''
                else:
                    tag_name = str(tag_name)
                
                act_item = QTreeWidgetItem([
                    str(actuator['act_number']),
                    str(actuator['act_name']),
                    tag_name
                ])
                self.actuators_tree.addTopLevelItem(act_item)
            
            # Auto-resize columns
            for i in range(self.actuators_tree.columnCount()):
                self.actuators_tree.resizeColumnToContents(i)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Machine Configuration Manager")
    
    window = MachineConfigWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
