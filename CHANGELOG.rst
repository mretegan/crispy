=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

`Unreleased`_
=============

`0.8.0`_ - 2024-09-26
=====================

Changed
-------
- Complete rewrite to use a more flexible and modular architecture.

Fixed
-----
- Bugs and issues present in previous versions.

`0.7.4`_ - 2023-03-30
=====================

Fixed
-----
- PyPI installation issue.

`0.7.3`_ - 2019-06-26
=====================

Fixed
-----
- Various bug fixes.

`0.7.2`_ - 2019-02-01
=====================

Added
-----
- XES calculations for 3d transition metals.

Changed
-------
- Updated the bundled Quanty version in the package installers.

`0.7.1`_ - 2018-10-07
=====================

Added
-----
- Ligand field calculations for the lanthanides and actinides.
- MLCT term (in addition to the existing LMCT) for transition metals.

`0.7.0`_ - 2018-09-26
=====================

Added
-----
- Dialog to display details about the results.
- D3h symmetry.

Changed
-------
- Package installers now contain the 2018 Autumn version of Quanty.

`0.6.3`_ - 2018-06-11
=====================

Added
-----
- Restored the ligand-field term for Td symmetry.

Changed
-------
- Improved the documentation.
- Removed all loops from RIXS calculations.

`0.6.2`_ - 2018-06-08
=====================

Changed
-------
- Package installers now contain the 2018 Summer version of Quanty.
- Faster RIXS calculations.

`0.6.1`_ - 2018-06-05
=====================

Fixed
-----
- Various bug fixes.

`0.6.0`_ - 2018-06-03
=====================

Added
-----
- XPS calculations.
- Automatic update checks.

Changed
-------
- Updated the Quanty templates.

`0.5.0`_ - 2018-03-26
=====================

Added
-----
- Legend on the plot canvas.
- Preferences and about dialogs.
- New set of icons.
- Support for the first half of the 5f elements.

Changed
-------
- Calculation labels are now editable.
- Simplified the context menu for the results tab.

`0.4.2`_ - 2018-02-02
=====================

Fixed
-----
- Various bug fixes.

`0.4.0`_ - 2018-01-28
=====================

Added
-----
- Support for M4,5 (3d) XAS calculations for 4f elements.
- Support for XMCD and X(M)LD calculations.
- Support for polarization dependence.
- Energy-dependent broadening for L2,3 (2p) and M4,5 (3d) edges.

Changed
-------
- Spectra are now shifted by the experimental edge energy.
- Updated core-hole lifetimes.

`0.3.0`_ - 2017-10-10
=====================

Added
-----
- Support for L2,3 (2p) XAS, L2,3-M4,5 (2p3d), and L2,3-N4,5 (2p4d) RIXS
  calculations for 4f elements.
- Support for L2,3 (2p) XAS calculations for 4d and 5d elements.
- Support for K (1s) XAS calculations for C3v and Td symmetries, including
  3d-4p hybridization for 3d elements.
- Interactive Gaussian broadening for 1D and 2D spectra using FFT.

Changed
-------
- The number of initial Hamiltonian states is now determined automatically.
- Refactored the Quanty module.

`0.2.0`_ - 2017-04-25
=====================

Added
-----
- Support for K-L2,3 (1s2p) and L2,3-M4,5 (2p3d) RIXS calculations.
- Logging console displaying the output of the calculation.
- Context menu for the calculations panel.
- Calculations can now be serialized.

`0.1.0`_ - 2016-08-21
=====================

The first release of Crispy.

Added
-----
- Support for the calculation of core-level spectra using Quanty, including:

  - K (1s), L1 (2s), L2,3 (2p), M1 (3s), M2,3 (3p) XAS for transition metals
  - Oh and D4h symmetries
  - Crystal field and ligand field models

- Interactive plotting of the results.
- Abstract list model and tree model to display/modify the input parameters.

.. _Unreleased: https://github.com/mretegan/crispy/compare/v0.8.0...HEAD
.. _0.8.0: https://github.com/mretegan/crispy/compare/v0.7.4...v0.8.0
.. _0.7.4: https://github.com/mretegan/crispy/compare/v0.7.3...v0.7.4
.. _0.7.3: https://github.com/mretegan/crispy/compare/v0.7.2...v0.7.3
.. _0.7.2: https://github.com/mretegan/crispy/compare/v0.7.1...v0.7.2
.. _0.7.1: https://github.com/mretegan/crispy/compare/v0.7.0...v0.7.1
.. _0.7.0: https://github.com/mretegan/crispy/compare/v0.6.3...v0.7.0
.. _0.6.3: https://github.com/mretegan/crispy/compare/v0.6.2...v0.6.3
.. _0.6.2: https://github.com/mretegan/crispy/compare/v0.6.1...v0.6.2
.. _0.6.1: https://github.com/mretegan/crispy/compare/v0.6.0...v0.6.1
.. _0.6.0: https://github.com/mretegan/crispy/compare/v0.5.0...v0.6.0
.. _0.5.0: https://github.com/mretegan/crispy/compare/v0.4.2...v0.5.0
.. _0.4.2: https://github.com/mretegan/crispy/compare/v0.4.0...v0.4.2
.. _0.4.0: https://github.com/mretegan/crispy/compare/v0.3.0...v0.4.0
.. _0.3.0: https://github.com/mretegan/crispy/compare/v0.2.0...v0.3.0
.. _0.2.0: https://github.com/mretegan/crispy/compare/v0.1.0...v0.2.0
.. _0.1.0: https://github.com/mretegan/crispy/releases/tag/v0.1.0
