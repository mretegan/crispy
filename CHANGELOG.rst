Changelog
=========

v2020.1rc0 (2020-11-12)
-----------------------
* Complete rewrite of the program to make it more modular.
* Added a Jupyter notebook interface.
* Added code to generate the atomic parameters and the Quanty templates.
* Changed the packaging to use PyInstaller for both Windows and macOS.

v0.7.3 (2019-06-26)
-------------------
* This is a bug fixing release.

v0.7.2 (2019-02-01)
-------------------
* Added XES calculations for 3d transition metals.
* Updated the Quanty version in the package installers.

v0.7.1 (2018-10-07)
-------------------
* Added ligand field calculations for the lanthanides and actinides.
* Added MLCT (in addition to the existing LMCT) term to the transition metals.

v0.7.0 (2018-09-26)
-------------------
* Added a dialog to display details about the results.
* Added the D3h symmetry.
* The package installers now contain the 2018 Autumn version of Quanty.

v0.6.3 (2018-06-11)
-------------------
* The documentation was improved.
* Removed all loops from RIXS calculations.
* Added back the ligand-field term for Td symmetry.

v0.6.2 (2018-06-08)
-------------------
* The package installers now contain the 2018 Summer version of Quanty.
* Speedup of the RIXS calculations.

v0.6.1 (2018-06-05)
-------------------
* This is a bug fix release.

v0.6.0 (2018-06-03)
-------------------
* Added XPS calculations.
* Updates are now automatically checked.
* The Quanty templates have been updated.

v0.5.0 (2018-03-26)
-------------------
* Made the calculations labels editable.
* Added legend on the plot canvas.
* Added preferences and about dialogs.
* Simplified context menu for the results tab.
* Added a new set of icons.
* Added support for the first half of the 5f elements.

v0.4.2 (2018-02-02)
-------------------
* This is a bug fix release.

v0.4.0 (2018-01-28)
-------------------
* Added support for M4,5 (3d) XAS calculations for 4f elements.
* Added support for XMCD and X(M)LD calculations.
* Added support for polarization dependence.
* Spectra are shifted by the experimental edge energy.
* Updated core-hole lifetimes.
* Added energy-dependent broadening for L2,3 (2p) and M4,5 (3d) edges.

v0.3.0 (2017-10-10)
-------------------
* Added support for L2,3 (2p) XAS, L2,3-M4,5 (2p3d) and L2,3-N4,5 (2p4d) RIXS calculations for 4f elements.
* Added support for L2,3 (2p) XAS calculations for 4d and 5d elements.
* Added support for K (1s) XAS calculations for C3v and Td symmetries including 3d-4p hybridization for 3d elements.
* Added interactive Gaussian broadening for 1D and 2D spectra using FFT.
* The number of initial Hamiltonian states is now determined automatically.
* The Quanty module was refactored.

v0.2.0 (2017-04-25)
-------------------
* Added support for K-L2,3 (1s2p) and L2,3-M4,5 (2p3d) RIXS calculations.
* Added a logging console displaying the output of the calculation.
* Added context menu for the calculations panel.
* The calculations can now be serialized.

v0.1.0 (2016-08-21)
-------------------
The first release of Crispy:

* Added support for the calculation of core-level spectra using Quanty, including:

  * K (1s), L1 (2s), L2,3 (2p), M1 (3s), M2,3 (3p) XAS for transition metals
  * Oh and D4h symmetries
  * crystal field and ligand field models

* Added interactive plotting of the results.
* Added an abstract list model and tree model to display/modify the input parameters.
