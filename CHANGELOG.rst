Changelog
=========

v0.4.0 (2018-01-28)
-------------------
What's new:

* support for M4,5 (3d) XAS simulations for 4f elements
* support for XMCD and X(M)LD simulations
* support for polarization dependence
* spectra are shifted by the experimental edge energy
* updated core-hole lifetimes
* energy dependent broadening for L2,3 and M4,5 edges


v0.3.0 (2017-10-10)
-------------------
What's new:

* support for L2,3 (2p) XAS, L2,3-M4,5 (2p3d) and L2,3-N4,5 (2p4d) RIXS simulations for 4f elements
* support for L2,3 (2p) XAS simulations for 4d and 5d elements
* support for K (1s) XAS simulations for C3v and Td symmetries including 3d-4p hybridization for 3d elements
* interactive Gaussian broadening for 1D and 2D spectra using FFT
* automatic determination of the number of initial Hamiltonian states

Changes:

* refactoring of the Quanty module by separating a class dealing with the simulation details from the widget class

v0.2.0 (2017-04-25)
-------------------
What's new:

* support for K-L2,3 (1s2p) and L2,3-M4,5 (2p3d) RIXS simulations
* logging console displaying the output of the calculation
* context menu for the simulations panel
* serialization of the simulations

v0.1.0 (2016-08-21)
-------------------
First release of Crispy:

* support for the simulation of core-level spectra using Quanty, including:

  * K (1s), L1 (2s), L2,3 (2p), M1 (3s), M2,3 (3p) XAS for transition metals
  * Oh and D4h symmetries
  * crystal field and ligand field models

* interactive plotting of the results
* abstract list model and tree model to display/modify the input parameters
