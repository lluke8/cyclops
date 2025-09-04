# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('src', 'src'), ('health_reference.png', '.'), ('blank.png', '.')],
    hiddenimports=['tkinter', 'tkinter.scrolledtext', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog', 'pyautogui', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'cv2', 'numpy', 'pytesseract', 'keyboard', 'psutil', 'threading', 'logging', 'json', 'os', 'sys', 'time', 'random', 're', 'typing'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Cyclops_Complete',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
