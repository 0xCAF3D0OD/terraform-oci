## Simple Summary

- `pathex=['.']`: Python needs to know where to look for your local 
- `filesdatas=[('../.env', '.')]`: Include the .env file in the executable
- `hiddenimports=[...]`: Explicitly list all modules that PyInstaller does not detect.

```rpmspec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['oci-resource-ctl'],  # ← Main script to compile
    
    # ============================================================
    # pathex: Paths where to search for Python modules
    # ============================================================
    pathex=['.'],  
    # BEFORE: pathex=[]
    # AFTER: pathex=['.']
    # 
    # WHY: 
    # - '.' = current directory (srcs/)
    # - Python needs to know where to find your local modules
    # - Without this, it won't find classes.py, utils/, etc.
    # - Equivalent to: sys.path.append('.')
    
    binaries=[],  # ← Compiled libraries (.so, .dll) - you don't have any
    
    # ============================================================
    # datas: Non-Python files to include in the executable
    # ============================================================
    datas=[
        ('../.env', '.'),  
    ],
    # BEFORE: datas=[]
    # AFTER: datas=[('../.env', '.')]
    #
    # WHY:
    # - Your script uses load_dotenv() to load .env
    # - .env is in oci-python/ (parent of srcs/)
    # - '../.env' = source path (where to find the file)
    # - '.' = destination in executable (root)
    # - Format: (source, destination)
    #
    # WARNING: If .env contains secrets, don't distribute
    # the executable! Or use environment variables instead.
    
    # ============================================================
    # hiddenimports: Modules that PyInstaller doesn't detect auto
    # ============================================================
    hiddenimports=[
        # --- Your local modules (CRITICAL) ---
        'classes',  # ← The missing module!
        
        # Sub-package governance_resources/
        'governance_resources',
        'governance_resources.compartment_handler',
        
        # Sub-package management_resources/
        'management_resources',
        'management_resources.groupes_handler',
        'management_resources.policy_handler',
        'management_resources.users_handler',
        
        # Sub-package utils/
        'utils',
        'utils.config',
        'utils.inquire_handler',
        
        # --- External dependencies ---
        'oci',                      # Oracle SDK
        'oci.identity',             # OCI identity module
        'oci.config',               # OCI config
        'oci.exceptions',           # OCI exceptions
        
        'InquirerPy',               # ← FIXED: You use InquirerPy!
        'InquirerPy.base.control',  # InquirerPy sub-modules
        'InquirerPy.separator',
        
        'dotenv',                   # python-dotenv for .env
    ],
    # WHY hiddenimports:
    # - PyInstaller analyzes your code to find imports
    # - But it misses dynamic or conditional imports
    # - Example: if condition: import module → PyInstaller misses this
    # - Local modules (classes, utils, etc.) are not in
    #   site-packages so PyInstaller doesn't see them
    # - SOLUTION: List them explicitly here
    
    hookspath=[],      # ← Custom hook scripts (not needed here)
    hooksconfig={},    # ← Hook configuration (not needed)
    runtime_hooks=[],  # ← Scripts to run at startup (not needed)
    excludes=[],       # ← Modules to explicitly exclude (not needed)
    noarchive=False,   # ← Archive Python modules (leave False)
    optimize=0,        # ← Python optimization level (0 = debug)
)

pyz = PYZ(a.pure)  # ← Python archive with all modules

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='oci-resource-ctl',
    debug=False,           # ← False = production mode
    bootloader_ignore_signals=False,
    strip=False,           # ← Don't strip symbols (keep debug info)
    upx=True,              # ← Compress with UPX (reduces size)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,          # ← True = console application (not GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```