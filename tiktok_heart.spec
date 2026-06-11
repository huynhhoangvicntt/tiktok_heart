# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['tiktok_heart.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'PIL',
        'scipy', 'cryptography', 'setuptools',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TikTok_AutoHeart',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # tắt UPX — UPX nén làm antivirus nghi hơn
    console=False,      # ẩn terminal, chỉ hiện GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=None,
)
