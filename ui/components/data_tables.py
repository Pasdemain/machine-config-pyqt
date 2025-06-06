"""
Advanced Data Table Components

Custom table models and views optimized for machine configuration data.
This module demonstrates proper Model-View architecture in PyQt6.
"""

from typing import List, Optional, Any
from PyQt6.QtWidgets import (
    QTableView, QHeaderView, QAbstractItemView, 
    QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt6.QtCore import (
    QAbstractTableModel, Qt, QModelIndex, pyqtSignal, 
    QVariant, QSortFilterProxyModel
)
from PyQt6.QtGui import QFont, QColor, QPalette

from models.machine_data import Station, Actuator


class StationTableModel(QAbstractTableModel):
    """
    Custom table model for displaying station data.
    
    This model demonstrates proper implementation of QAbstractTableModel
    with support for:
    - Custom data display and formatting
    - Sorting capabilities
    - Selection tracking
    - Data validation
    
    Signals:
        station_selected: Emitted when a station is selected
    """
    
    station_selected = pyqtSignal(str)  # station_number
    
    # Column definitions
    COLUMNS = [
        ('Station #', 'nb'),
        ('Station Name', 'name'),
        ('Tag Name', 'tag_name'),
        ('Upstream #', 'up_num'),
        ('Actuators', 'actuator_count')
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stations: List[Station] = []
        self._selected_station = None
    
    def set_stations(self, stations: List[Station]):
        """
        Update the model with new station data.
        
        Args:
            stations: List of Station objects to display
        """
        self.beginResetModel()
        self._stations = stations
        self.endResetModel()
    
    def get_station(self, row: int) -> Optional[Station]:
        """
        Get station object at specified row.
        
        Args:
            row: Row index
            
        Returns:
            Station object or None if invalid row
        """
        if 0 <= row < len(self._stations):
            return self._stations[row]
        return None
    
    def select_station(self, station_number: str):
        """
        Select a station by number.
        
        Args:
            station_number: Station number to select
        """
        self._selected_station = station_number
        self.station_selected.emit(station_number)
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, self.columnCount()-1))
    
    # QAbstractTableModel Implementation
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of stations"""
        return len(self._stations)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns"""
        return len(self.COLUMNS)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for given index and role"""
        if not index.isValid() or not (0 <= index.row() < len(self._stations)):
            return QVariant()
        
        station = self._stations[index.row()]
        column_name, column_attr = self.COLUMNS[index.column()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            if column_attr == 'actuator_count':
                return len(station.actuators)
            else:
                return getattr(station, column_attr, "")
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Highlight selected station
            if self._selected_station and station.nb == self._selected_station:
                return QColor("#e3f2fd")
        
        elif role == Qt.ItemDataRole.FontRole:
            # Bold font for selected station
            if self._selected_station and station.nb == self._selected_station:
                font = QFont()
                font.setBold(True)
                return font
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Center align station number and actuator count
            if column_attr in ['nb', 'actuator_count']:
                return Qt.AlignmentFlag.AlignCenter
        
        elif role == Qt.ItemDataRole.ToolTipRole:
            # Provide detailed tooltip
            return (f"Station {station.nb}: {station.name}\n"
                   f"Tag: {station.tag_name}\n"
                   f"Upstream: {station.up_num}\n"
                   f"Actuators: {len(station.actuators)}")
        
        return QVariant()
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return header data"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section][0]
        
        elif role == Qt.ItemDataRole.FontRole and orientation == Qt.Orientation.Horizontal:
            font = QFont()
            font.setBold(True)
            return font
        
        return QVariant()
    
    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        """Sort the model by column"""
        if 0 <= column < len(self.COLUMNS):
            self.layoutAboutToBeChanged.emit()
            
            column_name, column_attr = self.COLUMNS[column]
            reverse = (order == Qt.SortOrder.DescendingOrder)
            
            if column_attr == 'actuator_count':
                self._stations.sort(key=lambda s: len(s.actuators), reverse=reverse)
            else:
                self._stations.sort(key=lambda s: getattr(s, column_attr, ""), reverse=reverse)
            
            self.layoutChanged.emit()


class ActuatorTableModel(QAbstractTableModel):
    """
    Custom table model for displaying actuator data.
    
    Features:
    - Display actuators for selected station
    - Custom formatting and validation
    - Search/filter capabilities
    - Export functionality
    """
    
    # Column definitions
    COLUMNS = [
        ('Actuator #', 'act_number'),
        ('Actuator Name', 'act_name'),
        ('Tag Name', 'act_tagname'),
        ('Total Track', 'total_track')
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._actuators: List[Actuator] = []
        self._station_name = ""
    
    def set_actuators(self, actuators: List[Actuator], station_name: str = ""):
        """
        Update the model with new actuator data.
        
        Args:
            actuators: List of Actuator objects to display
            station_name: Name of the station these actuators belong to
        """
        self.beginResetModel()
        self._actuators = actuators
        self._station_name = station_name
        self.endResetModel()
    
    def get_actuator(self, row: int) -> Optional[Actuator]:
        """
        Get actuator object at specified row.
        
        Args:
            row: Row index
            
        Returns:
            Actuator object or None if invalid row
        """
        if 0 <= row < len(self._actuators):
            return self._actuators[row]
        return None
    
    # QAbstractTableModel Implementation
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of actuators"""
        return len(self._actuators)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns"""
        return len(self.COLUMNS)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for given index and role"""
        if not index.isValid() or not (0 <= index.row() < len(self._actuators)):
            return QVariant()
        
        actuator = self._actuators[index.row()]
        column_name, column_attr = self.COLUMNS[index.column()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            value = getattr(actuator, column_attr, "")
            if column_attr == 'total_track' and value:
                return f"{value:.1f}"
            return value or ""
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Center align actuator number and total track
            if column_attr in ['act_number', 'total_track']:
                return Qt.AlignmentFlag.AlignCenter
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Alternate row colors for better readability
            if index.row() % 2 == 0:
                return QColor("#f8f9fa")
        
        elif role == Qt.ItemDataRole.ToolTipRole:
            # Provide detailed tooltip
            return (f"Actuator {actuator.act_number}: {actuator.act_name}\n"
                   f"Tag: {actuator.act_tagname or 'N/A'}\n"
                   f"Tracks: {actuator.total_track}")
        
        return QVariant()
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return header data"""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section][0]
        
        elif role == Qt.ItemDataRole.FontRole and orientation == Qt.Orientation.Horizontal:
            font = QFont()
            font.setBold(True)
            return font
        
        return QVariant()
    
    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        """Sort the model by column"""
        if 0 <= column < len(self.COLUMNS):
            self.layoutAboutToBeChanged.emit()
            
            column_name, column_attr = self.COLUMNS[column]
            reverse = (order == Qt.SortOrder.DescendingOrder)
            
            if column_attr == 'total_track':
                self._actuators.sort(key=lambda a: a.total_track or 0, reverse=reverse)
            else:
                self._actuators.sort(key=lambda a: getattr(a, column_attr, ""), reverse=reverse)
            
            self.layoutChanged.emit()


class DataTableView(QTableView):
    """
    Enhanced table view with modern styling and optimized performance.
    
    Features:
    - Responsive column sizing
    - Modern visual styling
    - Optimized scrolling and rendering
    - Context menu support
    - Export capabilities
    
    This component demonstrates advanced QTableView customization
    and performance optimization techniques.
    """
    
    def __init__(self, parent=None, enable_sorting=True, alternate_colors=True):
        super().__init__(parent)
        
        self.enable_sorting = enable_sorting
        self.alternate_colors = alternate_colors
        
        self._setup_view()
        self._apply_styling()
        self._optimize_performance()
    
    def _setup_view(self):
        """Configure table view settings"""
        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Sorting
        if self.enable_sorting:
            self.setSortingEnabled(True)
        
        # Alternating row colors
        if self.alternate_colors:
            self.setAlternatingRowColors(True)
        
        # Grid and headers
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        
        # Header configuration
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.verticalHeader().setVisible(False)
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(32)
    
    def _apply_styling(self):
        """Apply modern table styling"""
        self.setStyleSheet("""
            QTableView {
                gridline-color: #e9ecef;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            
            QTableView::item {
                padding: 8px;
                border: none;
            }
            
            QTableView::item:selected {
                background-color: #007bff;
                color: white;
            }
            
            QTableView::item:hover {
                background-color: #e3f2fd;
            }
            
            QHeaderView::section {
                background-color: #f1f3f4;
                color: #212529;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
                font-weight: bold;
            }
            
            QHeaderView::section:hover {
                background-color: #e9ecef;
            }
            
            QHeaderView::section:pressed {
                background-color: #ced4da;
            }
            
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #ced4da;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
            
            QScrollBar:horizontal {
                background-color: #f8f9fa;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #ced4da;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #adb5bd;
            }
        """)
    
    def _optimize_performance(self):
        """Apply performance optimizations for large datasets"""
        # Enable uniform row heights for better performance
        self.setUniformRowHeights(True)
        
        # Optimize scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    
    def auto_resize_columns(self):
        """
        Automatically resize columns to optimal width.
        
        This method balances content visibility with table width,
        demonstrating proper column sizing strategies.
        """
        # Resize columns to content
        self.resizeColumnsToContents()
        
        # Ensure minimum column widths
        header = self.horizontalHeader()
        for i in range(header.count()):
            current_width = header.sectionSize(i)
            min_width = 100  # Minimum column width
            if current_width < min_width:
                header.resizeSection(i, min_width)
        
        # Limit maximum column width to prevent overly wide columns
        max_width = self.width() // 3  # Max 1/3 of table width per column
        for i in range(header.count() - 1):  # Exclude last column (stretches)
            current_width = header.sectionSize(i)
            if current_width > max_width:
                header.resizeSection(i, max_width)
    
    def setModel(self, model):
        """Override setModel to auto-resize columns when model changes"""
        super().setModel(model)
        if model and model.rowCount() > 0:
            # Delay auto-resize to ensure data is loaded
            self.resizeColumnsToContents()


class SearchableTableModel(QSortFilterProxyModel):
    """
    Proxy model that adds search/filtering capabilities to data tables.
    
    This model wraps any QAbstractTableModel and provides:
    - Text-based filtering across all columns
    - Case-insensitive search
    - Real-time filtering as user types
    - Multiple search terms support
    
    Usage:
        base_model = StationTableModel()
        searchable_model = SearchableTableModel()
        searchable_model.setSourceModel(base_model)
        table_view.setModel(searchable_model)
        
        # Filter data
        searchable_model.set_filter_text("station 1")
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ""
        
        # Configure filtering
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterKeyColumn(-1)  # Filter all columns
    
    def set_filter_text(self, text: str):
        """
        Set the filter text for searching.
        
        Args:
            text: Search text (supports multiple terms separated by spaces)
        """
        self._filter_text = text.strip()
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Determine if a row should be included in the filtered results.
        
        Args:
            source_row: Row index in source model
            source_parent: Parent index in source model
            
        Returns:
            True if row should be included, False otherwise
        """
        if not self._filter_text:
            return True
        
        # Split search text into terms
        search_terms = self._filter_text.lower().split()
        if not search_terms:
            return True
        
        # Get source model
        source_model = self.sourceModel()
        if not source_model:
            return True
        
        # Collect all text from this row
        row_text = []
        for column in range(source_model.columnCount()):
            index = source_model.index(source_row, column, source_parent)
            data = source_model.data(index, Qt.ItemDataRole.DisplayRole)
            if data:
                row_text.append(str(data).lower())
        
        combined_text = " ".join(row_text)
        
        # Check if all search terms are found in the row
        return all(term in combined_text for term in search_terms)


# Template Usage Example:
"""
Here's how to use the data table components:

class MachineConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create models
        self.station_model = StationTableModel()
        self.actuator_model = ActuatorTableModel()
        
        # Create searchable proxy models
        self.station_proxy = SearchableTableModel()
        self.station_proxy.setSourceModel(self.station_model)
        
        self.actuator_proxy = SearchableTableModel()
        self.actuator_proxy.setSourceModel(self.actuator_model)
        
        # Create views
        self.station_table = DataTableView()
        self.station_table.setModel(self.station_proxy)
        
        self.actuator_table = DataTableView()
        self.actuator_table.setModel(self.actuator_proxy)
        
        # Connect signals
        self.station_table.selectionModel().currentRowChanged.connect(self.on_station_selected)
        self.station_model.station_selected.connect(self.load_actuators)
    
    def load_stations(self, machine_data):
        stations = list(machine_data.stations.values())
        self.station_model.set_stations(stations)
        self.station_table.auto_resize_columns()
    
    def on_station_selected(self, current, previous):
        if current.isValid():
            # Get station from proxy model
            source_index = self.station_proxy.mapToSource(current)
            station = self.station_model.get_station(source_index.row())
            if station:
                self.station_model.select_station(station.nb)
    
    def load_actuators(self, station_number):
        station = self.machine_data.get_station(station_number)
        if station:
            self.actuator_model.set_actuators(station.actuators, station.name)
            self.actuator_table.auto_resize_columns()
"""
