--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4f
-- symmetry: D4h
-- experiment: RIXS
-- edge: L2,3-M4,5 (2p3d)
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
EpsIn = $XPolarization -- Incident polarization.

-- Y-axis parameters.
Emin2 = $YEmin -- Minimum value of the energy range (eV).
Emax2 = $YEmax -- Maximum value of the energy range (eV).
NPoints2 = $YNPoints -- Number of points of the spectra.
ZeroShift2 = $YZeroShift -- Shift that brings the edge or line energy to approximately zero (eV).
ExperimentalShift2 = $YExperimentalShift -- Experimental edge or line energy (eV).
Gaussian2 = $YGaussian -- Gaussian FWHM (eV).
Gamma2 = $YGamma -- Lorentzian FWHM used in the spectra calculation (eV).

WaveVectorOut = $YWaveVector -- Scattered wave vector.
EpsOut = $YPolarization -- Scattered polarization.

SpectraToCalculate = $SpectraToCalculate -- Types of spectra to calculate.
DenseBorder = $DenseBorder -- Number of determinants where we switch from dense methods to sparse methods.
ShiftSpectra = $ShiftSpectra -- If enabled, shift the spectra in the experimental energy range.

Prefix = "$Prefix" -- File name prefix.

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
NFermions = 30

NElectrons_2p = 6
NElectrons_3d = 10
NElectrons_4f = $NElectrons_4f

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_3d = {6, 8, 10, 12, 14}
IndexUp_3d = {7, 9, 11, 13, 15}
IndexDn_4f = {16, 18, 20, 22, 24, 26, 28}
IndexUp_4f = {17, 19, 21, 23, 25, 27, 29}

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

