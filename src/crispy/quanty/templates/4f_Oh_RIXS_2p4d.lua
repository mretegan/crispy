--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4f
-- symmetry: Oh
-- experiment: RIXS
-- edge: L2,3-N4,5 (2p4d)
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
MagneticFieldTerm = $MagneticFieldTerm
ExchangeFieldTerm = $ExchangeFieldTerm

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 30

NElectrons_2p = 6
NElectrons_4d = 10
NElectrons_4f = $NElectrons_4f

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_4d = {6, 8, 10, 12, 14}
IndexUp_4d = {7, 9, 11, 13, 15}
IndexDn_4f = {16, 18, 20, 22, 24, 26, 28}
IndexUp_4f = {17, 19, 21, 23, 25, 27, 29}

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

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2p = NewOperator("Number", NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_4d = NewOperator("Number", NFermions, IndexUp_4d, IndexUp_4d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_4d, IndexDn_4d, {1, 1, 1, 1, 1})

N_4f = NewOperator("Number", NFermions, IndexUp_4f, IndexUp_4f, {1, 1, 1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_4f, IndexDn_4f, {1, 1, 1, 1, 1, 1, 1})

if AtomicTerm then
    F0_4f_4f = NewOperator("U", NFermions, IndexUp_4f, IndexDn_4f, {1, 0, 0, 0})
    F2_4f_4f = NewOperator("U", NFermions, IndexUp_4f, IndexDn_4f, {0, 1, 0, 0})
    F4_4f_4f = NewOperator("U", NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 1, 0})
    F6_4f_4f = NewOperator("U", NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 0, 1})
  
    F0_2p_4f = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {1, 0}, {0, 0})
    F2_2p_4f = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {0, 1}, {0, 0})
    G2_2p_4f = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {0, 0}, {1, 0})
    G4_2p_4f = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {0, 0}, {0, 1})
  
    F0_4d_4f = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {1, 0, 0}, {0, 0, 0});
    F2_4d_4f = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 1, 0}, {0, 0, 0});
    F4_4d_4f = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 1}, {0, 0, 0});
    G1_4d_4f = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {1, 0, 0});
    G3_4d_4f = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 1, 0});
    G5_4d_4f = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 0, 1});

    U_4f_4f_i  = $U(4f,4f)_i_value
    F2_4f_4f_i = $F2(4f,4f)_i_value * $F2(4f,4f)_i_scaleFactor
    F4_4f_4f_i = $F4(4f,4f)_i_value * $F4(4f,4f)_i_scaleFactor
    F6_4f_4f_i = $F6(4f,4f)_i_value * $F6(4f,4f)_i_scaleFactor
    F0_4f_4f_i = U_4f_4f_i + 4 / 195 * F2_4f_4f_i + 2 / 143 * F4_4f_4f_i + 100 / 5577 * F6_4f_4f_i

    U_4f_4f_m  = $U(4f,4f)_m_value
    F2_4f_4f_m = $F2(4f,4f)_m_value * $F2(4f,4f)_m_scaleFactor
    F4_4f_4f_m = $F4(4f,4f)_m_value * $F4(4f,4f)_m_scaleFactor
    F6_4f_4f_m = $F6(4f,4f)_m_value * $F6(4f,4f)_m_scaleFactor
    F0_4f_4f_m = U_4f_4f_m + 4 / 195 * F2_4f_4f_m + 2 / 143 * F4_4f_4f_m + 100 / 5577 * F6_4f_4f_m
    U_2p_4f_m  = $U(2p,4f)_m_value
    F2_2p_4f_m = $F2(2p,4f)_m_value * $F2(2p,4f)_m_scaleFactor
    G2_2p_4f_m = $G2(2p,4f)_m_value * $G2(2p,4f)_m_scaleFactor
    G4_2p_4f_m = $G4(2p,4f)_m_value * $G4(2p,4f)_m_scaleFactor
    F0_2p_4f_m = U_2p_4f_m + 3 / 70 * G2_2p_4f_m + 2 / 63 * G4_2p_4f_m

    U_4f_4f_f  = $U(4f,4f)_f_value
    F2_4f_4f_f = $F2(4f,4f)_f_value * $F2(4f,4f)_f_scaleFactor
    F4_4f_4f_f = $F4(4f,4f)_f_value * $F4(4f,4f)_f_scaleFactor
    F6_4f_4f_f = $F6(4f,4f)_f_value * $F6(4f,4f)_f_scaleFactor
    F0_4f_4f_f = U_4f_4f_f + 4 / 195 * F2_4f_4f_f + 2 / 143 * F4_4f_4f_f + 100 / 5577 * F6_4f_4f_f
    U_4d_4f_f  = $U(4d,4f)_f_value
    F2_4d_4f_f = $F2(4d,4f)_f_value * $F2(4d,4f)_f_scaleFactor
    F4_4d_4f_f = $F4(4d,4f)_f_value * $F4(4d,4f)_f_scaleFactor
    G1_4d_4f_f = $G1(4d,4f)_f_value * $G1(4d,4f)_f_scaleFactor
    G3_4d_4f_f = $G3(4d,4f)_f_value * $G3(4d,4f)_f_scaleFactor
    G5_4d_4f_f = $G5(4d,4f)_f_value * $G5(4d,4f)_f_scaleFactor
    F0_4d_4f_f = U_4d_4f_f + 3 / 70 * G1_4d_4f_f + 2 / 105 * G3_4d_4f_f + 5 / 231 * G5_4d_4f_f

    H_i = H_i + Chop(
          F0_4f_4f_i * F0_4f_4f
        + F2_4f_4f_i * F2_4f_4f
        + F4_4f_4f_i * F4_4f_4f
        + F6_4f_4f_i * F6_4f_4f)

    H_m = H_m + Chop(
          F0_4f_4f_m * F0_4f_4f
        + F2_4f_4f_m * F2_4f_4f
        + F4_4f_4f_m * F4_4f_4f
        + F6_4f_4f_m * F6_4f_4f
        + F0_2p_4f_m * F0_2p_4f
        + F2_2p_4f_m * F2_2p_4f
        + G2_2p_4f_m * G2_2p_4f
        + G4_2p_4f_m * G4_2p_4f)

    H_f = H_f + Chop(
          F0_4f_4f_f * F0_4f_4f
        + F2_4f_4f_f * F2_4f_4f
        + F4_4f_4f_f * F4_4f_4f
        + F6_4f_4f_f * F6_4f_4f
        + F0_4d_4f_f * F0_4d_4f
        + F2_4d_4f_f * F2_4d_4f
        + F4_4d_4f_f * F4_4d_4f
        + G1_4d_4f_f * G1_4d_4f
        + G3_4d_4f_f * G3_4d_4f
        + G5_4d_4f_f * G5_4d_4f)

    ldots_4f = NewOperator("ldots", NFermions, IndexUp_4f, IndexDn_4f)

    ldots_2p = NewOperator("ldots", NFermions, IndexUp_2p, IndexDn_2p)

    ldots_4d = NewOperator("ldots", NFermions, IndexUp_4d, IndexDn_4d)

    zeta_4f_i = $zeta(4f)_i_value * $zeta(4f)_i_scaleFactor

    zeta_4f_m = $zeta(4f)_m_value * $zeta(4f)_m_scaleFactor
    zeta_2p_m = $zeta(2p)_m_value * $zeta(2p)_m_scaleFactor

    zeta_4f_f = $zeta(4f)_f_value * $zeta(4f)_f_scaleFactor
    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_4f_i * ldots_4f)

    H_m = H_m + Chop(
          zeta_4f_m * ldots_4f
        + zeta_2p_m * ldots_2p)

    H_f = H_f + Chop(
          zeta_4f_f * ldots_4f
        + zeta_4d_f * ldots_4d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Eav_4f_i = ($Ea2u(4f)_i_value + 3 * $Et1u(4f)_i_value + 3 * $Et2u(4f)_i_value) / 7
    Ea2u_4f_i = $Ea2u(4f)_i_value - Eav_4f_i
    Et1u_4f_i = $Et1u(4f)_i_value - Eav_4f_i
    Et2u_4f_i = $Et2u(4f)_i_value - Eav_4f_i

    Akm_4f_i = {
        {0, 0, (1 / 7) * (Ea2u_4f_i + (3) * (Et1u_4f_i + Et2u_4f_i))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_4f_i) + (-3) * (Et1u_4f_i) + Et2u_4f_i)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_4f_i) + (-3) * (Et1u_4f_i) + Et2u_4f_i))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_4f_i) + (-3) * (Et1u_4f_i) + Et2u_4f_i))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_4f_i) + (5) * (Et1u_4f_i) + (-9) * (Et2u_4f_i))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_4f_i) + (5) * (Et1u_4f_i) + (-9) * (Et2u_4f_i)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_4f_i) + (5) * (Et1u_4f_i) + (-9) * (Et2u_4f_i)))}
    }

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a2u     %8.3f\n", Ea2u_4f_i))
    io.write(string.format("t1u     %8.3f\n", Et1u_4f_i))
    io.write(string.format("t2u     %8.3f\n", Et2u_4f_i))
    io.write("================\n")
    io.write("\n")

    Eav_4f_m = ($Ea2u(4f)_m_value + 3 * $Et1u(4f)_m_value + 3 * $Et2u(4f)_m_value) / 7
    Ea2u_4f_m = $Ea2u(4f)_m_value - Eav_4f_m
    Et1u_4f_m = $Et1u(4f)_m_value - Eav_4f_m
    Et2u_4f_m = $Et2u(4f)_m_value - Eav_4f_m

    Akm_4f_m = {
        {0, 0, (1 / 7) * (Ea2u_4f_m + (3) * (Et1u_4f_m + Et2u_4f_m))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_4f_m) + (-3) * (Et1u_4f_m) + Et2u_4f_m)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_4f_m) + (-3) * (Et1u_4f_m) + Et2u_4f_m))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_4f_m) + (-3) * (Et1u_4f_m) + Et2u_4f_m))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_4f_m) + (5) * (Et1u_4f_m) + (-9) * (Et2u_4f_m))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_4f_m) + (5) * (Et1u_4f_m) + (-9) * (Et2u_4f_m)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_4f_m) + (5) * (Et1u_4f_m) + (-9) * (Et2u_4f_m)))}
    }

    Eav_4f_f = ($Ea2u(4f)_f_value + 3 * $Et1u(4f)_f_value + 3 * $Et2u(4f)_f_value) / 7
    Ea2u_4f_f = $Ea2u(4f)_f_value - Eav_4f_f
    Et1u_4f_f = $Et1u(4f)_f_value - Eav_4f_f
    Et2u_4f_f = $Et2u(4f)_f_value - Eav_4f_f

    Akm_4f_f = {
        {0, 0, (1 / 7) * (Ea2u_4f_f + (3) * (Et1u_4f_f + Et2u_4f_f))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_4f_f) + (-3) * (Et1u_4f_f) + Et2u_4f_f)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_4f_f) + (-3) * (Et1u_4f_f) + Et2u_4f_f))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_4f_f) + (-3) * (Et1u_4f_f) + Et2u_4f_f))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_4f_f) + (5) * (Et1u_4f_f) + (-9) * (Et2u_4f_f))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_4f_f) + (5) * (Et1u_4f_f) + (-9) * (Et2u_4f_f)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_4f_f) + (5) * (Et1u_4f_f) + (-9) * (Et2u_4f_f)))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_f))
