#!/usr/bin/env python3
"""Merge an arm64 and an x86_64 PyInstaller .app bundle into a universal2 bundle.

The two bundles are produced by running PyInstaller (onedir) on an Apple Silicon
and an Intel macOS runner. This walks the arm64 bundle and, for every file, fuses
the matching x86_64 file with ``lipo`` when both are thin Mach-O binaries, and
copies it otherwise (identical files, already-universal binaries, data files).

Usage:
    python merge-universal.py <arm64.app> <x86_64.app> <output.app>
"""

import argparse
import filecmp
import os
import shutil
import subprocess
import sys

# Mach-O magic numbers, matched against the first four bytes on disk.
THIN_MAGICS = {
    b"\xfe\xed\xfa\xce",  # 32-bit, big-endian
    b"\xfe\xed\xfa\xcf",  # 64-bit, big-endian
    b"\xce\xfa\xed\xfe",  # 32-bit, little-endian
    b"\xcf\xfa\xed\xfe",  # 64-bit, little-endian
}
FAT_MAGICS = {
    b"\xca\xfe\xba\xbe",  # big-endian
    b"\xbe\xba\xfe\xca",  # little-endian
}


def macho_kind(path):
    """Return "thin", "fat" or None by inspecting the file's magic bytes.

    Detection is by content, not extension: PyInstaller ships extension-less
    Mach-O binaries (e.g. inside Qt frameworks). Fat magic is shared with Java
    .class files, so it is disambiguated using the architecture count, which is
    small for a real universal binary.
    """
    try:
        with open(path, "rb") as f:
            header = f.read(8)
    except OSError:
        return None
    if len(header) < 8:
        return None
    magic = header[:4]
    if magic in THIN_MAGICS:
        return "thin"
    if magic in FAT_MAGICS:
        byteorder = "big" if magic == b"\xca\xfe\xba\xbe" else "little"
        architectures = int.from_bytes(header[4:8], byteorder)
        return "fat" if architectures < 30 else None
    return None


def collect(root):
    """Map each path inside ``root`` to its kind ("dir", "symlink" or "file")."""
    entries = {}
    for current, dirnames, filenames in os.walk(root):
        # Symlinked directories must be recreated as links, not descended into.
        for name in list(dirnames):
            absolute = os.path.join(current, name)
            relative = os.path.relpath(absolute, root)
            if os.path.islink(absolute):
                dirnames.remove(name)
                entries[relative] = "symlink"
            else:
                entries[relative] = "dir"
        for name in filenames:
            absolute = os.path.join(current, name)
            relative = os.path.relpath(absolute, root)
            entries[relative] = "symlink" if os.path.islink(absolute) else "file"
    return entries


def recreate_symlink(src, dest):
    if os.path.lexists(dest):
        os.remove(dest)
    os.symlink(os.readlink(src), dest)


def fuse_file(arm_path, x86_path, dest):
    subprocess.run(["lipo", "-create", arm_path, x86_path, "-output", dest], check=True)
    shutil.copymode(arm_path, dest)


def merge(arm_root, x86_root, out_root):
    arm = collect(arm_root)
    x86 = collect(x86_root)
    all_paths = sorted(set(arm) | set(x86), key=lambda p: p.count(os.sep))

    os.makedirs(out_root, exist_ok=True)

    # Create the directory skeleton first so files have somewhere to land.
    for relative in all_paths:
        if "dir" in (arm.get(relative), x86.get(relative)):
            os.makedirs(os.path.join(out_root, relative), exist_ok=True)

    # Mach-O binaries that exist for only one architecture cannot be made
    # universal; collect them and report all of them together at the end.
    single_arch = []

    for relative in all_paths:
        arm_kind = arm.get(relative)
        x86_kind = x86.get(relative)
        if "dir" in (arm_kind, x86_kind):
            continue

        out_path = os.path.join(out_root, relative)
        arm_path = os.path.join(arm_root, relative)
        x86_path = os.path.join(x86_root, relative)

        # Symlinks: recreate verbatim from whichever tree has them.
        if "symlink" in (arm_kind, x86_kind):
            if arm_kind == "symlink" and x86_kind == "symlink":
                if os.readlink(arm_path) != os.readlink(x86_path):
                    print(f"WARNING: symlink target differs, using arm64: {relative}")
            recreate_symlink(arm_path if arm_kind == "symlink" else x86_path, out_path)
            continue

        # Regular file present in only one of the two bundles.
        if arm_kind is None or x86_kind is None:
            present = arm_path if arm_kind else x86_path
            if macho_kind(present):
                single_arch.append(relative)
                continue
            print(f"WARNING: data file present in only one architecture: {relative}")
            shutil.copy2(present, out_path)
            continue

        # Regular file present in both: identical -> copy, otherwise fuse Mach-O.
        if filecmp.cmp(arm_path, x86_path, shallow=False):
            shutil.copy2(arm_path, out_path)
            continue

        arm_macho = macho_kind(arm_path)
        x86_macho = macho_kind(x86_path)
        if arm_macho == "thin" and x86_macho == "thin":
            fuse_file(arm_path, x86_path, out_path)
        elif "fat" in (arm_macho, x86_macho):
            # Already-universal binary that merely differs in signature bytes.
            shutil.copy2(arm_path if arm_macho == "fat" else x86_path, out_path)
        elif bool(arm_macho) != bool(x86_macho):
            single_arch.append(relative)
        else:
            print(f"WARNING: data file differs, using arm64: {relative}")
            shutil.copy2(arm_path, out_path)

    if single_arch:
        listing = "\n".join(f"  - {p}" for p in sorted(single_arch))
        sys.exit(
            "ERROR: these Mach-O binaries exist for only one architecture, so "
            "the merged app would crash on the missing one:\n"
            f"{listing}\n"
            "Make the dependency sets identical across both builds (exclude the "
            "package in crispy.spec, or install it on both runners)."
        )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("arm64_app", help="Path to the arm64 .app bundle")
    parser.add_argument("x86_64_app", help="Path to the x86_64 .app bundle")
    parser.add_argument("output_app", help="Path to write the universal .app bundle")
    args = parser.parse_args()

    for path in (args.arm64_app, args.x86_64_app):
        if not os.path.isdir(path):
            sys.exit(f"ERROR: not a directory: {path}")
    if os.path.exists(args.output_app):
        shutil.rmtree(args.output_app)

    merge(args.arm64_app, args.x86_64_app, args.output_app)

    # Self-check: the main executable must now be universal.
    executable = os.path.join(args.output_app, "Contents", "MacOS", "Crispy")
    if os.path.exists(executable):
        result = subprocess.run(
            ["lipo", "-archs", executable], capture_output=True, text=True
        )
        architectures = set(result.stdout.split())
        print(f"Merged executable architectures: {result.stdout.strip()}")
        if not {"x86_64", "arm64"} <= architectures:
            sys.exit(
                f"ERROR: merged executable is not universal: {result.stdout.strip()}"
            )

    print(f"Universal bundle written to {args.output_app}")


if __name__ == "__main__":
    main()
