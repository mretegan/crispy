Supported Systems
==================

Crispy generates Quanty input for core-level spectroscopy calculations on a
single absorbing ion. The element, charge, symmetry, experiment, and edge are
chosen on the *General Setup* page; the combinations available there are listed
below.

Absorbing Ions
--------------
Calculations are organized by the **valence shell** of the absorbing ion.

.. list-table::
    :header-rows: 1
    :widths: 14 16 70

    * - Valence shell
      - Elements
      - Notes
    * - ``3d``
      - Sc – Cu
      - First-row transition metals.
    * - ``4d``
      - Y – Ag
      - Second-row transition metals.
    * - ``5d``
      - Hf – Au
      - Third-row transition metals.
    * - ``4f``
      - La – Yb
      - Lanthanides.
    * - ``5f``
      - Ac – Cm
      - Actinides.

The available oxidation states (charges) depend on the element and are offered
in the charge selector.

Experiments and Edges
---------------------
The edges available for each valence shell and experiment:

**3d transition metals**

* **XAS / XPS** — K (1s), L\ :sub:`1` (2s), L\ :sub:`2,3` (2p), M\ :sub:`1` (3s), M\ :sub:`2,3` (3p)
* **XES** — Kα (1s2p), Kβ (1s3p)
* **RIXS** — K-L\ :sub:`2,3` (1s2p), K-M\ :sub:`2,3` (1s3p), L\ :sub:`2,3`-M\ :sub:`4,5` (2p3d)

**4d transition metals**

* **XAS** — L\ :sub:`1` (2s), L\ :sub:`2,3` (2p), M\ :sub:`1` (3s), M\ :sub:`2,3` (3p), N\ :sub:`1` (4s), N\ :sub:`2,3` (4p)
* **XPS** — the XAS edges and M\ :sub:`4,5` (3d)
* **RIXS** — L\ :sub:`2,3`-N\ :sub:`4,5` (2p4d)

**5d transition metals**

* **XAS** — L\ :sub:`1` (2s), L\ :sub:`2,3` (2p), M\ :sub:`1` (3s), M\ :sub:`2,3` (3p), N\ :sub:`1` (4s), N\ :sub:`2,3` (4p), O\ :sub:`1` (5s), O\ :sub:`2,3` (5p)
* **XPS** — the XAS edges and M\ :sub:`4,5` (3d), N\ :sub:`4,5` (4d)
* **RIXS** — L\ :sub:`2,3`-O\ :sub:`4,5` (2p5d)

**4f lanthanides**

* **XAS / XPS** — L\ :sub:`2,3` (2p), M\ :sub:`2,3` (3p), M\ :sub:`4,5` (3d), N\ :sub:`2,3` (4p), N\ :sub:`4,5` (4d)
* **RIXS** — L\ :sub:`2,3`-M\ :sub:`4,5` (2p3d), L\ :sub:`2,3`-N\ :sub:`4,5` (2p4d), M\ :sub:`4,5`-N\ :sub:`6,7` (3d4f)

**5f actinides**

* **XAS / XPS** — L\ :sub:`2,3` (2p), M\ :sub:`2,3` (3p), M\ :sub:`4,5` (3d), N\ :sub:`2,3` (4p), N\ :sub:`4,5` (4d)
* **RIXS** — L\ :sub:`2,3`-M\ :sub:`4,5` (2p3d), L\ :sub:`2,3`-N\ :sub:`4,5` (2p4d), M\ :sub:`4,5`-O\ :sub:`6,7` (3d5f)

Point-Group Symmetries
----------------------
The local symmetry of the absorbing site can be one of:

``Oh``, ``Td``, ``D4h``, ``D3h``, ``D3d``, ``C3v``.

Each fixes the crystal-field splitting and the parameters exposed in the
*Crystal Field* term. The orientation conventions (how the *x*, *y*, *z* axes are
attached to the symmetry elements) and the splitting for every geometry are
documented in :doc:`Symmetry, the crystal field, and the choice of axes
</user_guide/crystal_field>`.

Hamiltonian Terms
-----------------
Depending on the ion and symmetry, the following terms can be enabled in the
*Hamiltonian Setup*:

* **Atomic** — Slater integrals (F\ :sup:`k`, G\ :sup:`k`) and spin-orbit
  coupling (always available).
* **Crystal Field** — the point-group crystal field (always available).
* **Ligands Hybridization (LMCT / MLCT)** — charge-transfer with a ligand shell;
  available for ``Oh`` and ``D4h`` in the *d* block and ``Oh`` in the *f* block.
* **3d–4p Hybridization** — for the K (1s) pre-edge in the non-centrosymmetric
  ``Td`` and ``C3v`` *d*-block cases.
* **Magnetic Field** and **Exchange Field** — always available.