N_3d = NewOperator("Number", NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

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
  
    F0_3d_4f = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {1, 0, 0}, {0, 0, 0});
    F2_3d_4f = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 1, 0}, {0, 0, 0});
    F4_3d_4f = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 1}, {0, 0, 0});
    G1_3d_4f = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {1, 0, 0});
    G3_3d_4f = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 1, 0});
    G5_3d_4f = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 0, 1});

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
    U_3d_4f_f  = $U(3d,4f)_f_value
    F2_3d_4f_f = $F2(3d,4f)_f_value * $F2(3d,4f)_f_scaleFactor
    F4_3d_4f_f = $F4(3d,4f)_f_value * $F4(3d,4f)_f_scaleFactor
    G1_3d_4f_f = $G1(3d,4f)_f_value * $G1(3d,4f)_f_scaleFactor
    G3_3d_4f_f = $G3(3d,4f)_f_value * $G3(3d,4f)_f_scaleFactor
    G5_3d_4f_f = $G5(3d,4f)_f_value * $G5(3d,4f)_f_scaleFactor
    F0_3d_4f_f = U_3d_4f_f + 3 / 70 * G1_3d_4f_f + 2 / 105 * G3_3d_4f_f + 5 / 231 * G5_3d_4f_f

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
        + F0_3d_4f_f * F0_3d_4f
        + F2_3d_4f_f * F2_3d_4f
        + F4_3d_4f_f * F4_3d_4f
        + G1_3d_4f_f * G1_3d_4f
        + G3_3d_4f_f * G3_3d_4f
        + G5_3d_4f_f * G5_3d_4f)

    ldots_4f = NewOperator("ldots", NFermions, IndexUp_4f, IndexDn_4f)

    ldots_2p = NewOperator("ldots", NFermions, IndexUp_2p, IndexDn_2p)

    ldots_3d = NewOperator("ldots", NFermions, IndexUp_3d, IndexDn_3d)

    zeta_4f_i = $zeta(4f)_i_value * $zeta(4f)_i_scaleFactor

    zeta_4f_m = $zeta(4f)_m_value * $zeta(4f)_m_scaleFactor
    zeta_2p_m = $zeta(2p)_m_value * $zeta(2p)_m_scaleFactor

    zeta_4f_f = $zeta(4f)_f_value * $zeta(4f)_f_scaleFactor
    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_4f_i * ldots_4f)

    H_m = H_m + Chop(
          zeta_4f_m * ldots_4f
        + zeta_2p_m * ldots_2p)

    H_f = H_f + Chop(
          zeta_4f_f * ldots_4f
        + zeta_3d_f * ldots_3d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D4h crystal field for f electrons, Quanty "zxy" setting: the four-fold C4 axis
    -- is along z and the C2' axes / vertical mirror planes lie along x and y. The
    -- seven 4f orbitals split into a2u + b1u + b2u + 2 eu (the two eu sets mix
    -- through Meu); energies are referenced to their (degeneracy-weighted) average so
    -- the k = 0 monopole vanishes. The Akm expansion is taken from the Quanty
    -- point-group tables (https://www.quanty.org/physics_chemistry/point_groups).
    Eav_4f_i = ($Ea2u(4f)_i_value + $Eb1u(4f)_i_value + $Eb2u(4f)_i_value + 2 * $Eeu1(4f)_i_value + 2 * $Eeu2(4f)_i_value) / 7
    Ea2u_4f_i = $Ea2u(4f)_i_value - Eav_4f_i
    Eb1u_4f_i = $Eb1u(4f)_i_value - Eav_4f_i
    Eb2u_4f_i = $Eb2u(4f)_i_value - Eav_4f_i
    Eeu1_4f_i = $Eeu1(4f)_i_value - Eav_4f_i
    Eeu2_4f_i = $Eeu2(4f)_i_value - Eav_4f_i
    Meu_4f_i = $Meu(4f)_i_value

    Akm_4f_i = {
        {0, 0, (1 / 7) * (Ea2u_4f_i + Eb1u_4f_i + Eb2u_4f_i + 2 * Eeu1_4f_i + 2 * Eeu2_4f_i)},
        {2, 0, (5 / 7) * (Ea2u_4f_i - Eeu1_4f_i + sqrt(15) * Meu_4f_i)},
        {4, 0, (3 / 28) * (12 * Ea2u_4f_i - 14 * Eb1u_4f_i - 14 * Eb2u_4f_i + 9 * Eeu1_4f_i + 7 * Eeu2_4f_i - 2 * sqrt(15) * Meu_4f_i)},
        {4, -4, (-3 / 56) * (2 * sqrt(70) * Eb1u_4f_i - 2 * sqrt(70) * Eb2u_4f_i - 3 * sqrt(70) * Eeu1_4f_i + 3 * sqrt(70) * Eeu2_4f_i - 2 * sqrt(42) * Meu_4f_i)},
        {4, 4, (-3 / 56) * (2 * sqrt(70) * Eb1u_4f_i - 2 * sqrt(70) * Eb2u_4f_i - 3 * sqrt(70) * Eeu1_4f_i + 3 * sqrt(70) * Eeu2_4f_i - 2 * sqrt(42) * Meu_4f_i)},
        {6, 0, (13 / 280) * (40 * Ea2u_4f_i + 12 * Eb1u_4f_i + 12 * Eb2u_4f_i - 25 * Eeu1_4f_i - 39 * Eeu2_4f_i - 14 * sqrt(15) * Meu_4f_i)},
        {6, -4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_4f_i - 4 * sqrt(42) * Eb2u_4f_i + 5 * sqrt(42) * Eeu1_4f_i - 5 * sqrt(42) * Eeu2_4f_i + 2 * sqrt(70) * Meu_4f_i))},
        {6, 4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_4f_i - 4 * sqrt(42) * Eb2u_4f_i + 5 * sqrt(42) * Eeu1_4f_i - 5 * sqrt(42) * Eeu2_4f_i + 2 * sqrt(70) * Meu_4f_i))}
    }

    io.write("Initial-state D4h crystal field Hamiltonian (a2u, b1u, b2u, eu) diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("%-7s %8.3f\n", "a2u", Ea2u_4f_i))
    io.write(string.format("%-7s %8.3f\n", "b1u", Eb1u_4f_i))
    io.write(string.format("%-7s %8.3f\n", "b2u", Eb2u_4f_i))
    io.write(string.format("%-7s %8.3f\n", "eu(1)", Eeu1_4f_i))
    io.write(string.format("%-7s %8.3f\n", "eu(2)", Eeu2_4f_i))
    io.write("================\n")
    io.write(string.format("Off-diagonal elements: <eu(1)|H|eu(2)> = %.3f.\n", Meu_4f_i))
    io.write("\n")

    Eav_4f_m = ($Ea2u(4f)_m_value + $Eb1u(4f)_m_value + $Eb2u(4f)_m_value + 2 * $Eeu1(4f)_m_value + 2 * $Eeu2(4f)_m_value) / 7
    Ea2u_4f_m = $Ea2u(4f)_m_value - Eav_4f_m
    Eb1u_4f_m = $Eb1u(4f)_m_value - Eav_4f_m
    Eb2u_4f_m = $Eb2u(4f)_m_value - Eav_4f_m
    Eeu1_4f_m = $Eeu1(4f)_m_value - Eav_4f_m
    Eeu2_4f_m = $Eeu2(4f)_m_value - Eav_4f_m
    Meu_4f_m = $Meu(4f)_m_value

    Akm_4f_m = {
        {0, 0, (1 / 7) * (Ea2u_4f_m + Eb1u_4f_m + Eb2u_4f_m + 2 * Eeu1_4f_m + 2 * Eeu2_4f_m)},
        {2, 0, (5 / 7) * (Ea2u_4f_m - Eeu1_4f_m + sqrt(15) * Meu_4f_m)},
        {4, 0, (3 / 28) * (12 * Ea2u_4f_m - 14 * Eb1u_4f_m - 14 * Eb2u_4f_m + 9 * Eeu1_4f_m + 7 * Eeu2_4f_m - 2 * sqrt(15) * Meu_4f_m)},
        {4, -4, (-3 / 56) * (2 * sqrt(70) * Eb1u_4f_m - 2 * sqrt(70) * Eb2u_4f_m - 3 * sqrt(70) * Eeu1_4f_m + 3 * sqrt(70) * Eeu2_4f_m - 2 * sqrt(42) * Meu_4f_m)},
        {4, 4, (-3 / 56) * (2 * sqrt(70) * Eb1u_4f_m - 2 * sqrt(70) * Eb2u_4f_m - 3 * sqrt(70) * Eeu1_4f_m + 3 * sqrt(70) * Eeu2_4f_m - 2 * sqrt(42) * Meu_4f_m)},
        {6, 0, (13 / 280) * (40 * Ea2u_4f_m + 12 * Eb1u_4f_m + 12 * Eb2u_4f_m - 25 * Eeu1_4f_m - 39 * Eeu2_4f_m - 14 * sqrt(15) * Meu_4f_m)},
        {6, -4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_4f_m - 4 * sqrt(42) * Eb2u_4f_m + 5 * sqrt(42) * Eeu1_4f_m - 5 * sqrt(42) * Eeu2_4f_m + 2 * sqrt(70) * Meu_4f_m))},
        {6, 4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_4f_m - 4 * sqrt(42) * Eb2u_4f_m + 5 * sqrt(42) * Eeu1_4f_m - 5 * sqrt(42) * Eeu2_4f_m + 2 * sqrt(70) * Meu_4f_m))}
    }

    Eav_4f_f = ($Ea2u(4f)_f_value + $Eb1u(4f)_f_value + $Eb2u(4f)_f_value + 2 * $Eeu1(4f)_f_value + 2 * $Eeu2(4f)_f_value) / 7
    Ea2u_4f_f = $Ea2u(4f)_f_value - Eav_4f_f
    Eb1u_4f_f = $Eb1u(4f)_f_value - Eav_4f_f
    Eb2u_4f_f = $Eb2u(4f)_f_value - Eav_4f_f
    Eeu1_4f_f = $Eeu1(4f)_f_value - Eav_4f_f
    Eeu2_4f_f = $Eeu2(4f)_f_value - Eav_4f_f
    Meu_4f_f = $Meu(4f)_f_value

    Akm_4f_f = {
        {0, 0, (1 / 7) * (Ea2u_4f_f + Eb1u_4f_f + Eb2u_4f_f + 2 * Eeu1_4f_f + 2 * Eeu2_4f_f)},
        {2, 0, (5 / 7) * (Ea2u_4f_f - Eeu1_4f_f + sqrt(15) * Meu_4f_f)},
        {4, 0, (3 / 28) * (12 * Ea2u_4f_f - 14 * Eb1u_4f_f - 14 * Eb2u_4f_f + 9 * Eeu1_4f_f + 7 * Eeu2_4f_f - 2 * sqrt(15) * Meu_4f_f)},
        {4, -4, (-3 / 56) * (2 * sqrt(70) * Eb1u_4f_f - 2 * sqrt(70) * Eb2u_4f_f - 3 * sqrt(70) * Eeu1_4f_f + 3 * sqrt(70) * Eeu2_4f_f - 2 * sqrt(42) * Meu_4f_f)},
        {4, 4, (-3 / 56) * (2 * sqrt(70) * Eb1u_4f_f - 2 * sqrt(70) * Eb2u_4f_f - 3 * sqrt(70) * Eeu1_4f_f + 3 * sqrt(70) * Eeu2_4f_f - 2 * sqrt(42) * Meu_4f_f)},
        {6, 0, (13 / 280) * (40 * Ea2u_4f_f + 12 * Eb1u_4f_f + 12 * Eb2u_4f_f - 25 * Eeu1_4f_f - 39 * Eeu2_4f_f - 14 * sqrt(15) * Meu_4f_f)},
        {6, -4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_4f_f - 4 * sqrt(42) * Eb2u_4f_f + 5 * sqrt(42) * Eeu1_4f_f - 5 * sqrt(42) * Eeu2_4f_f + 2 * sqrt(70) * Meu_4f_f))},
        {6, 4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_4f_f - 4 * sqrt(42) * Eb2u_4f_f + 5 * sqrt(42) * Eeu1_4f_f - 5 * sqrt(42) * Eeu2_4f_f + 2 * sqrt(70) * Meu_4f_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_f))
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
                                           {"000000 1111111111 00000000000000", NElectrons_3d, NElectrons_3d},
                                           {"000000 0000000000 11111111111111", NElectrons_4f, NElectrons_4f}}

IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000", NElectrons_2p - 1, NElectrons_2p - 1},
                                                {"000000 1111111111 00000000000000", NElectrons_3d, NElectrons_3d},
                                                {"000000 0000000000 11111111111111", NElectrons_4f + 1, NElectrons_4f + 1}}

FinalRestrictions = {NFermions, NBosons, {"111111 0000000000 00000000000000", NElectrons_2p, NElectrons_2p},
                                         {"000000 1111111111 00000000000000", NElectrons_3d - 1, NElectrons_3d - 1},
                                         {"000000 0000000000 11111111111111", NElectrons_4f + 1, NElectrons_4f + 1}}

CalculationRestrictions = nil

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

function GetResonantSpectrum(G, dZ, NOperators, NPsis, NPoints)
    -- Sum the resonant spectrum over the operator combinations and wavefunctions,
    -- weighted by the Boltzmann probabilities. The spectra object returned by
    -- CreateResonantSpectra contains one block of (NPoints + 1) rows for each
    -- operator combination and wavefunction.
    --
    -- @param G userdata: Spectra object returned by CreateResonantSpectra.
    -- @param dZ table: Boltzmann prefactors for each wavefunction.
    -- @param NOperators number: Number of transition operator combinations.
    -- @param NPsis number: Number of wavefunctions.
    -- @param NPoints number: Number of points along the incident energy axis.

    local Spectrum = 0
    local Shift = 0
    for i = 1, NPsis do
        for _ = 1, NOperators do
            local Indexes = {}
            for k = 1, NPoints + 1 do
                table.insert(Indexes, k + Shift)
            end
            Spectrum = Spectrum + Spectra.Element(G, Indexes) * dZ[i]
            Shift = Shift + NPoints + 1
        end
    end
    return Spectrum
