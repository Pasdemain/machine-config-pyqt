"""
Excel File Processing Module

Handles reading and parsing Excel files containing machine configuration data.
This module demonstrates proper file processing with error handling and progress tracking.
"""

import pandas as pd
import numpy as np
from typing import Optional, Callable
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from .machine_data import MachineData, Station, Actuator


class ExcelProcessorWorker(QThread):
    """
    Worker thread for processing Excel files without blocking the UI.
    
    This demonstrates proper threading in PyQt6 applications for
    long-running operations like file processing.
    
    Signals:
        progress_updated: Progress percentage (0-100)
        status_updated: Current operation status message
        processing_completed: Processing finished with MachineData result
        processing_failed: Processing failed with error message
    """
    
    progress_updated = pyqtSignal(int)  # percentage
    status_updated = pyqtSignal(str)    # status message
    processing_completed = pyqtSignal(object)  # MachineData
    processing_failed = pyqtSignal(str)        # error message
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self._is_cancelled = False
    
    def cancel(self):
        """Cancel the processing operation"""
        self._is_cancelled = True
    
    def run(self):
        """Main processing method running in separate thread"""
        try:
            machine_data = self._process_excel_file(self.file_path)
            if not self._is_cancelled:
                self.processing_completed.emit(machine_data)
        except Exception as e:
            if not self._is_cancelled:
                self.processing_failed.emit(str(e))
    
    def _process_excel_file(self, file_path: str) -> MachineData:
        """
        Process Excel file and extract machine configuration data.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            MachineData: Parsed machine configuration
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
            Exception: For other processing errors
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.status_updated.emit("Opening Excel file...")
        self.progress_updated.emit(10)
        
        if self._is_cancelled:
            return None
        
        try:
            # Load Excel file
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            self.status_updated.emit("Reading machine information...")
            self.progress_updated.emit(20)
            
            # Create machine data container
            machine_data = MachineData()
            
            # Extract machine number from Info sheet
            if 'Info' not in sheet_names:
                raise ValueError("Missing 'Info' sheet in Excel file")
            
            info_df = pd.read_excel(file_path, sheet_name='Info')
            if info_df.shape[0] < 2 or info_df.shape[1] < 2:
                raise ValueError("Invalid format in 'Info' sheet")
            
            machine_data.machine_num = str(info_df.iloc[1, 1])
            
            # Find station sheets (starting with 'ST')
            station_sheets = [name for name in sheet_names if name.startswith('ST')]
            
            if not station_sheets:
                raise ValueError("No station sheets found (sheets starting with 'ST')")
            
            self.status_updated.emit(f"Processing {len(station_sheets)} stations...")
            
            # Process each station sheet
            for i, sheet_name in enumerate(station_sheets):
                if self._is_cancelled:
                    return None
                
                progress = 30 + int((i / len(station_sheets)) * 60)
                self.progress_updated.emit(progress)
                self.status_updated.emit(f"Processing station: {sheet_name}")
                
                station = self._process_station_sheet(file_path, sheet_name)
                machine_data.add_station(station)
            
            self.status_updated.emit("Processing completed successfully")
            self.progress_updated.emit(100)
            
            return machine_data
            
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _process_station_sheet(self, file_path: Path, sheet_name: str) -> Station:
        """
        Process a single station sheet and extract station data.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of the station sheet
            
        Returns:
            Station: Processed station data
        """
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        if df.shape[0] < 8 or df.shape[1] < 4:
            raise ValueError(f"Invalid format in sheet '{sheet_name}'")
        
        # Extract station information
        station_number = str(sheet_name[2:]).zfill(2)
        station_name = str(df.iloc[0, 1]) if pd.notna(df.iloc[0, 1]) else f"Station {station_number}"
        tag_name = str(df.iloc[0, 1]) if pd.notna(df.iloc[0, 1]) else station_name
        up_num = str(df.iloc[3, 1]) if pd.notna(df.iloc[3, 1]) else ""
        
        station = Station(
            nb=station_number,
            name=station_name,
            tag_name=tag_name,
            up_num=up_num
        )
        
        # Process actuators (starting from row 8, excluding last row)
        actuator_rows = df.iloc[7:-1] if len(df) > 8 else df.iloc[7:]
        
        for _, row in actuator_rows.iterrows():
            if self._is_cancelled:
                return station
            
            # Skip empty rows
            if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                continue
            
            try:
                act_number = str(int(float(row.iloc[0]))).zfill(2)
                act_name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else f"Actuator {act_number}"
                act_total_track = float(row.iloc[2]) if pd.notna(row.iloc[2]) else 1.0
                act_up_numbering = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
                
                # Handle single vs multi-track actuators
                if act_total_track <= 1:
                    # Single track actuator
                    actuator = Actuator(
                        act_number=act_number,
                        act_name=act_name,
                        act_tagname=act_up_numbering,
                        total_track=act_total_track
                    )
                    station.add_actuator(actuator)
                else:
                    # Multi-track actuator - split by semicolon
                    tracks = str(act_up_numbering).split(';')
                    for track in tracks:
                        track = track.strip()
                        if track:  # Skip empty tracks
                            actuator = Actuator(
                                act_number=f"{track}{act_number}",
                                act_name=act_name,
                                act_tagname=track,
                                total_track=1.0  # Each split track is considered single
                            )
                            station.add_actuator(actuator)
                            
            except (ValueError, IndexError) as e:
                # Log warning but continue processing
                print(f"Warning: Skipping invalid actuator row in {sheet_name}: {e}")
                continue
        
        return station


class ExcelProcessor(QObject):
    """
    Main Excel processor class that coordinates file processing.
    
    This class provides a high-level interface for processing Excel files
    while managing threading and progress updates.
    
    Usage:
        processor = ExcelProcessor()
        processor.progress_updated.connect(progress_bar.setValue)
        processor.status_updated.connect(status_label.setText)
        processor.processing_completed.connect(self.handle_data)
        processor.process_file("path/to/file.xlsx")
    """
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    processing_completed = pyqtSignal(object)  # MachineData
    processing_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._worker = None
    
    def process_file(self, file_path: str):
        """
        Start processing an Excel file in a separate thread.
        
        Args:
            file_path: Path to the Excel file to process
        """
        if self._worker and self._worker.isRunning():
            self.cancel_processing()
        
        self._worker = ExcelProcessorWorker(file_path)
        
        # Connect worker signals
        self._worker.progress_updated.connect(self.progress_updated)
        self._worker.status_updated.connect(self.status_updated)
        self._worker.processing_completed.connect(self._on_processing_completed)
        self._worker.processing_failed.connect(self._on_processing_failed)
        
        # Start processing
        self._worker.start()
    
    def cancel_processing(self):
        """Cancel the current processing operation"""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.quit()
            self._worker.wait()
    
    def _on_processing_completed(self, machine_data: MachineData):
        """Handle successful processing completion"""
        self.processing_completed.emit(machine_data)
        self._cleanup_worker()
    
    def _on_processing_failed(self, error_message: str):
        """Handle processing failure"""
        self.processing_failed.emit(error_message)
        self._cleanup_worker()
    
    def _cleanup_worker(self):
        """Clean up worker thread resources"""
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
