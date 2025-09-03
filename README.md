# Cyclops - Desktop Automation System

A Python-based desktop automation application that performs predefined in-game actions by monitoring a remote screen via a Virtual Machine (VM). The core principle is reactive automation based on screen state.

## Features

- **Screen Capture**: Capture screen content of specified windows or regions
- **Optical Character Recognition (OCR)**: Read and interpret text from captured screen images
- **Computer Vision**: Identify and locate specific graphical elements via image/pattern matching
- **Input Simulation**: Programmatically control mouse and keyboard interactions
- **State Monitoring**: Continuously check for specific on-screen conditions
- **Reactive Logic**: Execute automated sequences when specific conditions are met
- **GUI Configuration**: User-friendly interface for setting up automation routines

## Installation

### Prerequisites

- Python 3.11 or higher
- Windows 10/11 (primary development platform)
- Tesseract OCR engine

### Setup

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd cyclops
   ```

2. **Install Python dependencies**
   ```bash
   py -m pip install -r requirements.txt
   ```

3. **Install Tesseract OCR** (if not already installed)
   ```bash
   winget install UB-Mannheim.TesseractOCR
   ```

4. **Run the Hello World test**
   ```bash
   py hello_world_test.py
   ```

## Quick Start

1. **Start the application**
   ```bash
   py main.py
   ```

2. **Configure your automation routines** through the GUI interface

3. **Set up your automation profiles** for different use cases

## Use Cases

### Rune Creation
- **Condition**: Presence of a specific item on screen (detected by image matching)
- **Action**: Simulate mouse drag of the item to target location, followed by pressing a predefined keyboard hotkey (F1-F12)

### Eating Food
- **Condition**: User-initiated or based on a cooldown timer
- **Action**: Simulate right-click on a specific screen coordinate (where the food item is located)

### Health Bar Monitoring & Emergency Response
- **Condition**: The color or pixel values in a predefined screen region (the health bar) indicate a "low health" state
- **Action**: Trigger an emergency macro: rapid sequence of mouse movements and keyboard presses (e.g., pressing a healing potion hotkey and moving the character to a safe location)

## Project Structure

```
cyclops/
├── src/                    # Source code
│   ├── core/              # Core functionality modules
│   ├── automation/        # Automation routines and workflows
│   ├── gui/               # User interface components
│   └── utils/             # Utility functions and helpers
├── assets/                # Static assets (images, templates)
├── config/                # Configuration files
├── tests/                 # Test files
├── docs/                  # Documentation
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## Configuration

The application uses JSON configuration files located in the `config/` directory. You can modify automation settings without editing code.

## Development

### Running Tests
```bash
py -m pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document all public functions and classes

## Safety Features

- **Fail-safe mechanism**: Move mouse to top-left corner to stop automation
- **Configurable timeouts**: Prevent infinite loops
- **Error handling**: Robust error recovery and logging
- **User confirmation**: Require confirmation for potentially dangerous operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions, please create an issue in the project repository.
