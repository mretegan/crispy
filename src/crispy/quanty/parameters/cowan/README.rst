Robert Cowan's Atomic Structure Codes
-------------------------------------
Crispy computes the atomic parameters by running ``rcn`` (the ``rcn31`` program
from the Cowan/TTMult suite) and parsing its output. The binaries are not
shipped; build them from source with the ``Makefile`` here (needs gfortran)::

    make            # fetch sources and build
    make install    # copy binaries into bin/
    make clean
    make distclean  # also remove the fetched sources

The Makefile pulls the sources from https://bitbucket.org/cjtitus/ttmult at a
pinned revision and links the gfortran runtime statically, so the binaries do
not need the shared libraries. It applies ``rcn31.patch`` (which makes ``rcn``
print every Slater integral) and, for convenience, also builds the rest of the
suite (``rcn2``, ``ttrcg``, and the ``rcg_cfp7{2,3,4}`` tables) that Crispy does
not use.

See https://www.tcd.ie/Physics/people/Cormac.McGuinness/Cowan for more on
Cowan's programs.
