@echo off
echo ========================================
echo    Cyclops VM Setup Script
echo ========================================
echo.

echo [1/6] Installing Python 3.11...
winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python. Please install manually.
    pause
    exit /b 1
)
echo ✓ Python installed successfully
echo.

echo [2/6] Installing Tesseract OCR...
winget install UB-Mannheim.TesseractOCR --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Tesseract OCR. Please install manually.
    pause
    exit /b 1
)
echo ✓ Tesseract OCR installed successfully
echo.

echo [3/6] Verifying Python installation...
py --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please check installation.
    pause
    exit /b 1
)
echo ✓ Python verification successful
echo.

echo [4/6] Installing Python dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies.
    pause
    exit /b 1
)
echo ✓ Python dependencies installed successfully
echo.

echo [5/6] Testing core modules...
py test_core_modules.py
if %errorlevel% neq 0 (
    echo WARNING: Core module test failed. Please check configuration.
    echo You may need to update the Tesseract path in config/default_config.json
) else (
    echo ✓ Core modules test successful
)
echo.

echo [6/6] Setup complete!
echo.
echo ========================================
echo    Setup Summary
echo ========================================
echo ✓ Python 3.11 installed
echo ✓ Tesseract OCR installed
echo ✓ Python dependencies installed
echo ✓ Core modules tested
echo.
echo Next steps:
echo 1. If Tesseract test failed, update the path in config/default_config.json
echo 2. Run 'run_cyclops.bat' to start the application
echo 3. Configure your automation routines in the GUI
echo.
echo For detailed instructions, see docs/VM_DEPLOYMENT_GUIDE.md
echo ========================================
pause
