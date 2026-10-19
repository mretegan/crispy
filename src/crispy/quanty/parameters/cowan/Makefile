# Fetch and build the Cowan atomic-structure binaries used by Crispy. The
# runtime libs are static-linked so the binaries do not depend on the
# MacPorts/GCC libgfortran, libquadmath, or libgcc_s dylibs.
#
# Sources come from the Cowan/TTMult suite on Bitbucket, pinned to a commit.
# Builds rcn31 (aliased rcn), rcn2, and ttrcg, then generates the rcg_cfp7{2,3,4}
# coefficient-of-fractional-parentage tables by running ttrcg on the ing11bk
# bookkeeping input.
#
# The build is native: run it on each platform (macOS, Linux, or Windows with
# MSYS2). The binaries go into bin/<os>-<arch>/, for example bin/darwin-arm64/.
#
# Usage:
#   make                          fetch sources, build binaries, generate cfp
#   make pull                     only fetch (and patch) the sources
#   make install                  copy binaries + cfp into bin/<os>-<arch>/
#   make clean                    remove built binaries and cfp tables
#   make distclean                also remove fetched sources
#   make SRC_COMMIT=<hash>         build from a different upstream revision
#   make FC=gfortran-15           build with a different Fortran compiler

SRC_COMMIT  ?= 25cd694b4ddf09e21a0eadef50c19a9fddce2c6b
SRC_BASEURL ?= https://bitbucket.org/cjtitus/ttmult/raw/$(SRC_COMMIT)/src
SRC_SCRIPTURL ?= https://bitbucket.org/cjtitus/ttmult/raw/$(SRC_COMMIT)/scripts
SRCDIR := src

# Make has a built-in FC (f77), so ?= does not work here.
ifeq ($(origin FC),default)
  FC := gfortran
endif
PROGS := rcn31 rcn2 ttrcg
CFP   := rcg_cfp72 rcg_cfp73 rcg_cfp74

# Legacy-Fortran flags the Cowan sources require.
FFLAGS := -O2 -w -fallow-argument-mismatch -fno-automatic -finit-local-zero -fno-align-commons

# The platform names must match platform_name() in crispy/quanty/cowan.py.
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
ARCH := $(patsubst aarch64,arm64,$(patsubst amd64,x86_64,$(UNAME_M)))

# macOS has no static libSystem, so only the runtime libs can be static-linked.
# Linux and Windows can link fully static.
ifeq ($(UNAME_S),Darwin)
  OS := darwin
  STATIC := -static-libgfortran -static-libgcc -static-libquadmath
  # Oldest macOS version on which the binaries run.
  MACOSX_DEPLOYMENT_TARGET ?= 13.0
  export MACOSX_DEPLOYMENT_TARGET
else ifneq ($(filter MINGW% UCRT% CLANG% MSYS% CYGWIN%,$(UNAME_S)),)
  OS := windows
  EXE := .exe
  STATIC := -static
else
  OS := linux
  STATIC := -static
endif

BINDIR ?= bin/$(OS)-$(ARCH)
PROG_FILES := $(addsuffix $(EXE),$(PROGS))

all: $(PROG_FILES) $(CFP)

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

$(PROG_FILES): %$(EXE): $(SRCDIR)/%.f
	$(FC) $(FFLAGS) $(STATIC) -o $@ $<

# ttrcg writes fort.72/73/74 in one pass; rename them to the rcg_cfp* tables.
# rcg_cfp7{3,4} are produced alongside rcg_cfp72, so they only depend on it.
rcg_cfp72: ttrcg$(EXE) $(SRCDIR)/ing11bk.rcg
	rm -f fort.9 fort.72 fort.73 fort.74
	cp $(SRCDIR)/ing11bk.rcg fort.10
	./ttrcg$(EXE) >/dev/null
	mv fort.72 rcg_cfp72
	mv fort.73 rcg_cfp73
	mv fort.74 rcg_cfp74
	rm -f fort.9 fort.10
rcg_cfp73 rcg_cfp74: rcg_cfp72

install: all
	mkdir -p $(BINDIR)
	cp $(PROG_FILES) $(CFP) $(BINDIR)/
	cp rcn31$(EXE) $(BINDIR)/rcn$(EXE)

clean:
	rm -f $(PROG_FILES) $(CFP)

distclean: clean
	rm -rf $(SRCDIR)

.PHONY: all pull install clean distclean
