#!/bin/sh

# Script that runs the rcn program from the TTMult suite.
# Note that the input file $NAME.rcn has to be created.

if [ ! -x "$TTMULT/rcn" ]; then
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
    $TTMULT/rcn
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