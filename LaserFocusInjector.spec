# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['sprite_converter_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('sprite_processor.py', '.'), ('mod_packager.py', '.'), ('Template.zip', '.'), ('pokemon_weaknesses.json', '.'), ('badges', 'badges'), ('modpackages', 'modpackages')],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageSequence', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.scrolledtext', 'mod_packager', 'sprite_processor'],
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
    name='LaserFocusInjector',
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
    icon=['icon.ico'],
)
