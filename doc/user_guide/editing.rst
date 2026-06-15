Editing a Calculation
=====================

The General Setup page exposes five combo boxes that define a calculation: the
**element** (symbol), **charge**, **symmetry**, **experiment**, and **edge**.
Changing any of them rebuilds the calculation. To avoid discarding the values
you have entered, Crispy keeps the parameters that still apply and regenerates
only the ones that depend on what changed.

The table below lists, for each combo box, which parameters are kept (✓) and
which are reset to their defaults (✗) when that combo box is changed.

.. list-table::
    :header-rows: 1
    :stub-columns: 1

    * - Parameter
      - Symbol
      - Charge
      - Symmetry
      - Experiment
      - Edge
    * - Temperature
      - ✓
      - ✓
      - ✓
      - ✓
      - ✓
    * - Magnetic field
      - ✓
      - ✓
      - ✓
      - ✓
      - ✓
    * - Gaussian broadening
      - ✓
      - ✓
      - ✓
      - ✓
      - ✓
    * - Energy limits, Lorentzian, wave vector, polarization, scale/normalization
      - ✗
      - ✓
      - ✓
      - ✗
      - ✗
    * - Spectra to calculate
      - ✗
      - ✓
      - ✓
      - ✗
      - ✗
    * - Atomic term (Slater integrals, spin-orbit coupling)
      - ✗
      - ✗
      - ✓
      - ✗
      - ✗
    * - Crystal field term
      - ✗
      - ✓
      - ✗
      - ✗
      - ✗
    * - Ligand and pd hybridization terms
      - ✗
      - ✓
      - ✗
      - ✗
      - ✗
    * - Exchange field term
      - ✗
      - ✓
      - ✓
      - ✗
      - ✗
    * - Scale factors (Fk, Gk, Zeta)
      - ✗
      - ✓
      - ✓
      - ✗
      - ✗
    * - Synchronize parameters
      - ✗
      - ✓
      - ✓
      - ✗
      - ✗
    * - Number of states
      - ✗
      - ✗
      - ✓
      - ✗
      - ✗
    * - Number of configurations
      - ✗
      - ✗
      - ✗
      - ✗
      - ✗

In short, changing the **charge** or the **symmetry** keeps almost everything
and resets only the pieces that genuinely depend on the new oxidation state or
point group. Changing the **element**, **experiment**, or **edge** keeps only
the experimental conditions (temperature, magnetic field, and Gaussian
broadening) and rebuilds the rest.

.. note::

    Selecting a previously computed result on the Results page restores **all**
    of its parameters, regardless of the table above.

A few entries deserve clarification:

* **Magnetic field.** The magnitude is always kept. When the beam geometry can
  change (element, experiment, or edge), the field is re-projected onto the new
  wave vector. A zero field leaves the magnetic field term disabled.
* **Gaussian broadening.** It is kept for the incident-energy axis. For RIXS the
  energy-transfer axis broadening is kept only when the calculation stays
  two-dimensional; switching to or from RIXS keeps only the incident-energy
  value.
* **Scale factors.** When the charge changes, the kept Fk, Gk, and Zeta are
  re-applied to the regenerated atomic parameters so that their individual scale
  factors stay consistent.
