--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: #m
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
Temperature = $Temperature -- temperature (Kelvin)

NPsis = $NPsis  -- number of states to consider in the spectra calculation
NPsisAuto = $NPsisAuto  -- determine the number of state automatically
NConfigurations = $NConfigurations  -- number of configurations

-- X-axis parameters
Emin1 = $XEmin  -- minimum value of the energy range (eV)
Emax1 = $XEmax  -- maximum value of the energy range (eV)
NPoints1 = $XNPoints  -- number of points of the spectra
ExperimentalShift1 = $XExperimentalShift  -- experimental edge energy (eV)
Gaussian1 = $XGaussian  -- Gaussian FWHM (eV)
Gamma1 = $XGamma  -- Lorentzian FWHM used in the spectra calculation (eV)

WaveVector = $XWaveVector  -- wave vector
Ev = $XFirstPolarization  -- vertical polarization
Eh = $XSecondPolarization  -- horizontal polarization

-- Y-axis parameters
Emin2 = $YEmin  -- minimum value of the energy range (eV)
Emax2 = $YEmax  -- maximum value of the energy range (eV)
NPoints2 = $YNPoints  -- number of points of the spectra
ExperimentalShift2 = $YExperimentalShift  -- experimental edge energy (eV)
Gaussian2 = $YGaussian  -- Gaussian FWHM (eV)
Gamma2 = $YGamma  -- Lorentzian FWHM used in the spectra calculation (eV)

WaveVector = $YWaveVector  -- wave vector
Ev = $YFirstPolarization  -- vertical polarization
Eh = $YSecondPolarization  -- horizontal polarization

SpectraToCalculate = $SpectraToCalculate  -- types of spectra to calculate
DenseBorder = $DenseBorder -- number of determinants where we switch from dense methods to sparse methods

Prefix = "$Prefix"  -- file name prefix

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
AtomicTerm = $AtomicTerm
CrystalFieldTerm = $CrystalFieldTerm
LmctLigandsHybridizationTerm = $LmctLigandsHybridizationTerm
MagneticFieldTerm = $MagneticFieldTerm
ExchangeFieldTerm = $ExchangeFieldTerm

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 30

NElectrons_#i = 6
NElectrons_#f = 10
NElectrons_#m = $NElectrons_#m

IndexDn_#i = {0, 2, 4}
IndexUp_#i = {1, 3, 5}
IndexDn_#f = {6, 8, 10, 12, 14}
IndexUp_#f = {7, 9, 11, 13, 15}
IndexDn_#m = {16, 18, 20, 22, 24, 26, 28}
IndexUp_#m = {17, 19, 21, 23, 25, 27, 29}

if LmctLigandsHybridizationTerm then
    NFermions = 44

    NElectrons_L1 = 14

    IndexDn_L1 = {30, 32, 34, 36, 38, 40, 42}
    IndexUp_L1 = {31, 33, 35, 37, 39, 41, 43}
end

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_m = 0
H_f = 0