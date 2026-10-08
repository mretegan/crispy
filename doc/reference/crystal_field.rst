Crystal Field and Axis Conventions
==================================

Symmetry and the Choice of Axes
-------------------------------
A free ion is **spherically symmetric**. Every orbital of a given angular
momentum :math:`\ell` (the five *d* orbitals, the seven *f* orbitals) is
degenerate, and the energy cannot depend on direction: there is simply no
preferred axis. In that situation talking about "the *z* axis" is meaningless.

Axes appear the moment the ion is placed in a **non-spherical environment**.
The surrounding ligands (or the crystalline lattice) lower the symmetry from the
full rotation group to one of the molecular **point groups** (``Oh``, ``Td``,
``D4h`` ...). Two things happen at once:

* the orbital degeneracy is partially lifted: the level splits into sets that
  transform as the **irreducible representations** (irreps) of the point group;
* the splitting is defined *relative to the symmetry elements* of that group:
  its rotation axes and mirror planes.

To turn this into numbers a calculation has to pin a **Cartesian frame** onto
those symmetry elements: the *z* axis is put along the principal rotation axis,
*x* and *y* along secondary axes or mirror planes, and so on. That frame is a
**convention** (several are equally valid, related by rotations), but the
numerical values of the crystal field parameters are only meaningful once it is
fixed. This page documents the convention Crispy uses for every implemented
geometry.

The Crystal Field Potential
---------------------------
Crispy builds the one-electron crystal field term as a potential expanded on
**renormalized (Racah) spherical harmonics** :math:`C^{(m)}_k`:

.. math::

    V(\theta,\phi) = \sum_{k,m} A_{k,m}\, C^{(m)}_k(\theta,\phi),
    \qquad C^{(m)}_k = \sqrt{\tfrac{4\pi}{2k+1}}\, Y^{(m)}_k ,

where the radial integrals :math:`\langle r^k \rangle` are absorbed into the
:math:`A_{k,m}` coefficients.

In the Quanty templates this is the ``Akm`` table of ``{k, m, value}`` triples
passed to ``NewOperator("CF", ...)``. Only **even** :math:`k` contribute within a
shell (:math:`k = 0, 2, 4` for *d*; :math:`k = 0, 2, 4, 6` for *f*), and which
:math:`\{k,m\}` terms survive (and with what coefficients) is fixed by the
point group **and its orientation**. The :math:`k=0` (monopole) term is a constant
shift of all levels and is dropped (or, equivalently, the irrep energies are
referenced to their degeneracy-weighted average).

The :math:`A_{k,m}` coefficients used in Crispy are taken directly from the
**Quanty point-group tables**:

    https://www.quanty.org/physics_chemistry/point_groups

Each point group there offers several *orientations* (sub-pages such as
``.../d3d/orientation_zy``); the symmetry-operation vectors listed on a page
state exactly how the rotation axes and mirror planes point in the *xyz* frame.

Axis Orientations
-----------------
The table below gives, for every symmetry implemented in Crispy, the Quanty
orientation that the templates reproduce and how the Cartesian axes are tied to
the symmetry elements.

.. list-table::
    :header-rows: 1
    :widths: 12 14 74

    * - Symmetry
      - Quanty setting
      - Alignment of the *xyz* axes with the symmetry elements
    * - ``Oh``
      - `xyz <https://www.quanty.org/physics_chemistry/point_groups/
        oh/orientation_xyz>`__
      - The three four-fold (``C4``) axes lie along *x*, *y*, and *z*:
        the octahedral ligands sit on the Cartesian axes. The ``C3`` axes run along
        the cube body-diagonals :math:`[\pm1,\pm1,\pm1]`.
    * - ``Td``
      - `xyz <https://www.quanty.org/physics_chemistry/point_groups/
        td/orientation_xyz>`__
      - The tetrahedron is inscribed in a cube whose edges lie along *x*, *y*,
        *z*. The ``S4``/``C2`` axes are along *x*, *y*, *z* and the four ``C3``
        axes along the cube body-diagonals. (The *d* field is exactly the
        negative of the ``Oh`` one.)
    * - ``D4h``
      - `zxy <https://www.quanty.org/physics_chemistry/point_groups/
        d4h/orientation_zxy>`__
      - The four-fold ``C4`` principal axis is along *z*; the ``C2'`` axes and
        the vertical mirror planes :math:`\sigma_v` lie along *x* and *y* (the
        equatorial ligands sit on *x* and *y*, so ``b1g`` is the
        :math:`d_{x^2-y^2}` orbital). The ``C2''`` axes / :math:`\sigma_d`
        planes are at 45°.
    * - ``D3d``
      - `zy <https://www.quanty.org/physics_chemistry/point_groups/
        d3d/orientation_zy>`__
      - The three-fold ``C3`` axis is along *z*; one basal ``C2`` axis is along
        *y* (the other two and the :math:`\sigma_d` planes follow at 120°).
    * - ``D3h``
      - `zx <https://www.quanty.org/physics_chemistry/point_groups/
        d3h/orientation_zx>`__
      - The three-fold ``C3`` axis is along *z*; the horizontal mirror
        :math:`\sigma_h` is the *xy* plane; one ``C2'`` axis lies along *x*.
    * - ``C3v``
      - `D3d "zy" <https://www.quanty.org/physics_chemistry/point_groups/
        d3d/orientation_zy>`__
      - The three-fold ``C3`` axis is along *z*; a vertical mirror plane
        :math:`\sigma_v` contains the *y* axis. The ``C3v`` pages of Quanty are
        unpopulated, so Crispy uses the König & Kremer convention, which is the
        ``D3d`` ``zy`` setting with the inversion center removed (the *d*–*d*
        block is identical because it is built from even-\ :math:`k` harmonics).

