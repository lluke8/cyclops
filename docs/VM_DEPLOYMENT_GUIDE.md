# Cyclops VM Deployment Guide

This guide explains how to deploy and run Cyclops on a Virtual Machine (VM) for remote automation.

## Prerequisites

- Windows VM with administrative access
- Internet connection for downloading dependencies
- At least 2GB RAM and 1GB free disk space

## Step 1: Install Python

### Option A: Using Windows Package Manager (Recommended)
```powershell
# Open PowerShell as Administrator
winget install Python.Python.3.11
```

### Option B: Manual Download
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Run installer with "Add Python to PATH" checked
3. Verify installation: `py --version`

## Step 2: Install Tesseract OCR

```powershell
# Using Windows Package Manager
winget install UB-Mannheim.TesseractOCR
```

**Important**: Note the installation path (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)

## Step 3: Deploy Cyclops Project

### Option A: Copy Project Folder
1. Copy your entire `cyclops` project folder to the VM
2. Place it in a convenient location (e.g., `C:\cyclops`)

### Option B: Git Clone (if using version control)
```powershell
git clone <your-repo-url> C:\cyclops
cd C:\cyclops
```

## Step 4: Install Python Dependencies

```powershell
# Navigate to project directory
cd C:\cyclops

# Install required packages
py -m pip install -r requirements.txt
```

## Step 5: Configure Tesseract Path

Edit `config/default_config.json` and update the Tesseract path:

```json
{
    "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

## Step 6: Test Installation

```powershell
# Run the test script
py test_core_modules.py
```

## Step 7: Launch Cyclops

```powershell
# Option 1: Using batch file
run_cyclops.bat

# Option 2: Direct Python execution
py main.py
```

## VM-Specific Considerations

### Performance Optimization
- **RAM**: Allocate at least 2GB RAM to the VM
- **CPU**: Enable hardware acceleration if available
- **Graphics**: Ensure proper graphics drivers are installed

### Network Configuration
- **RDP**: If using Remote Desktop, ensure proper display scaling
- **VNC**: Alternative remote access method
- **Local Access**: Best performance when accessing VM directly

### Automation Limitations
- **Input Simulation**: May be limited in some VM environments
- **Screen Capture**: Performance depends on VM graphics capabilities
- **Timing**: May need adjustment for VM performance characteristics

## Troubleshooting

### Common Issues

1. **Python not found**
   - Use `py` instead of `python` on Windows
   - Verify PATH environment variable

2. **Tesseract not found**
   - Check installation path in config
   - Verify Tesseract is in system PATH

3. **Import errors**
   - Ensure all dependencies are installed: `py -m pip install -r requirements.txt`
   - Check Python version compatibility

4. **Screen capture issues**
   - Verify display drivers
   - Check VM graphics acceleration settings

5. **Input simulation not working**
   - Some VMs block input simulation for security
   - Try running as Administrator
   - Check VM input settings

### Performance Tips

- **Close unnecessary applications** on the VM
- **Use dedicated graphics** if available
- **Monitor resource usage** during automation
- **Adjust cooldown timings** for VM performance

## Security Considerations

- **VM Isolation**: Ensure VM is properly isolated from host
- **Network Access**: Limit VM network access if not needed
- **User Permissions**: Run with minimal required permissions
- **Automation Scope**: Limit automation to intended applications only

## Maintenance

### Regular Updates
```powershell
# Update Python packages
py -m pip install --upgrade -r requirements.txt

# Update Tesseract (if needed)
winget upgrade UB-Mannheim.TesseractOCR
```

### Log Monitoring
- Check `cyclops.log` for errors
- Monitor system performance during automation
- Review automation success rates

## Support

If you encounter issues:
1. Check the logs in `cyclops.log`
2. Verify all dependencies are installed
3. Test individual components using test scripts
4. Review VM configuration and performance
