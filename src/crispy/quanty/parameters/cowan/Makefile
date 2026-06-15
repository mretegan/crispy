# Fetch and build the Cowan atomic-structure binaries used by Crispy. The
# runtime libs are static-linked so the binaries do not depend on the
# MacPorts/GCC libgfortran, libquadmath, or libgcc_s dylibs.
#
# Sources come from the Cowan/TTMult suite on Bitbucket, pinned to a commit.
# Builds rcn31 (aliased rcn), rcn2, and ttrcg, then generates the rcg_cfp7{2,3,4}
# coefficient-of-fractional-parentage tables by running ttrcg on the ing11bk
# bookkeeping input.
#
# Usage:
#   make                          fetch sources, build binaries, generate cfp
#   make pull                     only fetch (and patch) the sources
#   make install                  copy binaries + cfp into bin/
#   make clean                    remove built binaries and cfp tables
#   make distclean                also remove fetched sources
#   make SRC_COMMIT=<hash>         build from a different upstream revision

SRC_COMMIT  ?= 25cd694b4ddf09e21a0eadef50c19a9fddce2c6b
SRC_BASEURL ?= https://bitbucket.org/cjtitus/ttmult/raw/$(SRC_COMMIT)/src
SRC_SCRIPTURL ?= https://bitbucket.org/cjtitus/ttmult/raw/$(SRC_COMMIT)/scripts
SRCDIR := src

FC    := gfortran
PROGS := rcn31 rcn2 ttrcg
CFP   := rcg_cfp72 rcg_cfp73 rcg_cfp74

# Legacy-Fortran flags the Cowan sources require.
FFLAGS := -O2 -w -fallow-argument-mismatch -fno-automatic -finit-local-zero -fno-align-commons

# macOS has no static libSystem, so only the runtime libs can be static-linked.
# Linux can link fully static.
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  STATIC := -static-libgfortran -static-libgcc -static-libquadmath
  # Pin the deployment target to the build host so the linker does not warn
  # about overriding the version embedded in the MacPorts gfortran runtime.
  MACOSX_DEPLOYMENT_TARGET := $(shell sw_vers -productVersion | cut -d. -f1-2)
  export MACOSX_DEPLOYMENT_TARGET
else
  STATIC := -static
endif

BINDIR := bin

all: $(PROGS) $(CFP)

# Fetch (and patch) the sources without compiling.
pull: $(addprefix $(SRCDIR)/,$(addsuffix .f,$(PROGS))) $(SRCDIR)/ing11bk.rcg

# Fetch a source file from the pinned upstream revision.
$(SRCDIR)/%.f:
	@mkdir -p $(SRCDIR)
	curl -fsSL -o $@ $(SRC_BASEURL)/$*.f

# rcn31 needs one line patched out so it prints every Slater integral
# (see README.rst). This rule overrides the generic fetch rule for rcn31.f.
$(SRCDIR)/rcn31.f: rcn31.patch
	@mkdir -p $(SRCDIR)
	curl -fsSL -o $@ $(SRC_BASEURL)/rcn31.f
	patch -N $@ rcn31.patch

# Bookkeeping input that drives the cfp-table generation.
$(SRCDIR)/ing11bk.rcg:
	@mkdir -p $(SRCDIR)
	curl -fsSL -o $@ $(SRC_SCRIPTURL)/ing11bk.rcg

$(PROGS): %: $(SRCDIR)/%.f
	$(FC) $(FFLAGS) $(STATIC) -o $@ $<

# ttrcg writes fort.72/73/74 in one pass; rename them to the rcg_cfp* tables.
# rcg_cfp7{3,4} are produced alongside rcg_cfp72, so they only depend on it.
rcg_cfp72: ttrcg $(SRCDIR)/ing11bk.rcg
	rm -f fort.9 fort.72 fort.73 fort.74
	ln -sf $(SRCDIR)/ing11bk.rcg fort.10
	./ttrcg >/dev/null
	mv fort.72 rcg_cfp72
	mv fort.73 rcg_cfp73
	mv fort.74 rcg_cfp74
	rm -f fort.9 fort.10
rcg_cfp73 rcg_cfp74: rcg_cfp72

install: all
	mkdir -p $(BINDIR)
	cp $(PROGS) $(CFP) $(BINDIR)/
	cp rcn31 $(BINDIR)/rcn

clean:
	rm -f $(PROGS) $(CFP)

distclean: clean
	rm -rf $(SRCDIR)

.PHONY: all pull install clean distclean
