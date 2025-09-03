# Cyclops Project Structure

## Directory Overview

```
cyclops/
├── src/                    # Source code
│   ├── core/              # Core functionality modules
│   │   ├── __init__.py
│   │   ├── screen_capture.py    # Screen capture and region selection
│   │   ├── ocr_engine.py        # Text recognition functionality
│   │   ├── computer_vision.py   # Image matching and pattern recognition
│   │   ├── input_simulator.py   # Mouse and keyboard automation
│   │   └── state_monitor.py     # Screen state monitoring
│   │
│   ├── automation/        # Automation routines and workflows
│   │   ├── __init__.py
│   │   ├── rune_creation.py     # Rune creation automation
│   │   ├── food_eating.py       # Food consumption automation
│   │   ├── health_monitor.py    # Health bar monitoring and emergency response
│   │   └── workflow_manager.py  # Orchestrates automation sequences
│   │
│   ├── gui/               # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py       # Main application window
│   │   ├── config_panel.py      # Configuration interface
│   │   ├── automation_panel.py  # Automation control panel
│   │   └── status_display.py    # Status and logging display
│   │
│   └── utils/             # Utility functions and helpers
│       ├── __init__.py
│       ├── config_manager.py    # Configuration file management
│       ├── logger.py            # Logging utilities
│       ├── timing.py            # Timing and delay utilities
│       └── coordinates.py       # Coordinate system utilities
│
├── assets/                # Static assets
│   ├── images/           # Reference images for pattern matching
│   │   ├── health_bars/  # Health bar templates
│   │   ├── items/        # Item icons and templates
│   │   └── ui_elements/  # UI element templates
│   └── templates/        # Configuration templates
│
├── config/               # Configuration files
│   ├── default_config.json
│   ├── automation_profiles/
│   └── user_settings.json
│
├── tests/                # Test files
│   ├── __init__.py
│   ├── test_core/
│   ├── test_automation/
│   └── test_integration/
│
├── docs/                 # Documentation
│   ├── user_guide.md
│   ├── api_reference.md
│   └── automation_guide.md
│
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── README.md            # Project overview and setup
└── PROJECT_STRUCTURE.md # This file
```

## Module Responsibilities

### Core Modules (`src/core/`)
- **screen_capture.py**: Handles screenshot capture, window detection, and region selection
- **ocr_engine.py**: Text recognition using Tesseract OCR
- **computer_vision.py**: Image matching, template matching, and pattern recognition
- **input_simulator.py**: Mouse and keyboard input automation
- **state_monitor.py**: Continuous monitoring of screen states and conditions

### Automation Modules (`src/automation/`)
- **rune_creation.py**: Implements rune creation workflow
- **food_eating.py**: Implements food consumption automation
- **health_monitor.py**: Implements health monitoring and emergency responses
- **workflow_manager.py**: Orchestrates complex automation sequences

### GUI Modules (`src/gui/`)
- **main_window.py**: Main application interface
- **config_panel.py**: Configuration and settings interface
- **automation_panel.py**: Automation control and monitoring
- **status_display.py**: Real-time status and log display

### Utility Modules (`src/utils/`)
- **config_manager.py**: Handles configuration file loading/saving
- **logger.py**: Centralized logging system
- **timing.py**: Timing utilities and delay management
- **coordinates.py**: Coordinate system conversions and utilities

## Design Principles

1. **Modularity**: Each module has a single, well-defined responsibility
2. **Separation of Concerns**: Core functionality is separate from automation logic and UI
3. **Configuration-Driven**: Automation behaviors are configurable without code changes
4. **Testability**: Each module can be tested independently
5. **Extensibility**: New automation routines can be added easily
6. **Error Handling**: Robust error handling and recovery mechanisms
7. **Logging**: Comprehensive logging for debugging and monitoring

## File Naming Conventions

- Use snake_case for Python files
- Use descriptive names that indicate the module's purpose
- Include `__init__.py` files to make directories Python packages
- Configuration files use JSON format with descriptive names
- Test files are prefixed with `test_`
- Documentation files use markdown format