end

--------------------------------------------------------------------------------
-- Define the 4f-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1, 1, 1})

    Delta_4f_L1_i = $Delta(4f,L1)_i_value
    E_4f_i = (28 * Delta_4f_L1_i - 27 * U_4f_4f_i * NElectrons_4f - U_4f_4f_i * NElectrons_4f^2) / (2 * (14 + NElectrons_4f))
    E_L1_i = NElectrons_4f * (-2 * Delta_4f_L1_i + U_4f_4f_i * NElectrons_4f + U_4f_4f_i) / (2 * (NElectrons_4f + 14))

    Delta_4f_L1_m = $Delta(4f,L1)_m_value
    E_4f_m = (28 * Delta_4f_L1_m - U_4f_4f_m * NElectrons_4f^2 - 39 * U_4f_4f_m * NElectrons_4f - 228 * U_2p_4f_m) / (2 * (NElectrons_4f + 20))
    E_2p_m = (28 * Delta_4f_L1_m + U_4f_4f_m * NElectrons_4f^2 + U_4f_4f_m * NElectrons_4f - 2 * U_2p_4f_m * NElectrons_4f^2 - 30 * U_2p_4f_m * NElectrons_4f - 28 * U_2p_4f_m) / (2 * (NElectrons_4f + 20))
    E_L1_m = (-2 * Delta_4f_L1_m * NElectrons_4f - 12 * Delta_4f_L1_m + U_4f_4f_m * NElectrons_4f^2 + U_4f_4f_m * NElectrons_4f + 12 * U_2p_4f_m * NElectrons_4f + 12 * U_2p_4f_m) / (2 * (NElectrons_4f + 20))

    Delta_4f_L1_f = $Delta(4f,L1)_f_value
    E_4f_f = (28 * Delta_4f_L1_f - 460 * U_4d_4f_f - U_4f_4f_f * NElectrons_4f^2 - 47 * U_4f_4f_f * NElectrons_4f) / (2 * (NElectrons_4f + 24))
    E_4d_f = (28 * Delta_4f_L1_f - 2 * U_4d_4f_f * NElectrons_4f^2 - 30 * U_4d_4f_f * NElectrons_4f - 28 * U_4d_4f_f + U_4f_4f_f * NElectrons_4f^2 + U_4f_4f_f * NElectrons_4f) / (2 * (NElectrons_4f + 24))
    E_L1_f = (-2 * Delta_4f_L1_f * NElectrons_4f - 20 * Delta_4f_L1_f + 20 * U_4d_4f_f * NElectrons_4f + 20 * U_4d_4f_f + U_4f_4f_f * NElectrons_4f^2 + U_4f_4f_f * NElectrons_4f) / (2 * (NElectrons_4f + 24))

    H_i = H_i + Chop(
          E_4f_i * N_4f
        + E_L1_i * N_L1)

    H_m = H_f + Chop(
          E_4f_m * N_4f
        + E_2p_m * N_2p
        + E_L1_m * N_L1)

    H_f = H_f + Chop(
          E_4f_f * N_4f
        + E_4d_f * N_4d
        + E_L1_f * N_L1)

    Eav_L1_i = ($Ea2u(L1)_i_value + 3 * $Et1u(L1)_i_value + 3 * $Et2u(L1)_i_value) / 7
    Ea2u_L1_i = $Ea2u(L1)_i_value - Eav_L1_i
    Et1u_L1_i = $Et1u(L1)_i_value - Eav_L1_i
    Et2u_L1_i = $Et2u(L1)_i_value - Eav_L1_i

    Akm_L1_i = {
        {0, 0, (1 / 7) * (Ea2u_L1_i + (3) * (Et1u_L1_i + Et2u_L1_i))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_L1_i) + (-3) * (Et1u_L1_i) + Et2u_L1_i)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_i) + (-3) * (Et1u_L1_i) + Et2u_L1_i))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_i) + (-3) * (Et1u_L1_i) + Et2u_L1_i))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_L1_i) + (5) * (Et1u_L1_i) + (-9) * (Et2u_L1_i))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_i) + (5) * (Et1u_L1_i) + (-9) * (Et2u_L1_i)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_i) + (5) * (Et1u_L1_i) + (-9) * (Et2u_L1_i)))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_i))

    Eav_L1_m = ($Ea2u(L1)_m_value + 3 * $Et1u(L1)_m_value + 3 * $Et2u(L1)_m_value) / 7
    Ea2u_L1_m = $Ea2u(L1)_m_value - Eav_L1_m
    Et1u_L1_m = $Et1u(L1)_m_value - Eav_L1_m
    Et2u_L1_m = $Et2u(L1)_m_value - Eav_L1_m

    Akm_L1_m = {
        {0, 0, (1 / 7) * (Ea2u_L1_m + (3) * (Et1u_L1_m + Et2u_L1_m))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_L1_m) + (-3) * (Et1u_L1_m) + Et2u_L1_m)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_m) + (-3) * (Et1u_L1_m) + Et2u_L1_m))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_m) + (-3) * (Et1u_L1_m) + Et2u_L1_m))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_L1_m) + (5) * (Et1u_L1_m) + (-9) * (Et2u_L1_m))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_m) + (5) * (Et1u_L1_m) + (-9) * (Et2u_L1_m)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_m) + (5) * (Et1u_L1_m) + (-9) * (Et2u_L1_m)))}
    }

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_m))

    Eav_L1_f = ($Ea2u(L1)_f_value + 3 * $Et1u(L1)_f_value + 3 * $Et2u(L1)_f_value) / 7
    Ea2u_L1_f = $Ea2u(L1)_f_value - Eav_L1_f
    Et1u_L1_f = $Et1u(L1)_f_value - Eav_L1_f
    Et2u_L1_f = $Et2u(L1)_f_value - Eav_L1_f

    Akm_L1_f = {
        {0, 0, (1 / 7) * (Ea2u_L1_f + (3) * (Et1u_L1_f + Et2u_L1_f))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_L1_f) + (-3) * (Et1u_L1_f) + Et2u_L1_f)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_f) + (-3) * (Et1u_L1_f) + Et2u_L1_f))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_f) + (-3) * (Et1u_L1_f) + Et2u_L1_f))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_L1_f) + (5) * (Et1u_L1_f) + (-9) * (Et2u_L1_f))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_f) + (5) * (Et1u_L1_f) + (-9) * (Et2u_L1_f)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_f) + (5) * (Et1u_L1_f) + (-9) * (Et2u_L1_f)))}
    }

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_f))

    -- Mixing of the f-orbitals with the ligands.
    Va2u_4f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))

    Vt1u_4f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))

    Vt2u_4f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))
               + NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))

    Va2u_4f_L1_i = $Va2u(4f,L1)_i_value
    Vt1u_4f_L1_i = $Vt1u(4f,L1)_i_value
    Vt2u_4f_L1_i = $Vt2u(4f,L1)_i_value

    Va2u_4f_L1_f = $Va2u(4f,L1)_f_value
    Vt1u_4f_L1_f = $Vt1u(4f,L1)_f_value
    Vt2u_4f_L1_f = $Vt2u(4f,L1)_f_value

    H_i = H_i + Chop(
        Va2u_4f_L1_i * Va2u_4f_L1
      + Vt1u_4f_L1_i * Vt1u_4f_L1)
      + Vt2u_4f_L1_i * Vt2u_4f_L1

    H_f = H_f + Chop(
        Va2u_4f_L1_f * Va2u_4f_L1
      + Vt1u_4f_L1_f * Vt1u_4f_L1)
      + Vt2u_4f_L1_f * Vt2u_4f_L1
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4f = NewOperator("Sx", NFermions, IndexUp_4f, IndexDn_4f)
Sy_4f = NewOperator("Sy", NFermions, IndexUp_4f, IndexDn_4f)
Sz_4f = NewOperator("Sz", NFermions, IndexUp_4f, IndexDn_4f)
Ssqr_4f = NewOperator("Ssqr", NFermions, IndexUp_4f, IndexDn_4f)
Splus_4f = NewOperator("Splus", NFermions, IndexUp_4f, IndexDn_4f)
Smin_4f = NewOperator("Smin", NFermions, IndexUp_4f, IndexDn_4f)

