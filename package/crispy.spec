# pylint: disable=all
# type: ignore
"""PyInstaller script to build the application for macOS and Windows."""

import os
import logging
import sys
import subprocess

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

from crispy import version

logger = logging.getLogger("pyinstaller")

block_cipher = None
package_path = "../crispy"

if sys.platform == "darwin":
    icon = "crispy.icns"
elif sys.platform == "win32":
    icon = "crispy.ico"
icon = os.path.join(os.getcwd(), icon)
logger.info(icon)

datas = [
    (os.path.join(package_path, "uis"), "uis"),
    (os.path.join(package_path, "icons"), "icons"),
    (os.path.join(package_path, "quanty"), "quanty"),
]

for package in ("xraydb", "silx.resources"):
    datas.extend(collect_data_files(package))

hiddenimports = collect_submodules("fabio")

a = Analysis(
    [os.path.join(package_path, "main.py")],
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

# Remove the MKL libraries.
for binary in sorted(a.binaries):
    name, _, _ = binary
    for key in ("mkl",):
        if key in name:
            a.binaries.remove(binary)
            logger.info(f"Removed {name}.")

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
    # Remove the signature from the Python interpreter.
    # see https://github.com/pyinstaller/pyinstaller/issues/5062.
    subprocess.call(
        [
            "codesign",
            "--remove-signature",
            os.path.join("dist", "Crispy.app", "Contents", "MacOS", "Python"),
        ]
    )
    # Remove Quanty's Windows and Linux binaries.
    root = os.path.join("dist", "Crispy.app", "Contents", "Resources", "quanty", "bin")
    os.remove(os.path.join(root, "win32", "Quanty.exe"))
    os.remove(os.path.join(root, "linux", "Quanty"))

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