end

function GetFundamentalSpectra(G, dZ, NPsis, NPoints)
    -- Compute the two fundamental spectra A and B of the powder-averaged
    -- (isotropic) dipole-dipole RIXS response from the full 9 x 9 polarization
    -- grid produced by the "four-measurement" (+/-) scheme.
    --
    -- The transition operators passed to CreateResonantSpectra must be the
    -- nine-element basis on each side, in the order
    --   {Tx, Ty, Tz, (Tx+Ty)t, (Tx+Tz)t, (Ty+Tz)t, (Tx-Ty)t, (Tx-Tz)t, (Ty-Tz)t}
    -- with t = 1/sqrt(2). The spectra object then holds one (NPoints + 1) block
    -- for each (incident, emission) channel and wavefunction, ordered with the
    -- wavefunction outermost, then the incident operator, then the emission
    -- operator (the same ordering used by GetResonantSpectrum).
    --
    -- @param G userdata: Spectra object returned by CreateResonantSpectra.
    -- @param dZ table: Boltzmann prefactors for each wavefunction.
    -- @param NPsis number: Number of wavefunctions.
    -- @param NPoints number: Number of points along the incident energy axis.
    -- @return userdata, userdata: The fundamental spectra A and B.

    local NChannels = 9
    local NCombinations = NChannels * NChannels

    -- Channel (i, j) summed over the wavefunctions, weighted by the Boltzmann
    -- probabilities. i is the incident operator, j the emission operator.
    local function Channel(i, j)
        local Spectrum = 0
        for p = 1, NPsis do
            local Block = (p - 1) * NCombinations + (i - 1) * NChannels + (j - 1)
            local Indexes = {}
            for k = 1, NPoints + 1 do
                table.insert(Indexes, Block * (NPoints + 1) + k)
            end
            Spectrum = Spectrum + Spectra.Element(G, Indexes) * dZ[p]
        end
        return Spectrum
    end

    local Gpol = {}
    for i = 1, NChannels do
        Gpol[i] = {}
        for j = 1, NChannels do
            Gpol[i][j] = Channel(i, j)
        end
    end

    -- First rotational invariant: the 3 x 3 Cartesian block.
    local M1 = 0
    for i = 1, 3 do
        for j = 1, 3 do
            M1 = M1 + Gpol[i][j]
        end
    end

    -- Second and third invariants, recovered from the diagonal and the +/-
    -- combinations (the four-measurement scheme).
    local Gtrace = Gpol[1][1] + Gpol[2][2] + Gpol[3][3]

    local Gcross = 0
    for i = 1, 3 do
        local Plus = 3 + i
        local Minus = 6 + i
        Gcross = Gcross + (Gpol[Plus][Plus]
                         - Gpol[Plus][Minus]
                         - Gpol[Minus][Plus]
                         + Gpol[Minus][Minus])
    end

    local M23 = 2 * Gtrace + Gcross

    local A = (4 * M1 - M23) / 30
    local B = (-2 * M1 + 3 * M23) / 30

    return A, B
