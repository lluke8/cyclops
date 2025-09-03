@echo off
echo ========================================
echo    Creating Cyclops Deployment Package
echo ========================================
echo.

set PACKAGE_NAME=cyclops_deployment_%date:~-4,4%%date:~-10,2%%date:~-7,2%
set PACKAGE_DIR=%PACKAGE_NAME%

echo Creating deployment package: %PACKAGE_NAME%
echo.

echo [1/4] Creating package directory...
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"
echo ✓ Package directory created
echo.

echo [2/4] Copying project files...
xcopy /E /I /Y src "%PACKAGE_DIR%\src"
xcopy /E /I /Y config "%PACKAGE_DIR%\config"
xcopy /E /I /Y docs "%PACKAGE_DIR%\docs"
copy requirements.txt "%PACKAGE_DIR%\"
copy main.py "%PACKAGE_DIR%\"
copy run_cyclops.bat "%PACKAGE_DIR%\"
copy setup_vm.bat "%PACKAGE_DIR%\"
copy setup_vm.ps1 "%PACKAGE_DIR%\"
echo ✓ Project files copied
echo.

echo [3/4] Creating assets directory...
mkdir "%PACKAGE_DIR%\assets"
mkdir "%PACKAGE_DIR%\assets\templates"
echo ✓ Assets directory created
echo.

echo [4/4] Creating deployment instructions...
echo # Cyclops Deployment Package > "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo. >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo This package contains everything needed to deploy Cyclops on a VM. >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo. >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo Quick Setup: >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo 1. Copy this entire folder to your VM >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo 2. Run setup_vm.bat as Administrator >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo 3. Run run_cyclops.bat to start the application >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo. >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo For detailed instructions, see docs/VM_DEPLOYMENT_GUIDE.md >> "%PACKAGE_DIR%\DEPLOYMENT_INSTRUCTIONS.txt"
echo ✓ Deployment instructions created
echo.

echo ========================================
echo    Package Created Successfully!
echo ========================================
echo Package name: %PACKAGE_NAME%
echo Package location: %CD%\%PACKAGE_DIR%
echo.
echo To deploy on VM:
echo 1. Copy the '%PACKAGE_DIR%' folder to your VM
echo 2. Run setup_vm.bat as Administrator
echo 3. Run run_cyclops.bat to start
echo.
echo ========================================
pause
