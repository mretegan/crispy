# type: ignore
"""PyInstaller script to build the application for macOS and Windows."""

import os
import subprocess
import sys

from crispy import version
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, logger

block_cipher = None
package_path = os.path.abspath(os.path.join("..", "src", "crispy"))

if sys.platform == "darwin":
    icon = "crispy.icns"
elif sys.platform == "win32":
    icon = "crispy.ico"
icon = os.path.join(os.getcwd(), icon)
logger.info(icon)

data_paths = [
    ["uis", "*.ui"], 
    ["icons", "*.svg"], 
    ["quanty", "calculations.yaml"],
    ["quanty", "parameters", "*.h5"], 
    ["quanty", "templates", "*.lua"],
    ["quanty", "uis", "*.ui"],
    ["quanty", "uis", "details", "*.ui"],
    ["quanty", "bin", sys.platform, "*"],
]

datas = []
for data_path in data_paths:
    datas.append((os.path.join(package_path, *data_path), os.path.join(*data_path[:-1])))

for package in ("xraydb", "silx.resources"):
    datas.extend(collect_data_files(package))

hiddenimports = collect_submodules("fabio")

a = Analysis(
    [os.path.join(package_path, "__main__.py")],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Crispy",
)

app = BUNDLE(
    coll,
    name="Crispy.app",
    icon=icon,
    bundle_identifier=None,
    info_plist={
        "CFBundleIdentifier": "com.github.mretegan.crispy",
        "CFBundleShortVersionString": version,
        "CFBundleVersion": "Crispy " + version,
        "LSTypeIsPackage": True,
        "LSMinimumSystemVersion": "10.13.0",
        "NSHumanReadableCopyright": "MIT",
        "NSHighResolutionCapable": True,
        "NSPrincipalClass": "NSApplication",
        "NSAppleScriptEnabled": False,
    },
)

# Post build actions.
if sys.platform == "darwin":

    # Remove the extended attributes from the MacOS application as this causes
    # the application to fail to launch ("is damaged and can’t be opened. You
    # should move it to the Trash").
    subprocess.call(["xattr", "-cr", os.path.join("dist", "Crispy.app")])

    # Pack the application.
    subprocess.call(["bash", "create-dmg.sh"])

    # Rename the created .dmg image.
    os.rename(
        os.path.join("artifacts", "Crispy.dmg"),
        os.path.join("artifacts", f"Crispy-{version}.dmg"),
    )

elif sys.platform == "win32":
    # Remove Quanty's macOS and Linux binaries.
    root = os.path.join("dist", "Crispy", "quanty", "bin")
    os.remove(os.path.join(root, "darwin", "Quanty"))
    os.remove(os.path.join(root, "linux", "Quanty"))

    # Create the Inno Setup script.
    root = os.path.join(os.getcwd(), "assets")
    name = "create-installer.iss"
    template = open(name + ".template").read()
    template = template.replace("#Version", version)
    with open(os.path.join(name), "w") as f:
        f.write(template)

    # Run the Inno Setup compiler.
    subprocess.call(["iscc", name])

    # Remove the .iss file
    os.remove(name)