end

function CalculateT(Basis, Eps, WaveVector)
    -- Calculate the transition operator in the basis of tesseral harmonics for
    -- an arbitrary polarization and wave-vector (for quadrupole operators).
    --
    -- @param Basis table: Operators forming the basis.
    -- @param Eps table: Cartesian components of the polarization vector.
    -- @param WaveVector table: Cartesian components of the wave-vector.

    if #Basis == 3 then
        -- The basis for the dipolar operators must be in the order x, y, z.
        T = Eps[1] * Basis[1]
          + Eps[2] * Basis[2]
          + Eps[3] * Basis[3]
    elseif #Basis == 5 then
        -- The basis for the quadrupolar operators must be in the order xy, xz, yz, x2y2, z2.
        T = (Eps[1] * WaveVector[2] + Eps[2] * WaveVector[1]) / math.sqrt(3) * Basis[1]
          + (Eps[1] * WaveVector[3] + Eps[3] * WaveVector[1]) / math.sqrt(3) * Basis[2]
          + (Eps[2] * WaveVector[3] + Eps[3] * WaveVector[2]) / math.sqrt(3) * Basis[3]
          + (Eps[1] * WaveVector[1] - Eps[2] * WaveVector[2]) / math.sqrt(3) * Basis[4]
          + (Eps[3] * WaveVector[3]) * Basis[5]
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

Tx_3d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {{1, -1, t    }, {1, 1, -t    }})
Ty_3d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_3d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {{1,  0, 1    }                })

T_2p_4f = {CalculateT({Txy_2p_4f, Txz_2p_4f, Tyz_2p_4f, Tx2y2_2p_4f, Tz2_2p_4f}, EpsIn, WaveVectorIn)}
T_3d_2p = {CalculateT({Tx_3d_2p, Ty_3d_2p, Tz_3d_2p}, EpsOut, WaveVectorOut)}

if ShiftSpectra then
    Emin1 = Emin1 - (ZeroShift1 + ExperimentalShift1)
    Emax1 = Emax1 - (ZeroShift1 + ExperimentalShift1)
    Emin2 = Emin2 - (ZeroShift2 + ExperimentalShift2)
    Emax2 = Emax2 - (ZeroShift2 + ExperimentalShift2)
end

if CalculationRestrictions == nil then
    G = CreateResonantSpectra(H_m, H_f, T_2p_4f, T_3d_2p, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"DenseBorder", DenseBorder}})
else
    G = CreateResonantSpectra(H_m, H_f, T_2p_4f, T_3d_2p, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"Restrictions1", CalculationRestrictions}, {"Restrictions2", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

-- The Gaussian broadening is done using the same value for the two dimensions.
Gaussian = math.min(Gaussian1, Gaussian2)
G = GetResonantSpectrum(G, dZ_i, #T_2p_4f * #T_3d_2p, #Psis_i, NPoints1)
SaveSpectrum(G, Prefix .. "_k", Gaussian, 0.0)
