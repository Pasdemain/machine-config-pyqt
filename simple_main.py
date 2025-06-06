#!/usr/bin/env python3
"""
Simple Machine Configuration PyQt6 Interface
A direct PyQt6 conversion of the original Tkinter application
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class ExcelProcessor(QThread):
    """Simple Excel processor thread"""
    progress_updated = pyqtSignal(int, str)
    processing_completed = pyqtSignal(dict)
    processing_failed = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            self.progress_updated.emit(10, "Opening Excel file...")
            
            # Extract info like original code
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
                
                # Process actuators (same logic as original)
                for _, row in df.iloc[7:-1].iterrows():
                    if not pd.isna(row.iloc[0]):
                        act_number = str(int(row.iloc[0])).zfill(2)
                        act_name = row.iloc[1]
                        act_total_track = float(row.iloc[2]) if not pd.isna(row.iloc[2]) else 1.0
                        act_up_numbering = row.iloc[3]
                        act_tagname = row.iloc[3]
                        
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
                                })
                
                stations[station_number] = station
            
            dict_info['stations'] = stations
            
            self.progress_updated.emit(100, "Processing completed!")
            self.processing_completed.emit(dict_info)
            
        except Exception as e:
            self.processing_failed.emit(str(e))


class MachineConfigWindow(QMainWindow):
    """Simple machine configuration window - PyQt6 version of original"""
    
    def __init__(self):
        super().__init__()
        self.machine_data = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Machine Configuration Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Import section
        import_layout = QHBoxLayout()
        import_layout.addWidget(QLabel("Import backbone:"))
        
        self.file_label = QLabel("No file selected")
        import_layout.addWidget(self.file_label)
        
        self.import_button = QPushButton("Import backbone")
        self.import_button.clicked.connect(self.import_backbone)
        import_layout.addWidget(self.import_button)
        
        layout.addLayout(import_layout)
        
        # Machine section
        layout.addWidget(QLabel("Machine Section"))
        
        machine_layout = QHBoxLayout()
        machine_layout.addWidget(QLabel("Machine num:"))
        self.machine_num_entry = QLineEdit()
        machine_layout.addWidget(self.machine_num_entry)
        layout.addLayout(machine_layout)
        
        wph_layout = QHBoxLayout()
        wph_layout.addWidget(QLabel("WPH:"))
        self.wph_entry = QLineEdit()
        wph_layout.addWidget(self.wph_entry)
        layout.addLayout(wph_layout)
        
        nest_layout = QHBoxLayout()
        nest_layout.addWidget(QLabel("Nest by WPH:"))
        self.nest_wph_entry = QLineEdit()
        nest_layout.addWidget(self.nest_wph_entry)
        layout.addLayout(nest_layout)
        
        transport_layout = QHBoxLayout()
        transport_layout.addWidget(QLabel("Transport type:"))
        self.transport_entry = QLineEdit()
        transport_layout.addWidget(self.transport_entry)
        layout.addLayout(transport_layout)
        
        # Tables section
        tables_layout = QHBoxLayout()
        
        # Stations tree
        stations_layout = QVBoxLayout()
        stations_layout.addWidget(QLabel("Stations"))
        self.stations_tree = QTreeWidget()
        self.stations_tree.setHeaderLabels(['nb', 'name', 'tag_name', 'up_num'])
        self.stations_tree.itemClicked.connect(self.on_station_selected)
        stations_layout.addWidget(self.stations_tree)
        tables_layout.addLayout(stations_layout)
        
        # Actuators tree
        actuators_layout = QVBoxLayout()
        actuators_layout.addWidget(QLabel("Actuators"))
        self.actuators_tree = QTreeWidget()
        self.actuators_tree.setHeaderLabels(['act_number', 'act_name'])
        actuators_layout.addWidget(self.actuators_tree)
        tables_layout.addLayout(actuators_layout)
        
        layout.addLayout(tables_layout)
        
        # Validate button
        self.validate_button = QPushButton("Validate")
        layout.addWidget(self.validate_button)
    
    def import_backbone(self):
        """Import Excel backbone file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select backbone file", "",
            "Excel files (*.xlsx *.xls *.xlsm)"
        )
        
        if file_path:
            self.file_label.setText(Path(file_path).name)
            
            # Show progress dialog
            self.progress_dialog = QProgressDialog("Processing file...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
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
        QMessageBox.information(self, "Success", "File processed successfully!")
    
    def on_processing_failed(self, error_message):
        """Handle processing failure"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        QMessageBox.critical(self, "Error", f"Processing failed: {error_message}")
    
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
    
    def on_station_selected(self, item):
        """Handle station selection"""
        station = item.data(0, Qt.ItemDataRole.UserRole)
        if station:
            # Update actuators tree
            self.actuators_tree.clear()
            for actuator in station['actuators']:
                act_item = QTreeWidgetItem([
                    actuator['act_number'],
                    actuator['act_name']
                ])
                self.actuators_tree.addTopLevelItem(act_item)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Machine Configuration Manager")
    
    window = MachineConfigWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
