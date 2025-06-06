# Machine Configuration PyQt6 Interface

A simple and effective PyQt6 application for managing machine configuration data from Excel files.

## Features

✅ **Core Functionality:**
- Import Excel backbone files with station and actuator data
- Skip "Free" stations automatically
- Interactive station/actuator browsing
- Manual actuator type assignment
- Clean, professional interface

## Installation

```bash
# Clone the repository
git clone https://github.com/Pasdemain/machine-config-pyqt.git
cd machine-config-pyqt

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
python main.py
```

## Excel File Format

The application expects Excel files with:
- **Info Sheet**: Machine number in cell B2
- **Station Sheets (ST01, ST02, etc.)**:
  - Row 1, Column B: Station name
  - Row 4, Column B: Upstream number  
  - Row 8+: Actuator data (Number, Name, Tracks, Tag)

## Actuator Types

Supported actuator types from templates:
- Pneumatic Cylinder
- Electric Motor
- Servo Motor
- Gripper
- Sensor
- Valve
- Custom

## Project Structure

```
machine-config-pyqt/
├── main.py                     # Main application
├── requirements.txt            # Dependencies
├── actuator_types.json        # Actuator type definitions
└── README.md                  # This file
```