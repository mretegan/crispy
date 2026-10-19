Robert Cowan's Atomic Structure Codes
-------------------------------------
Crispy computes the atomic parameters by running ``rcn`` (the ``rcn31`` program
from the Cowan/TTMult suite) and parsing its output. The binaries are in
``bin/<os>-<arch>/``, for example ``bin/darwin-arm64/`` or
``bin/windows-x86_64/``. Crispy uses the folder that matches the platform.

Build the binaries from source with the ``Makefile`` here (needs gfortran). The
build is native, so run it on each platform::

    make            # fetch sources and build
    make install    # copy binaries into bin/<os>-<arch>/
    make clean
    make distclean  # also remove the fetched sources

On Windows, run ``make`` in an MSYS2 shell with the MinGW gfortran. On macOS,
the binaries run on macOS 13 and later. Set ``MACOSX_DEPLOYMENT_TARGET`` to change this.

The ``Build Cowan binaries`` GitHub Actions workflow builds the binaries for all
supported platforms. Download its artifact, copy the folders into ``bin/``, and
add them with ``git add -f`` (``.gitignore`` excludes ``bin/``).

The Makefile pulls the sources from https://bitbucket.org/cjtitus/ttmult at a
pinned revision and links the gfortran runtime statically, so the binaries do
not need the shared libraries. It applies ``rcn31.patch`` (which makes ``rcn``
print every Slater integral) and, for convenience, also builds the rest of the
suite (``rcn2``, ``ttrcg``, and the ``rcg_cfp7{2,3,4}`` tables).

See https://www.tcd.ie/Physics/people/Cormac.McGuinness/Cowan for more on
Cowan's programs.
