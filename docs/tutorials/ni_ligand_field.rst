2p XAS of Nickel Compounds: Towards a Multiconfigurational Treatment
====================================================================

The following tutorial illustrates the limitations of crystal field multiplets in reproducing the spectral features in a series of nickel compounds, and introduces the charge transfer multiplet, a more elaborate model that can overcome these limitations.

1. Crystal Field Multiplet Calculations
---------------------------------------
a. Calculate the 2p XAS spectrum of |Ni2+| using the default parameters. Make sure to include the *Crystal Field Term*. Identify the |L2| and |L3| edges.

b. Change the default scaling of the Slater integrals (κ) to 0.6, 0.4, and 0.2 and rerun the calculation. Overlay the four spectra and describe the evolution of the main peak and its high energy shoulder when the scaling parameter is decreased.

c. Compare the previous observation with the changes in the experimental spectra when going from fluoride to bromide in the series of nickel halides. How does the reduction factor and covalency of the metal-ligand bond correlate, knowing that the later increases with increasing atomic mass of the halide?

.. figure:: assets/laan_fig1.png
    :width: 60 %
    :align: center

    van der Laan et al., J. Phys. Rev. B, 1986, 33, 6.


d. For what reduction factor do you get the best agreement with the experiment spectrum of NiF. Is it reasonable to have to use this scaling factor?

e. Is there a particular region of the spectrum that doesn't seem to be reproduced using the previous crystal field multiplet calculations? 

.. |Ni2+| replace:: Ni\ :sup:`2+`\
.. |L2| replace:: L\ :sub:`2`\
.. |L3| replace:: L\ :sub:`3`\

2. The Charge Transfer Multiplet Model
--------------------------------------

a. Run a calculation using the following parameters (use the same values for the initial and final Hamiltonians): κ = 0.9, U(3d,3d) = 7.3 eV, U(2p,3d) = 8.5 eV (*Atomic Term*), 10Dq(3d) = 0.7 eV (*Crystal Field Term*), 10Dq(Ld) = 1.4 eV, Δ(3d,Ld) = 4.7 eV, Veg(3d,Ld) = 2.0 eV, Vt2g(3d,Ld) = 1.0 eV (*3d-Ligands Hybridization Term*). How does the simulated spectrum compare with the measured spectrum of NiO?

b. Repeat the above calculation while varying Δ between 0.0 and 10.0 eV. Notice the changes in the number of the metal 3d and the ligand electrons (<N_3d> and <N_Ld> in the logging window). What happens if Δ is negative?

c. Try to get a better agreement with the experimental spectrum of NiO by varying the crystal field parameters, 10Dq(3d) and 10Dq(Ld), and the hopping integrals, Veg(3d,Ld) and Vt2g(3d,Ld).
