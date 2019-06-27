Changelog
=========

v0.7.3 (2019-06-26)
-------------------
This is a bug fixing release.

v0.7.2 (2019-02-01)
-------------------
What's new:

* XES calculations for 3d transition metals
* update the Quanty version in the package installers

v0.7.1 (2018-10-07)
-------------------
What's new:

* ligand field calculations for the lanthanides and actinides
* add MLCT (in addition to the existing LMCT) term to the transition metals

v0.7.0 (2018-09-26)
-------------------
What's new:

* a dialog to display details about the results
* D3h symmetry
* the package installers now contain the 2018 Autumn version of Quanty

v0.6.3 (2018-06-11)
-------------------
What's new:

* improved documentation
* removed all loops from RIXS calculations
* add back the ligand-field term for Td symmetry

v0.6.2 (2018-06-08)
-------------------
What's new:

* the package installers now contain the 2018 Summer version of Quanty
* speedup of the RIXS calculations

v0.6.1 (2018-06-05)
-------------------
This is a bug fix release.

v0.6.0 (2018-06-03)
-------------------
What's new:

* XPS calculations
* automatic check for updates
* important changes to Quanty templates

v0.5.0 (2018-03-26)
-------------------
What's new:

* editable calculations labels
* legend on the plot canvas
* preferences and about dialogs
* simplified context menu for the results tab
* new set of icons
* support for the first half of the 5f elements

v0.4.2 (2018-02-02)
-------------------
This is a bug fix release.

v0.4.0 (2018-01-28)
-------------------
What's new:

* support for M4,5 (3d) XAS calculations for 4f elements
* support for XMCD and X(M)LD calculations
* support for polarization dependence
* spectra are shifted by the experimental edge energy
* updated core-hole lifetimes
* energy dependent broadening for L2,3 (2p) and M4,5 (3d) edges

v0.3.0 (2017-10-10)
-------------------
What's new:

* support for L2,3 (2p) XAS, L2,3-M4,5 (2p3d) and L2,3-N4,5 (2p4d) RIXS calculations for 4f elements
* support for L2,3 (2p) XAS calculations for 4d and 5d elements
* support for K (1s) XAS calculations for C3v and Td symmetries including 3d-4p hybridization for 3d elements
* interactive Gaussian broadening for 1D and 2D spectra using FFT
* automatic determination of the number of initial Hamiltonian states

Changes:

* refactoring of the Quanty module by separating a class dealing with the calculation details from the widget class

v0.2.0 (2017-04-25)
-------------------
What's new:

* support for K-L2,3 (1s2p) and L2,3-M4,5 (2p3d) RIXS calculations
* logging console displaying the output of the calculation
* context menu for the calculations panel
* serialization of the calculations

v0.1.0 (2016-08-21)
-------------------
First release of Crispy:

* support for the calculation of core-level spectra using Quanty, including:

  * K (1s), L1 (2s), L2,3 (2p), M1 (3s), M2,3 (3p) XAS for transition metals
  * Oh and D4h symmetries
  * crystal field and ligand field models

* interactive plotting of the results
* abstract list model and tree model to display/modify the input parameters
