# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['oci-resource-ctl'],  # Script principal
    pathex=['.'],  # ← IMPORTANT : Ajouter le répertoire courant
    binaries=[],
    datas=[],
    hiddenimports=[
        # Module racine
        'classes',

        # Sous-paquet governance_resources
        'governance_resources',
        'governance_resources.compartment_handler',

        # Sous-paquet management_resources
        'management_resources',
        'management_resources.groupes_handler',
        'management_resources.policy_handler',
        'management_resources.users_handler',

        # Sous-paquet utils
        'utils',
        'utils.config',
        'utils.inquire_handler',

        # Dépendances externes qui peuvent poser problème
        'InquirerPy',
        'InquirerPy.base.control',
        'InquirerPy.separator',
        'oci',
        'oci.identity',
        'oci.config',
        'oci.exceptions',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='oci-resource-ctl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)