Lx_4f = NewOperator("Lx", NFermions, IndexUp_4f, IndexDn_4f)
Ly_4f = NewOperator("Ly", NFermions, IndexUp_4f, IndexDn_4f)
Lz_4f = NewOperator("Lz", NFermions, IndexUp_4f, IndexDn_4f)
Lsqr_4f = NewOperator("Lsqr", NFermions, IndexUp_4f, IndexDn_4f)
Lplus_4f = NewOperator("Lplus", NFermions, IndexUp_4f, IndexDn_4f)
Lmin_4f = NewOperator("Lmin", NFermions, IndexUp_4f, IndexDn_4f)

Jx_4f = NewOperator("Jx", NFermions, IndexUp_4f, IndexDn_4f)
Jy_4f = NewOperator("Jy", NFermions, IndexUp_4f, IndexDn_4f)
Jz_4f = NewOperator("Jz", NFermions, IndexUp_4f, IndexDn_4f)
Jsqr_4f = NewOperator("Jsqr", NFermions, IndexUp_4f, IndexDn_4f)
Jplus_4f = NewOperator("Jplus", NFermions, IndexUp_4f, IndexDn_4f)
Jmin_4f = NewOperator("Jmin", NFermions, IndexUp_4f, IndexDn_4f)

Tx_4f = NewOperator("Tx", NFermions, IndexUp_4f, IndexDn_4f)
Ty_4f = NewOperator("Ty", NFermions, IndexUp_4f, IndexDn_4f)
Tz_4f = NewOperator("Tz", NFermions, IndexUp_4f, IndexDn_4f)

