Calculating the |L2,3| XAS of |Ti4+|
====================================

In this tutorial, the calculation of the |L2,3| absorption spectrum of |Ti4+|, resulting from 2p to 3d electronic dipole transitions, is used to illustrates some of the fundamental concepts in using multiplet calculations as a tool to interpret experimental data. As can be seen from the figure below the spectrum calculated using multiplet theory can be in very good agreement with the experimental spectrum (dotted).

.. figure:: assets/degroot_fig7.png
    :width: 60 %
    :align: center

    de Groot et al., Phys. Rev. B., 1990, 41 (2), 928--937.

Atomic Multiplet
----------------
1. Calculate the XAS spectrum at the |L2,3| edges of |Ti4+| in spherical symmetry, i.e. using an atomic representation of the system. For this you need to exclude the crystal field contribution from the Hamiltonian. In addition set the Lorentzian broadening to 0.1, and the Gaussian broadening to 0.0. Leave all the other parameters to their default values. How many transitions are visible in the spectrum? Identify the |L2| and |L3| edges.

    **Note**: What is the initial electronic configuration of |Ti4+|? How many multi-electronic states does this configuration have? Write down their spectroscopic terms. Repeat the same exercise for the final electronic configuration. Using the selection rules for dipole transitions (Δ\ *J* = 0, ±1 except for *J* = *J*\ ' = 0) how many transitions do you expect?

2. In semi-empirical multiplet calculations, the Hamiltonian parameters are varied to improve the agreement with experiment. In the case of the atomic parameters, i.e. Slater integrals and spin orbit coupling constants, instead of modifying the parameters themselves, it is customary to use scaling factors to change them. Run a calculation with the scaling of the 2p spin orbit coupling constant, ζ(2p), set to 0.5. After the calculation finishes, set this value back to 1.0, and run a second calculation with the 3d spin orbit coupling, ζ(3d), in the *Final Hamiltonian* set to 0.5. Which interaction affects the most the energy separation between the |L2| and |L3| edges? Check that the energy separation between the two edges is close to 3/2·ζ(2p).

3. Change back the scaling parameter to 1.0 for both 2p and 3d spin orbit coupling. Perform three calculations using 0.8, 0.4, and 0.0 for the scaling of the Slater integrals, |Fk| and |Gk|. Instead of changing each scaling value individually as before, use the input boxes above the Hamiltonian terms. Plot the three spectra. What is the influence of the electronic repulsions on the spectrum? Check that in the last case, with the scaling factors set to zero, the intensity ratio of the |L3|/|L2| also called the branching ratio, is close to 2:1.

Crystal Field Multiplet
-----------------------
1. Set the scaling factors for the Slater integrals back to 0.8. Enable the *Crystal Field* and change the 10Dq value to 2.0 eV for both the initial and final Hamiltonian. In octahedral symmetry, the crystal field splitting 10Dq is also written |DeltaO|. Run the calculation and compare with the case of spherical symmetry. How many transitions do you observe at the |L3| edge? How many transitions at the |L2| edge?

2. In the previous calculation the Lorentzian broadening was set to 0.1 eV to better identify the number of transitions. Change it to 0.2 eV and run the calculation. Observe its effect on the final spectrum.

3. Until now we have used the same Lorentzian broadening for both |L2| and |L3| edges. In reality the width of the 2p core hole, which is related to the lifetime, is larger at the |L2| edge than at the |L3| edge. Change the Lorentzian broadening to 0.2, 0.4, 460. This will apply a 0.2 eV broadening at the |L3| edge, a 0.4 eV at the |L2| edge, and will change between the two broadenings at 460 eV. Run the calculation and compare it with the previous spectrum.

4. Run a set of calculations with 10Dq ranging from 0 to 2.0 eV, in steps of 0.5 eV. Plot the resulting spectra. What is the influence of the crystal field splitting?

5. Set the 10Dq value to 2.0 eV and switch off the Slater integrals and the 3d spin-orbit coupling. How many transitions does the calculated spectrum have? Check if their intensity ratio is close to 6:4:3:2, i.e. the theoretical ratio given by the degeneracy of the 3d orbitals (3:2) and the branching ratio discussed before (2:1). What is the energy separation between the first two transitions? How does this compare to the energy separation between the last two transitions.

Adding Tetragonal Distortion
----------------------------
1. Next we are going to study the influence of a tetragonal distortion, i.e. an elongation or compression along one of the four fold axes. Lowering the symmetry from |Oh| to |D4h|, results in a different energy splitting of the 3d orbitals as can be seen in the figure below. The relative energy position of the orbitals depends on the distortion applied to the octahedron and is determined by two parameters Ds and Dt, in addition to the Dq parameter.

.. image:: assets/orbitals_diagram.png
    :width: 60 %
    :align: center

2. Change the symmetry of the system to |D4h|. Note that by doing this all parameters will be reset to their default values. Set the Dq value to 0.25 eV. This is equivalent to setting the 10Dq value to 2.5 eV in the case of the |Oh| symmetry. While keeping Dt zero, vary the value of Ds between -0.6 and 0.6 eV in steps of 0.2 eV. Try to rationalize the changes you observe in the spectrum. Do a similar test for Dt while keeping Ds zero.

.. |L2,3| replace:: L\ :sub:`2,3`\
.. |Ti4+| replace:: Ti\ :sup:`4+`\
.. |L2| replace:: L\ :sub:`2`\
.. |L3| replace:: L\ :sub:`3`\
.. |Fk| replace:: F\ :sub:`k`\
.. |Gk| replace:: G\ :sub:`k`\
.. |DeltaO| replace:: Δ\ :sub:`O`\
.. |2p3/2| replace:: 2p\ :sub:`3/2`\
.. |2p1/2| replace:: 2p\ :sub:`1/2`\
.. |3d(eg)| replace:: 3d(e\ :sub:`g`)\
.. |3d(t2g)| replace:: 3d(t\ :sub:`2g`)\
.. |Oh| replace:: O\ :sub:`h`\
.. |D4h| replace:: D\ :sub:`4h`\
