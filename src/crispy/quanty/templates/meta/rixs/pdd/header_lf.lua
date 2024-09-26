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
Temperature = $Temperature -- Temperature (Kelvin).

NPsis = $NPsis -- Number of states to consider in the spectra calculation.
NPsisAuto = $NPsisAuto -- Determine the number of state automatically.
NConfigurations = $NConfigurations -- Number of configurations.

-- X-axis parameters.
Emin1 = $XEmin -- Minimum value of the energy range (eV).
Emax1 = $XEmax -- Maximum value of the energy range (eV).
NPoints1 = $XNPoints -- Number of points of the spectra.
ZeroShift1 = $XZeroShift -- Shift that brings the edge or line energy to approximately zero (eV).
ExperimentalShift1 = $XExperimentalShift -- Experimental edge or line energy (eV).
Gaussian1 = $XGaussian -- Gaussian FWHM (eV).
Gamma1 = $XGamma -- Lorentzian FWHM used in the spectra calculation (eV).

WaveVectorIn = $XWaveVector -- Incident wave vector.
EpsSigmaIn = $XFirstPolarization -- Incident sigma polarization.
EpsPiIn = $XSecondPolarization -- Incident pi polarization.

-- Y-axis parameters.
Emin2 = $YEmin -- Minimum value of the energy range (eV).
Emax2 = $YEmax -- Maximum value of the energy range (eV).
NPoints2 = $YNPoints -- Number of points of the spectra.
ZeroShift2 = $YZeroShift -- Shift that brings the edge or line energy to approximately zero (eV).
ExperimentalShift2 = $YExperimentalShift -- Experimental edge or line energy (eV).
Gaussian2 = $YGaussian -- Gaussian FWHM (eV).
Gamma2 = $YGamma -- Lorentzian FWHM used in the spectra calculation (eV).

WaveVectorOut = $YWaveVector -- Scattered wave vector.
EpsSigmaOut = $YFirstPolarization -- Scattered sigma polarization.
EpsPiOut = $YSecondPolarization -- Scattered pi polarization.

SpectraToCalculate = $SpectraToCalculate -- Types of spectra to calculate.
DenseBorder = $DenseBorder -- Number of determinants where we switch from dense methods to sparse methods.
ShiftSpectra = $ShiftSpectra -- If enabled, shift the spectra in the experimental energy range.

Prefix = "$Prefix" -- File name prefix.

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
AtomicTerm = $AtomicTerm
CrystalFieldTerm = $CrystalFieldTerm
LmctLigandsHybridizationTerm = $LmctLigandsHybridizationTerm
MlctLigandsHybridizationTerm = $MlctLigandsHybridizationTerm
MagneticFieldTerm = $MagneticFieldTerm
ExchangeFieldTerm = $ExchangeFieldTerm

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_#i = 6
NElectrons_#m = $NElectrons_#m

IndexDn_#i = {0, 2, 4}
IndexUp_#i = {1, 3, 5}
IndexDn_#m = {6, 8, 10, 12, 14}
IndexUp_#m = {7, 9, 11, 13, 15}

if LmctLigandsHybridizationTerm then
    NFermions = 26

    NElectrons_L1 = 10

    IndexDn_L1 = {16, 18, 20, 22, 24}
    IndexUp_L1 = {17, 19, 21, 23, 25}
end

if MlctLigandsHybridizationTerm then
    NFermions = 26

    NElectrons_L2 = 0

    IndexDn_L2 = {16, 18, 20, 22, 24}
    IndexUp_L2 = {17, 19, 21, 23, 25}
end

if LmctLigandsHybridizationTerm and MlctLigandsHybridizationTerm then
    return
end

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_m = 0
H_f = 0