Sx = Sx_4f
Sy = Sy_4f
Sz = Sz_4f

Lx = Lx_4f
Ly = Ly_4f
Lz = Lz_4f

Jx = Jx_4f
Jy = Jy_4f
Jz = Jz_4f

Tx = Tx_4f
Ty = Ty_4f
Tz = Tz_4f

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if MagneticFieldTerm then
    -- The values are in eV, and not Tesla. To convert from Tesla to eV multiply
    -- the value with EnergyUnits.Tesla.value.
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_m = $Bx_m_value
    By_m = $By_m_value
    Bz_m = $Bz_m_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_m = H_m + Chop(
          Bx_m * (2 * Sx + Lx)
        + By_m * (2 * Sy + Ly)
        + Bz_m * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if ExchangeFieldTerm then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_m = $Hx_m_value
    Hy_m = $Hy_m_value
    Hz_m = $Hz_m_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_m = H_m + Chop(
          Hx_m * Sx
        + Hy_m * Sy
        + Hz_m * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000", NElectrons_2p, NElectrons_2p},
                                           {"000000 1111111111 00000000000000", NElectrons_4d, NElectrons_4d},
                                           {"000000 0000000000 11111111111111", NElectrons_4f, NElectrons_4f}}

IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000", NElectrons_2p - 1, NElectrons_2p - 1},
                                                {"000000 1111111111 00000000000000", NElectrons_4d, NElectrons_4d},
                                                {"000000 0000000000 11111111111111", NElectrons_4f + 1, NElectrons_4f + 1}}

FinalRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000", NElectrons_2p, NElectrons_2p},
                                         {"000000 1111111111 00000000000000", NElectrons_4d - 1, NElectrons_4d - 1},
                                         {"000000 0000000000 11111111111111", NElectrons_4f + 1, NElectrons_4f + 1}}

CalculationRestrictions = nil

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000 00000000000000", NElectrons_2p, NElectrons_2p},
                                               {"000000 1111111111 00000000000000 00000000000000", NElectrons_4d, NElectrons_4d},
                                               {"000000 0000000000 11111111111111 00000000000000", NElectrons_4f, NElectrons_4f},
                                               {"000000 0000000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000 00000000000000", NElectrons_2p - 1, NElectrons_2p - 1},
                                                    {"000000 1111111111 00000000000000 00000000000000", NElectrons_4d, NElectrons_4d},
                                                    {"000000 0000000000 11111111111111 00000000000000", NElectrons_4f + 1, NElectrons_4f + 1},
                                                    {"000000 0000000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000 00000000000000", NElectrons_2p, NElectrons_2p},
                                             {"000000 1111111111 00000000000000 00000000000000", NElectrons_4d - 1, NElectrons_4d - 1},
                                             {"000000 0000000000 11111111111111 00000000000000", NElectrons_4f + 1, NElectrons_4f + 1},
                                             {"000000 0000000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {"000000 0000000000 00000000000000 11111111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

--------------------------------------------------------------------------------
-- Define some helper functions.
--------------------------------------------------------------------------------
function MatrixToOperator(Matrix, StartIndex)
    -- Transform a matrix to an operator.
    local Operator = 0
    for i = 1, #Matrix do
        for j = 1, #Matrix do
            local Weight = Matrix[i][j]
            Operator = Operator + NewOperator("Number", #Matrix + StartIndex, i + StartIndex - 1, j + StartIndex - 1) * Weight
        end
    end
    Operator.Chop()
    return Operator
end

function ValueInTable(Value, Table)
    -- Check if a value is in a table.
    for _, v in ipairs(Table) do
        if Value == v then
            return true
        end
    end
    return false
end

function GetSpectrum(G, Ids, dZ, NOperators, NPsis)
    -- Extract the spectrum corresponding to the operators identified using the
    -- Ids argument. The returned spectrum is a weighted sum, where the weights
    -- are the Boltzmann probabilities.
    --
    -- @param G userdata: Spectrum object as returned by the functions defined in Quanty, i.e. one spectrum
    --                    for each operator and each wavefunction.
    -- @param Ids table: Indexes of the operators that are considered in the returned spectrum.
    -- @param dZ table: Boltzmann prefactors for each of the spectrum in the spectra object.
    -- @param NOperators number: Number of transition operators.
    -- @param NPsis number: Number of wavefunctions.

    if not (type(Ids) == "table") then
        Ids = {Ids}
    end

    local Id = 1
    local dZs = {}

    for i = 1, NOperators do
        for _ = 1, NPsis do
            if ValueInTable(i, Ids) then
                table.insert(dZs, dZ[Id])
            else
                table.insert(dZs, 0)
            end
            Id = Id + 1
        end
    end
    return Spectra.Sum(G, dZs)
end

function SaveSpectrum(G, Filename, Gaussian, Lorentzian, Pcl)
    if Pcl == nil then
        Pcl = 1
    end
    G = -1 / math.pi / Pcl * G
    G.Broaden(Gaussian, Lorentzian)
    G.Print({{"file", Filename .. ".spec"}})
end

function CalculateT(Basis, Eps, K)
    -- Calculate the transition operator in the basis of tesseral harmonics for
    -- an arbitrary polarization and wave-vector (for quadrupole operators).
    --
    -- @param Basis table: Operators forming the basis.
    -- @param Eps table: Cartesian components of the polarization vector.
    -- @param K table: Cartesian components of the wave-vector.

    if #Basis == 3 then
        -- The basis for the dipolar operators must be in the order x, y, z.
        T = Eps[1] * Basis[1]
          + Eps[2] * Basis[2]
          + Eps[3] * Basis[3]
    elseif #Basis == 5 then
        -- The basis for the quadrupolar operators must be in the order xy, xz, yz, x2y2, z2.
        T = (Eps[1] * K[2] + Eps[2] * K[1]) / math.sqrt(3) * Basis[1]
          + (Eps[1] * K[3] + Eps[3] * K[1]) / math.sqrt(3) * Basis[2]
          + (Eps[2] * K[3] + Eps[3] * K[2]) / math.sqrt(3) * Basis[3]
          + (Eps[1] * K[1] - Eps[2] * K[2]) / math.sqrt(3) * Basis[4]
          + (Eps[3] * K[3]) * Basis[5]
    end
    return Chop(T)
end

function DotProduct(a, b)
    return Chop(a[1] * b[1] + a[2] * b[2] + a[3] * b[3])
end

function WavefunctionsAndBoltzmannFactors(H, NPsis, NPsisAuto, Temperature, Threshold, StartRestrictions, CalculationRestrictions)
    -- Calculate the wavefunctions and Boltzmann factors of a Hamiltonian.
    --
    -- @param H userdata: Hamiltonian for which to calculate the wavefunctions.
    -- @param NPsis number: The number of wavefunctions.
    -- @param NPsisAuto boolean: Determine automatically the number of wavefunctions that are populated at the specified
    --                           temperature and within the threshold.
    -- @param Temperature number: The temperature in eV.
    -- @param Threshold number: Threshold used to determine the number of wavefunction in the automatic procedure.
    -- @param StartRestrictions table: Occupancy restrictions at the start of the calculation.
    -- @param CalculationRestrictions table: Occupancy restrictions used during the calculation.
    -- @return table: The calculated wavefunctions.
    -- @return table: The calculated Boltzmann factors.

    if Threshold == nil then
        Threshold = 1e-8
    end

    local dZ = {}
    local Z = 0
    local Psis

    if NPsisAuto == true and NPsis ~= 1 then
        NPsis = 4
        local NPsisIncrement = 8
        local NPsisIsConverged = false

        while not NPsisIsConverged do
            if CalculationRestrictions == nil then
                Psis = Eigensystem(H, StartRestrictions, NPsis)
            else
                Psis = Eigensystem(H, StartRestrictions, NPsis, {{"restrictions", CalculationRestrictions}})
            end

            if not (type(Psis) == "table") then
                Psis = {Psis}
            end

            if E_gs == nil then
                E_gs = Psis[1] * H * Psis[1]
            end

            Z = 0

            for i, Psi in ipairs(Psis) do
                local E = Psi * H * Psi

                if math.abs(E - E_gs) < Threshold ^ 2 then
                    dZ[i] = 1
                else
                    dZ[i] = math.exp(-(E - E_gs) / Temperature)
                end

                Z = Z + dZ[i]

                if dZ[i] / Z < Threshold then
                    i = i - 1
                    NPsisIsConverged = true
                    NPsis = i
                    Psis = {unpack(Psis, 1, i)}
                    dZ = {unpack(dZ, 1, i)}
                    break
                end
            end

            if NPsisIsConverged then
                break
            else
                NPsis = NPsis + NPsisIncrement
            end
        end
    else
        if CalculationRestrictions == nil then
            Psis = Eigensystem(H, StartRestrictions, NPsis)
        else
            Psis = Eigensystem(H, StartRestrictions, NPsis, {{"restrictions", CalculationRestrictions}})
        end

        if not (type(Psis) == "table") then
            Psis = {Psis}
        end

        local E_gs = Psis[1] * H * Psis[1]

        Z = 0

        for i, psi in ipairs(Psis) do
            local E = psi * H * psi

            if math.abs(E - E_gs) < Threshold ^ 2 then
                dZ[i] = 1
            else
                dZ[i] = math.exp(-(E - E_gs) / Temperature)
            end

            Z = Z + dZ[i]
        end
    end

    -- Normalize the Boltzmann factors to unity.
    for i in ipairs(dZ) do
        dZ[i] = dZ[i] / Z
    end

    return Psis, dZ
end

function PrintHamiltonianAnalysis(Psis, Operators, dZ, Header, Footer)
    io.write(Header)
    for i, Psi in ipairs(Psis) do
        io.write(string.format("%5d", i))
        for j, Operator in ipairs(Operators) do
            if j == 1 then
                io.write(string.format("%12.6f", Complex.Re(Psi * Operator * Psi)))
            elseif Operator == "dZ" then
                io.write(string.format("%12.2e", dZ[i]))
            else
                io.write(string.format("%10.4f", Complex.Re(Psi * Operator * Psi)))
            end
        end
        io.write("\n")
    end
    io.write(Footer)
end

function CalculateEnergyDifference(H1, H1Restrictions, H2, H2Restrictions)
    -- Calculate the energy difference between the lowest eigenstates of the two
    -- Hamiltonians.
    --
    -- @param H1 userdata: The first Hamiltonian.
    -- @param H1Restrictions table: Restrictions of the occupation numbers for H1.
    -- @param H2 userdata: The second Hamiltonian.
    -- @param H2Restrictions table: Restrictions of the occupation numbers for H2.

    local E1 = 0.0
    local E2 = 0.0

    if H1 ~= nil and H1Restrictions ~= nil then
        Psis1, _ = WavefunctionsAndBoltzmannFactors(H1, 1, false, 0, nil, H1Restrictions, nil)
        E1 = Psis1[1] * H1 * Psis1[1]
    end

    if H2 ~= nil and H2Restrictions ~= nil then
        Psis2, _ = WavefunctionsAndBoltzmannFactors(H2, 1, false, 0, nil, H2Restrictions, nil)
        E2 = Psis2[1] * H2 * Psis2[1]
    end

    return E1 - E2
end

--------------------------------------------------------------------------------
-- Analyze the initial Hamiltonian.
--------------------------------------------------------------------------------
Temperature = Temperature * EnergyUnits.Kelvin.value

Sk = DotProduct(WaveVectorIn, {Sx, Sy, Sz})
Lk = DotProduct(WaveVectorIn, {Lx, Ly, Lz})
Jk = DotProduct(WaveVectorIn, {Jx, Jy, Jz})
Tk = DotProduct(WaveVectorIn, {Tx, Ty, Tz})

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4f, N_2p, N_4f, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_4f>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n"

if LmctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4f, N_2p, N_4f, N_L1, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_4f>    <N_L1>          dZ\n"
    Header = Header .. "===========================================================================================================================================\n"
    Footer = "===========================================================================================================================================\n"
end

local Psis_i, dZ_i = WavefunctionsAndBoltzmannFactors(H_i, NPsis, NPsisAuto, Temperature, nil, InitialRestrictions, CalculationRestrictions)
PrintHamiltonianAnalysis(Psis_i, Operators, dZ_i, string.format(Header, "initial"), Footer)

-- Stop the calculation if no spectra need to be calculated.
if next(SpectraToCalculate) == nil then
    return
end

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
local t = math.sqrt(1 / 2)

Txy_2p_4f   = NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_2p_4f   = NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -1, t    }, {2, 1, -t    }})
Tyz_2p_4f   = NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_2p_4f = NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -2, t    }, {2, 2,  t    }})
Tz2_2p_4f   = NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2,  0, 1    }                })

