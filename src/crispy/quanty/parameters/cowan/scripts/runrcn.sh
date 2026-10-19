#!/bin/sh

# Script that runs the rcn program from the TTMult suite.
# Note that the input file $NAME.rcn has to be created.

# Locate the binaries relative to this script. The folder names must match the
# ones that the Makefile creates, for example bin/darwin-arm64.
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
    mingw* | ucrt* | clang* | msys* | cygwin*) OS=windows ;;
esac
ARCH=$(uname -m)
case "$ARCH" in
    aarch64) ARCH=arm64 ;;
    amd64) ARCH=x86_64 ;;
esac
BINDIR=$(cd "$(dirname "$0")/../bin/$OS-$ARCH" && pwd)

if [ ! -x "$BINDIR/rcn" ]; then
    echo "rcn command was not found."
    exit 1
fi

if [ "$#" -eq 0 ]; then
    NAME='input'
else
    NAME="$1"
fi

if [ -f "$NAME.rcn" ]; then
    ln -sf $NAME.rcn fort.10
    # Note that rcn is an alias to rcn31.
    $BINDIR/rcn
    if [ $? -ne 0 ]; then
        echo "rcn calculation has failed."
        exit 1
    fi
    mv fort.9 $NAME.rcn_out
    rm fort.10
    echo "rcn calculation has finished successfully."
else
    echo "Could not find $NAME.rcn in the current folder."
    exit 1
fi

exit 0
