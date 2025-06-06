"""
Machine Configuration Data Models

Well-structured data classes for managing machine, station, and actuator information.
This module demonstrates proper data modeling with PyQt6 integration.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class Actuator:
    """
    Represents an actuator in a station.
    
    Attributes:
        act_number: Unique actuator identifier
        act_name: Human-readable actuator name
        act_tagname: Optional tag name for industrial systems
        total_track: Number of tracks (for multi-track actuators)
    """
    act_number: str
    act_name: str
    act_tagname: Optional[str] = None
    total_track: float = 1.0
    
    def __post_init__(self):
        """Validate and format actuator data after initialization"""
        # Ensure act_number is zero-padded to 2 digits
        if self.act_number.isdigit():
            self.act_number = self.act_number.zfill(2)


@dataclass
class Station:
    """
    Represents a station containing multiple actuators.
    
    Attributes:
        nb: Station number (zero-padded)
        name: Station name
        tag_name: Tag name for industrial systems
        up_num: Upstream numbering
        actuators: List of actuators in this station
    """
    nb: str
    name: str
    tag_name: str
    up_num: str
    actuators: List[Actuator] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and format station data after initialization"""
        # Ensure station number is zero-padded to 2 digits
        if self.nb.isdigit():
            self.nb = self.nb.zfill(2)
    
    def add_actuator(self, actuator: Actuator):
        """Add an actuator to this station"""
        self.actuators.append(actuator)
    
    def get_actuator_count(self) -> int:
        """Get the total number of actuators in this station"""
        return len(self.actuators)


class MachineData(QObject):
    """
    Main data container for machine configuration.
    
    This class manages the complete machine configuration including
    machine-level parameters and all stations with their actuators.
    
    Signals:
        data_changed: Emitted when machine data is updated
        station_added: Emitted when a new station is added
        station_removed: Emitted when a station is removed
    """
    
    # PyQt signals for reactive UI updates
    data_changed = pyqtSignal()
    station_added = pyqtSignal(str)  # station_number
    station_removed = pyqtSignal(str)  # station_number
    
    def __init__(self):
        super().__init__()
        self._machine_num: Optional[str] = None
        self._wph: Optional[float] = None
        self._nest_wph: Optional[float] = None
        self._transport_type: Optional[str] = None
        self._stations: Dict[str, Station] = {}
    
    # Properties with getters and setters for validation
    @property
    def machine_num(self) -> Optional[str]:
        return self._machine_num
    
    @machine_num.setter
    def machine_num(self, value: Optional[str]):
        if self._machine_num != value:
            self._machine_num = value
            self.data_changed.emit()
    
    @property
    def wph(self) -> Optional[float]:
        return self._wph
    
    @wph.setter
    def wph(self, value: Optional[float]):
        if self._wph != value:
            self._wph = value
            self.data_changed.emit()
    
    @property
    def nest_wph(self) -> Optional[float]:
        return self._nest_wph
    
    @nest_wph.setter
    def nest_wph(self, value: Optional[float]):
        if self._nest_wph != value:
            self._nest_wph = value
            self.data_changed.emit()
    
    @property
    def transport_type(self) -> Optional[str]:
        return self._transport_type
    
    @transport_type.setter
    def transport_type(self, value: Optional[str]):
        if self._transport_type != value:
            self._transport_type = value
            self.data_changed.emit()
    
    @property
    def stations(self) -> Dict[str, Station]:
        """Get read-only access to stations"""
        return self._stations.copy()
    
    def add_station(self, station: Station):
        """Add a station to the machine configuration"""
        self._stations[station.nb] = station
        self.station_added.emit(station.nb)
        self.data_changed.emit()
    
    def remove_station(self, station_nb: str):
        """Remove a station from the machine configuration"""
        if station_nb in self._stations:
            del self._stations[station_nb]
            self.station_removed.emit(station_nb)
            self.data_changed.emit()
    
    def get_station(self, station_nb: str) -> Optional[Station]:
        """Get a specific station by number"""
        return self._stations.get(station_nb)
    
    def get_station_count(self) -> int:
        """Get the total number of stations"""
        return len(self._stations)
    
    def get_total_actuator_count(self) -> int:
        """Get the total number of actuators across all stations"""
        return sum(station.get_actuator_count() for station in self._stations.values())
    
    def clear(self):
        """Clear all machine data"""
        self._machine_num = None
        self._wph = None
        self._nest_wph = None
        self._transport_type = None
        self._stations.clear()
        self.data_changed.emit()
    
    def to_dict(self) -> Dict:
        """Convert machine data to dictionary for serialization"""
        return {
            'machine_num': self._machine_num,
            'wph': self._wph,
            'nest_wph': self._nest_wph,
            'transport_type': self._transport_type,
            'stations': {
                nb: {
                    'nb': station.nb,
                    'name': station.name,
                    'tag_name': station.tag_name,
                    'up_num': station.up_num,
                    'actuators': [
                        {
                            'act_number': act.act_number,
                            'act_name': act.act_name,
                            'act_tagname': act.act_tagname,
                            'total_track': act.total_track
                        }
                        for act in station.actuators
                    ]
                }
                for nb, station in self._stations.items()
            }
        }
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return (f"MachineData(machine_num={self._machine_num}, "
                f"stations={len(self._stations)}, "
                f"total_actuators={self.get_total_actuator_count()})")