Parameters and Orbital Splittings
---------------------------------
The orbital splittings and the parameters exposed in the interface are listed
below for both the *d* and *f* blocks. Energies are quoted relative to the
barycenter.

``Oh``: Octahedral
~~~~~~~~~~~~~~~~~~
* *d*: ``eg`` + ``t2g`` separated by the single parameter ``10Dq``
  (``eg`` at :math:`+0.6\,\mathrm{10Dq}`, ``t2g`` at :math:`-0.4\,\mathrm{10Dq}`).
* *f*: ``a2u`` + ``t1u`` + ``t2u`` (parameters ``Ea2u``, ``Et1u``, ``Et2u``).

``Td``: Tetrahedral
~~~~~~~~~~~~~~~~~~~
* *d*: ``e`` + ``t2`` (``e`` at :math:`-0.6\,\mathrm{10Dq}`, ``t2`` at
  :math:`+0.4\,\mathrm{10Dq}`), the inverted ``Oh`` field.
* *f*: ``a1`` + ``t1`` + ``t2`` (parameters ``Ea1``, ``Et1``, ``Et2``). The
  Quanty point-group table labels the singlet ``a2``.

``D4h``: Tetragonal
~~~~~~~~~~~~~~~~~~~
* *d*: ``a1g`` + ``b1g`` + ``b2g`` + ``eg``, parametrized by ``10Dq``, ``Ds``,
  ``Dt``, with Dq = 10Dq/10 (``a1g`` = 6Dq − 2Ds − 6Dt,
  ``b1g`` = 6Dq + 2Ds − Dt, ``b2g`` = −4Dq + 2Ds − Dt, ``eg`` = −4Dq − Ds + 4Dt).
* *f*: ``a2u`` + ``b1u`` + ``b2u`` + 2 ``eu``; the two ``eu`` sets mix through the
  off-diagonal ``Meu`` (parameters ``Ea2u``, ``Eb1u``, ``Eb2u``, ``Eeu1``,
  ``Eeu2``, ``Meu``).

``D3d``: Trigonal (With Inversion)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* *d*: ``a1g`` + 2 ``eg``; the two ``eg`` sets (descended from the cubic ``eg``
  and ``t2g``) mix through ``Meg`` (parameters ``Ea1g``, ``Eegσ``, ``Eegπ``,
  ``Meg``).
* *f*: ``a1u`` + 2 ``a2u`` + 2 ``eu``; the ``a2u`` pair mixes through ``Ma2u`` and
  the ``eu`` pair through ``Meu`` (parameters ``Ea1u``, ``Ea2uA``, ``Ea2uB``,
  ``Eeu1``, ``Eeu2``, ``Ma2u``, ``Meu``).

``D3h``: Trigonal (With a Horizontal Mirror)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* *d*: ``a1'`` + ``e'`` + ``e''``, parametrized by ``Dμ`` and ``Dν``
  (``a1'`` = −2Dμ − 6Dν, ``e'`` = 2Dμ − Dν, ``e''`` = −Dμ + 4Dν).
* *f*: ``a1'`` + ``a2'`` + ``a2''`` + ``e'`` + ``e''`` (no off-diagonal mixing:
  every irrep appears once; parameters ``Ea1p``, ``Ea2p``, ``Ea2pp``, ``Eep``,
  ``Eepp``).

``C3v``: Trigonal (No Inversion)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* *d*: ``a1`` + ``e`` + ``e``, parametrized by ``10Dq``, ``Dσ``, ``Dτ``. The two
  ``e`` sets share an irrep and mix, so the Hamiltonian is **not** diagonal in
  the irrep basis (the off-diagonal element is
  :math:`-\tfrac{\sqrt2}{3}(3D\sigma - 5D\tau)`; see König & Kremer, p. 56).
* *f*: 2 ``a1`` + ``a2`` + 2 ``e``; the two ``a1`` sets mix through ``Ma1`` and the
  two ``e`` sets through ``Me`` (parameters ``Ea2``, ``Ea1A``, ``Ea1B``,
  ``Ee1``, ``Ee2``, ``Ma1``, ``Me``).

.. note::

    Because only even-\ :math:`k` harmonics enter the on-site crystal field, two
    point groups that differ only by an inversion center (for example ``D3d`` and
    ``C3v``, or ``Oh`` and ``Td`` for the *d*–*d* coupling apart from the sign)
    share the same ``Akm`` structure. This is why ``C3v`` can be taken over from
    the populated ``D3d`` Quanty page.

References
----------
* Quanty point-group tables: https://www.quanty.org/physics_chemistry/point_groups
* E. König and S. Kremer, *Ligand Field Energy Diagrams* (Plenum, 1977): the
  ``C3v`` and trigonal conventions.
