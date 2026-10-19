#!/bin/sh

# Script that runs the rcn2 program from the TTMult suite.

# Locate the binaries relative to this script. The folder names must match the
# ones that the Makefile creates, for example bin/linux-x86_64.
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
    mingw* | ucrt* | clang* | msys* | cygwin*) OS=windows ;;
esac
ARCH=$(uname -m)
case "$ARCH" in
    aarch64) ARCH=arm64 ;;
    amd64) ARCH=x86_64 ;;
esac
# The macOS binaries are universal, so the folder has no architecture.
case "$OS" in
    darwin) PLATFORM=darwin ;;
    *) PLATFORM="$OS-$ARCH" ;;
esac
BINDIR=$(cd "$(dirname "$0")/../bin/$PLATFORM" && pwd)

if [ ! -x "$BINDIR/rcn2" ]; then
    echo "rcn2 command was not found."
    exit 1
fi

if [ "$#" -eq 0 ]; then
    NAME='input'
else
    NAME="$1"
fi

# The input file for rcn2 must be added in the current folder.
if [ -f "$NAME.rcn2" ]; then
    ln -sf $NAME.rcn2 fort.10
    $BINDIR/rcn2
    if [ $? -ne 0 ]; then
        echo "rcn2 calculation has failed."
        exit 1
    fi
    mv fort.9 $NAME.rcn2_out
    mv fort.11 $NAME.rcg
    rm fort.10
    echo "rcn2 calculation has finished successfully."
else
    echo "Could not find $NAME.rcn2 in the current folder."
    exit 1
fi

exit 0
