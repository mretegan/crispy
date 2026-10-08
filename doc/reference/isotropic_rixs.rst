Isotropic RIXS
==============
Supported Calculations
----------------------
The **Powder/Solution** option calculates an isotropic (orientation-averaged)
spectrum for RIXS edges with dipole transitions in both absorption and emission.
It supports 3d, 4d, and 5d transition metals, and 4f and 5f systems, in every
supported symmetry. This option is unavailable for RIXS edges with quadrupole
absorption.

Quanty Requirements
-------------------
Isotropic RIXS requires a Quanty version that supports ``Tensor=true`` in
``CreateResonantSpectra``.

Earlier Crispy versions with isotropic RIXS support used nine polarization
operators for absorption and nine for emission. That implementation did not
require these tensor options, but it was less efficient.

Single-crystal RIXS and the other spectroscopy calculations do not use these
resonant tensor options.

Calculation and Geometry
------------------------
Crispy supplies three Cartesian dipole operators (x, y, z) for absorption and
three for emission. From the resulting resonant tensor, it calculates two
fundamental spectra, A and B, that are independent of the scattering geometry.

Crispy combines these spectra as ``A + B * factor`` to calculate the isotropic
spectrum. The geometry factor depends on the **Resolve** polarization option:

* When enabled, the factor is the squared projection of the incoming
  polarization onto the outgoing polarization.
* When disabled, the factor is half of the difference between one and the squared
  projection of the incoming polarization onto the outgoing wave vector.