Tx_4d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {{1, -1, t    }, {1, 1, -t    }})
Ty_4d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_4d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {{1,  0, 1    }                })

T_2p_4f = {Txy_2p_4f, Txz_2p_4f, Tyz_2p_4f, Tx2y2_2p_4f, Tz2_2p_4f}
T_4d_2p = {Tx_4d_2p, Ty_4d_2p, Tz_4d_2p}

if ShiftSpectra then
    Emin1 = Emin1 - (ZeroShift1 + ExperimentalShift1)
    Emax1 = Emax1 - (ZeroShift1 + ExperimentalShift1)
    Emin2 = Emin2 - (ZeroShift2 + ExperimentalShift2)
    Emax2 = Emax2 - (ZeroShift2 + ExperimentalShift2)
end

if CalculationRestrictions == nil then
    G = CreateResonantSpectra(H_m, H_f, T_2p_4f, T_4d_2p, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"DenseBorder", DenseBorder}})
else
    G = CreateResonantSpectra(H_m, H_f, T_2p_4f, T_4d_2p, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"Restrictions1", CalculationRestrictions}, {"Restrictions2", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

Giso = 0
Shift = 0
for i = 1, #Psis_i do
    for j = 1, #T_2p_4f * #T_4d_2p do
        Indexes = {}
        for k = 1, NPoints1 + 1 do
            table.insert(Indexes, k + Shift)
        end
        Giso = Giso + Spectra.Element(G, Indexes) * dZ_i[i]
        Shift = Shift + NPoints1 + 1
    end
end

-- The Gaussian broadening is done using the same value for the two dimensions.
Gaussian = math.min(Gaussian1, Gaussian2)
if Gaussian ~= 0 then
    Giso.Broaden(Gaussian, 0.0)
end

Giso = -1 / math.pi * Giso
Giso.Print({{"file", Prefix .. "_iso.spec"}})
