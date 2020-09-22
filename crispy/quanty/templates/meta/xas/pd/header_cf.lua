--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: #f
-- symmetry: #symmetry
-- experiment: #experiment
-- edge: #edge
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- Set the verbosity of the calculation. For increased verbosity use the values
-- 0x00FF or 0xFFFF.
--------------------------------------------------------------------------------
Verbosity($Verbosity)

--------------------------------------------------------------------------------
-- Define the parameters of the calculation.
--------------------------------------------------------------------------------
Temperature = $Temperature -- Temperature (Kelvin)

NPsis = $NPsis  -- Number of states to calculate
NPsisAuto = $NPsisAuto  -- Determine the number of state automatically
NConfigurations = $NConfigurations  -- Number of configurations

Emin = $XEmin  -- Minimum value of the energy range (eV)
Emax = $XEmax  -- Maximum value of the energy range (eV)
NPoints = $XNPoints  -- Number of points of the spectra
ExperimentalShift = $XExperimentalShift  -- Experimental edge energy (eV)
ZeroShift = $XZeroShift  -- Energy required to shift the calculated spectrum to start from approximately zero (eV)
Gaussian = $XGaussian  -- Gaussian FWHM (eV)
Lorentzian = $XLorentzian  -- Lorentzian FWHM (eV)

WaveVector = $XWaveVector  -- Wave vector
Ev = $XFirstPolarization  -- Vertical polarization
Eh = $XSecondPolarization  -- Horizontal polarization

SpectraToCalculate = $SpectraToCalculate  -- Type of spectra to calculate
DenseBorder = $DenseBorder -- Number of determinants where we switch from dense methods to sparse methods

Prefix = "$Prefix"  -- File name prefix

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
AtomicTerm = $AtomicTerm
CrystalFieldTerm = $CrystalFieldTerm
MagneticFieldTerm = $MagneticFieldTerm
ExchangeFieldTerm = $ExchangeFieldTerm

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_#i = 6
NElectrons_#f = $NElectrons_#f

IndexDn_#i = {0, 2, 4}
IndexUp_#i = {1, 3, 5}
IndexDn_#f = {6, 8, 10, 12, 14}
IndexUp_#f = {7, 9, 11, 13, 15}

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0