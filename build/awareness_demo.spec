"""
awareness_demo.spec — PyInstaller spec for Windows and macOS packaging.

Usage:
    pyinstaller build/awareness_demo.spec

Outputs:
    dist/AwarenessDemo        (macOS .app or Linux binary)
    dist/AwarenessDemo.exe    (Windows)
"""

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent  # noqa: F821 — PyInstaller provides SPECPATH

a = Analysis(
    [str(ROOT / "run.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Templates
        (str(ROOT / "app" / "templates"), "app/templates"),
        # Static assets
        (str(ROOT / "app" / "static"), "app/static"),
        # Certs (generated before packaging)
        (str(ROOT / "certs"), "certs"),
        # Scripts needed by the launcher
        (str(ROOT / "scripts"), "scripts"),
        # App source (for imports)
        (str(ROOT / "app"), "app"),
    ],
    hiddenimports=[
        "app",
        "app.app",
        "app.config",
        "app.routes.home",
        "app.routes.auth",
        "app.routes.chat",
        "app.routes.banking",
        "app.routes.upload",
        "app.storage.memory_storage",
        "app.storage.factory",
        "app.schemas.models",
        "flask",
        "werkzeug",
        "cryptography",
        "pydantic",
        "pydantic_settings",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "ruff", "mypy"],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AwarenessDemo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Keep console open so Wireshark filters are visible
    icon=None,
)

# macOS .app bundle
if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        exe,
        name="AwarenessDemo.app",
        icon=None,
        bundle_identifier="com.demo.security-awareness",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": "1.0.0",
        },
    )
