# type: ignore
# -*- mode: python -*-
"""PyInstaller script to build the application for macOS and Windows.

On macOS the spec only builds ``dist/Crispy.app``. Code signing, disk image
creation and notarization are run separately (see codesign.sh, create-dmg.sh and
notarize.sh) so that the two per-architecture builds can first be fused into a
single universal2 bundle with merge-universal.py.

On Windows the spec builds the application, runs Inno Setup and creates a zip
archive.
"""

import importlib.metadata
import os
import shutil
import subprocess
import sys

from crispy import version
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, logger

block_cipher = None

if sys.platform == "darwin":
    icon = "crispy.icns"
elif sys.platform == "win32":
    icon = "crispy.ico"
else:
    raise RuntimeError("Unsupported platform")
icon = os.path.join(SPECPATH, icon)  # noqa: F821
logger.info(icon)

project_path = os.path.abspath(os.path.join(SPECPATH, ".."))  # noqa: F821
package_path = os.path.join(project_path, "src", "crispy")


def create_license_file(filename):
    """Generate a LICENSE file with the licenses of the main dependencies."""
    import PyQt6.QtCore

    with open(filename, "w") as f:
        f.write(
            f"""\
This is free software.

It includes many software packages with different licenses:

- Python ({sys.version}): PSF license, https://www.python.org/
- Qt ({PyQt6.QtCore.QT_VERSION_STR}): GNU Lesser General Public License v3, https://www.qt.io/
"""
        )
        for dist in sorted(
            importlib.metadata.distributions(), key=lambda d: (d.name or "").lower()
        ):
            license = dist.metadata.get("License")
            homepage = dist.metadata.get("Home-page")
            info = ", ".join(item for item in (license, homepage) if item)
            f.write(f"- {dist.name} ({dist.version}): {info}\n")


# Application data files, relative to the crispy package.
data_paths = [
    ["uis", "*.ui"],
    ["icons", "*.svg"],
    ["quanty", "calculations.yaml"],
    ["quanty", "parameters", "*.h5"],
    ["quanty", "parameters", "p-d_hybridization", "parameters.dat"],
    ["quanty", "templates", "*.lua"],
    ["quanty", "uis", "*.ui"],
    ["quanty", "uis", "details", "*.ui"],
    ["quanty", "bin", sys.platform, "*"],
]

datas = []
for data_path in data_paths:
    datas.append(
        (os.path.join(package_path, *data_path), os.path.join(*data_path[:-1]))
    )

for package in ("xraydb", "silx.resources"):
    datas.extend(collect_data_files(package))

# Documentation and license files, bundled at the root of the application.
datas.append((os.path.join(project_path, "README.rst"), "."))
datas.append((os.path.join(project_path, "LICENSE.rst"), "."))

# The dependency license dump is generated before the analysis so it is bundled,
# and removed once the build is done.
license_file = os.path.join(SPECPATH, "LICENSE")  # noqa: F821
create_license_file(license_file)
datas.append((license_file, "."))

hiddenimports = ["hdf5plugin"]
hiddenimports += collect_submodules("fabio")

a = Analysis(  # noqa: F821
    [os.path.join(package_path, "__main__.py")],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    # These produce native (.so) modules on only one architecture, which would
    # break the universal2 merge of the two per-architecture builds:
    #  - greenlet: SQLAlchemy (via xraydb) requires it through a platform_machine
    #    marker that lists x86_64 but not macOS arm64, so it lands on x86_64 only.
    #    crispy uses SQLAlchemy synchronously and never imports greenlet.
    #  - sqlalchemy.cyextension: SQLAlchemy ships a cp312 arm64 wheel carrying
    #    these optional C speedups but no cp312 x86_64 wheel, so x86_64 falls back
    #    to the pure-Python wheel without them.
    # Excluding both keeps the builds symmetric; SQLAlchemy uses its pure-Python
    # fallbacks (negligible cost for xraydb's small queries).
    excludes=["greenlet", "sqlalchemy.cyextension"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Crispy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icon,
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Crispy",
)

if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        coll,
        name="Crispy.app",
        icon=icon,
        bundle_identifier=None,
        info_plist={
            "CFBundleIdentifier": "com.github.mretegan.crispy",
            "CFBundleShortVersionString": version,
            "CFBundleVersion": "Crispy " + version,
            "LSTypeIsPackage": True,
            "LSMinimumSystemVersion": "14.0",
            "NSHumanReadableCopyright": "MIT",
            "NSHighResolutionCapable": True,
            "NSPrincipalClass": "NSApplication",
            "NSAppleScriptEnabled": False,
        },
    )


def innosetup():
    """Create an installer using Inno Setup."""
    config_name = "create-installer.iss"
    with open(config_name + ".template") as f:
        content = f.read().replace("#Version", version)
    with open(config_name, "w") as f:
        f.write(content)
    subprocess.call(["iscc", os.path.join(SPECPATH, config_name)])  # noqa: F821
    os.remove(config_name)


def make_zip():
    """Create a zip archive of the application."""
    base_name = os.path.join(
        SPECPATH, "artifacts", f"Crispy-{version}-windows-application"  # noqa: F821
    )
    shutil.make_archive(
        base_name,
        format="zip",
        root_dir=os.path.join(SPECPATH, "dist"),  # noqa: F821
        base_dir="Crispy",
    )


# Post-build actions.
os.remove(license_file)

if sys.platform == "win32":
    innosetup()
    make_zip()
