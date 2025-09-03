# Cyclops VM Setup Script (PowerShell)
# Run this script as Administrator on your VM

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Cyclops VM Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    Write-Host "[1/6] Installing Python 3.11..." -ForegroundColor Yellow
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Python"
    }
    Write-Host "✓ Python installed successfully" -ForegroundColor Green
    Write-Host ""

    Write-Host "[2/6] Installing Tesseract OCR..." -ForegroundColor Yellow
    winget install UB-Mannheim.TesseractOCR --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Tesseract OCR"
    }
    Write-Host "✓ Tesseract OCR installed successfully" -ForegroundColor Green
    Write-Host ""

    Write-Host "[3/6] Verifying Python installation..." -ForegroundColor Yellow
    $pythonVersion = py --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found after installation"
    }
    Write-Host "✓ Python verification successful: $pythonVersion" -ForegroundColor Green
    Write-Host ""

    Write-Host "[4/6] Installing Python dependencies..." -ForegroundColor Yellow
    py -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip"
    }
    
    py -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Python dependencies"
    }
    Write-Host "✓ Python dependencies installed successfully" -ForegroundColor Green
    Write-Host ""

    Write-Host "[5/6] Testing core modules..." -ForegroundColor Yellow
    py test_core_modules.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Core module test failed. Please check configuration." -ForegroundColor Yellow
        Write-Host "You may need to update the Tesseract path in config/default_config.json" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Core modules test successful" -ForegroundColor Green
    }
    Write-Host ""

    Write-Host "[6/6] Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    Setup Summary" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✓ Python 3.11 installed" -ForegroundColor Green
    Write-Host "✓ Tesseract OCR installed" -ForegroundColor Green
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
    Write-Host "✓ Core modules tested" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. If Tesseract test failed, update the path in config/default_config.json" -ForegroundColor White
    Write-Host "2. Run 'run_cyclops.bat' to start the application" -ForegroundColor White
    Write-Host "3. Configure your automation routines in the GUI" -ForegroundColor White
    Write-Host ""
    Write-Host "For detailed instructions, see docs/VM_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Setup failed. Please check the error and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"
