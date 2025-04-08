a = Analysis(
    ['main.py'],
    pathex=None,
    binaries=None,
    datas=[('data','data'), ('ui','ui'), ('.\config.ini' , '.'), ('.\logo.ico' , '.'), ('.\MyWidgets.py' , '.')],
    hiddenimports=[],
    hookspath=None,
    hooksconfig={},
    runtime_hooks=None,
    excludes=None,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KGA Katalog',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.',
    icon='.\logo.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KGA Katalog',
)
