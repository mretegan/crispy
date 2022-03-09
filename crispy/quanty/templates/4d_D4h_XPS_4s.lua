--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4d
-- symmetry: D4h
-- experiment: XPS
-- edge: N1 (4s)
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

Emin = $XEmin -- Minimum value of the energy range (eV).
Emax = $XEmax -- Maximum value of the energy range (eV).
NPoints = $XNPoints -- Number of points of the spectra.
ZeroShift = $XZeroShift -- Shift that brings the edge or line energy to approximately zero (eV).
ExperimentalShift = $XExperimentalShift -- Experimental edge or line energy (eV).
Gaussian = $XGaussian -- Gaussian FWHM (eV).
Lorentzian = $XLorentzian -- Lorentzian FWHM (eV).
Gamma = $XGamma -- Lorentzian FWHM used in the spectra calculation (eV).

WaveVector = $XWaveVector -- Wave vector.
Ev = $XFirstPolarization -- Vertical polarization.
Eh = $XSecondPolarization -- Horizontal polarization.

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
NFermions = 12

NElectrons_4s = 2
NElectrons_4d = $NElectrons_4d

IndexDn_4s = {0}
IndexUp_4s = {1}
IndexDn_4d = {2, 4, 6, 8, 10}
IndexUp_4d = {3, 5, 7, 9, 11}

if LmctLigandsHybridizationTerm then
    NFermions = 22

    NElectrons_L1 = 10

    IndexDn_L1 = {12, 14, 16, 18, 20}
    IndexUp_L1 = {13, 15, 17, 19, 21}
end

if MlctLigandsHybridizationTerm then
    NFermions = 22

    NElectrons_L2 = 10

    IndexDn_L2 = {12, 14, 16, 18, 20}
    IndexUp_L2 = {13, 15, 17, 19, 21}
end

if LmctLigandsHybridizationTerm and MlctLigandsHybridizationTerm then
    return
end

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_4s = NewOperator("Number", NFermions, IndexUp_4s, IndexUp_4s, {1})
     + NewOperator("Number", NFermions, IndexDn_4s, IndexDn_4s, {1})

N_4d = NewOperator("Number", NFermions, IndexUp_4d, IndexUp_4d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_4d, IndexDn_4d, {1, 1, 1, 1, 1})

if AtomicTerm then
    F0_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {1, 0, 0})
    F2_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {0, 1, 0})
    F4_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {0, 0, 1})

    F0_4s_4d = NewOperator("U", NFermions, IndexUp_4s, IndexDn_4s, IndexUp_4d, IndexDn_4d, {1}, {0})
    G2_4s_4d = NewOperator("U", NFermions, IndexUp_4s, IndexDn_4s, IndexUp_4d, IndexDn_4d, {0}, {1})

    U_4d_4d_i = $U(4d,4d)_i_value
    F2_4d_4d_i = $F2(4d,4d)_i_value * $F2(4d,4d)_i_scaleFactor
    F4_4d_4d_i = $F4(4d,4d)_i_value * $F4(4d,4d)_i_scaleFactor
    F0_4d_4d_i = U_4d_4d_i + 2 / 63 * F2_4d_4d_i + 2 / 63 * F4_4d_4d_i

    U_4d_4d_f = $U(4d,4d)_f_value
    F2_4d_4d_f = $F2(4d,4d)_f_value * $F2(4d,4d)_f_scaleFactor
    F4_4d_4d_f = $F4(4d,4d)_f_value * $F4(4d,4d)_f_scaleFactor
    F0_4d_4d_f = U_4d_4d_f + 2 / 63 * F2_4d_4d_f + 2 / 63 * F4_4d_4d_f
    U_4s_4d_f = $U(4s,4d)_f_value
    G2_4s_4d_f = $G2(4s,4d)_f_value * $G2(4s,4d)_f_scaleFactor
    F0_4s_4d_f = U_4s_4d_f + 1 / 10 * G2_4s_4d_f

    H_i = H_i + Chop(
          F0_4d_4d_i * F0_4d_4d
        + F2_4d_4d_i * F2_4d_4d
        + F4_4d_4d_i * F4_4d_4d)

    H_f = H_f + Chop(
          F0_4d_4d_f * F0_4d_4d
        + F2_4d_4d_f * F2_4d_4d
        + F4_4d_4d_f * F4_4d_4d
        + F0_4s_4d_f * F0_4s_4d
        + G2_4s_4d_f * G2_4s_4d)

    ldots_4d = NewOperator("ldots", NFermions, IndexUp_4d, IndexDn_4d)

    zeta_4d_i = $zeta(4d)_i_value * $zeta(4d)_i_scaleFactor

    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_4d_i * ldots_4d)

    H_f = H_f + Chop(
          zeta_4d_f * ldots_4d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if  CrystalFieldTerm then
    -- PotentialExpandedOnClm("D4h", 2, {Ea1g, Eb1g, Eb2g, Eeg})
    -- Dq_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    -- Ds_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    -- Dt_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Akm = {{4, 0, 21}, {4, -4, 1.5 * sqrt(70)}, {4, 4, 1.5 * sqrt(70)}}
    Dq_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Akm = {{2, 0, -7}}
    Ds_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Akm = {{4, 0, -21}}
    Dt_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Dq_4d_i = $10Dq(4d)_i_value / 10.0
    Ds_4d_i = $Ds(4d)_i_value
    Dt_4d_i = $Dt(4d)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1g     %8.3f\n", 6 * Dq_4d_i - 2 * Ds_4d_i - 6 * Dt_4d_i ))
    io.write(string.format("b1g     %8.3f\n", 6 * Dq_4d_i + 2 * Ds_4d_i - Dt_4d_i ))
    io.write(string.format("b2g     %8.3f\n", -4 * Dq_4d_i + 2 * Ds_4d_i - Dt_4d_i ))
    io.write(string.format("eg      %8.3f\n", -4 * Dq_4d_i - Ds_4d_i + 4 * Dt_4d_i))
    io.write("================\n")
    io.write("\n")

    Dq_4d_f = $10Dq(4d)_f_value / 10.0
    Ds_4d_f = $Ds(4d)_f_value
    Dt_4d_f = $Dt(4d)_f_value

    H_i = H_i + Chop(
          Dq_4d_i * Dq_4d
        + Ds_4d_i * Ds_4d
        + Dt_4d_i * Dt_4d)

    H_f = H_f + Chop(
          Dq_4d_f * Dq_4d
        + Ds_4d_f * Ds_4d
        + Dt_4d_f * Dt_4d)
end

--------------------------------------------------------------------------------
-- Define the 4d-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_4d_L1_i = $Delta(4d,L1)_i_value
    E_4d_i = (10 * Delta_4d_L1_i - NElectrons_4d * (19 + NElectrons_4d) * U_4d_4d_i / 2) / (10 + NElectrons_4d)
    E_L1_i = NElectrons_4d * ((1 + NElectrons_4d) * U_4d_4d_i / 2 - Delta_4d_L1_i) / (10 + NElectrons_4d)

    Delta_4d_L1_f = $Delta(4d,L1)_f_value
    E_4d_f = (10 * Delta_4d_L1_f - NElectrons_4d * (23 + NElectrons_4d) * U_4d_4d_f / 2 - 22 * U_4s_4d_f) / (12 + NElectrons_4d)
    E_4s_f = (10 * Delta_4d_L1_f + (1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 - (10 + NElectrons_4d) * U_4s_4d_f)) / (12 + NElectrons_4d)
    E_L1_f = (-2 * Delta_4d_L1_f * NElectrons_4d - 4 * Delta_4d_L1_f + U_4d_4d_f * NElectrons_4d^2 + U_4d_4d_f * NElectrons_4d + 4 * U_4s_4d_f * NElectrons_4d + 4 * U_4s_4d_f) / (2 * (NElectrons_4d + 12))

    H_i = H_i + Chop(
          E_4d_i * N_4d
        + E_L1_i * N_L1)

    H_f = H_f + Chop(
          E_4d_f * N_4d
        + E_4s_f * N_4s
        + E_L1_f * N_L1)

    Dq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_4d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_4d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_4d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_4d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L1_i = $10Dq(L1)_i_value / 10.0
    Ds_L1_i = $Ds(L1)_i_value
    Dt_L1_i = $Dt(L1)_i_value
    Va1g_4d_L1_i = $Va1g(4d,L1)_i_value
    Vb1g_4d_L1_i = $Vb1g(4d,L1)_i_value
    Vb2g_4d_L1_i = $Vb2g(4d,L1)_i_value
    Veg_4d_L1_i = $Veg(4d,L1)_i_value

    Dq_L1_f = $10Dq(L1)_f_value / 10.0
    Ds_L1_f = $Ds(L1)_f_value
    Dt_L1_f = $Dt(L1)_f_value
    Va1g_4d_L1_f = $Va1g(4d,L1)_f_value
    Vb1g_4d_L1_f = $Vb1g(4d,L1)_f_value
    Vb2g_4d_L1_f = $Vb2g(4d,L1)_f_value
    Veg_4d_L1_f = $Veg(4d,L1)_f_value

    H_i = H_i + Chop(
          Dq_L1_i * Dq_L1
        + Ds_L1_i * Ds_L1
        + Dt_L1_i * Dt_L1
        + Va1g_4d_L1_i * Va1g_4d_L1
        + Vb1g_4d_L1_i * Vb1g_4d_L1
        + Vb2g_4d_L1_i * Vb2g_4d_L1
        + Veg_4d_L1_i  * Veg_4d_L1)

    H_f = H_f + Chop(
          Dq_L1_f * Dq_L1
        + Ds_L1_f * Ds_L1
        + Dt_L1_f * Dt_L1
        + Va1g_4d_L1_f * Va1g_4d_L1
        + Vb1g_4d_L1_f * Vb1g_4d_L1
        + Vb2g_4d_L1_f * Vb2g_4d_L1
        + Veg_4d_L1_f  * Veg_4d_L1)
end

--------------------------------------------------------------------------------
-- Define the 4d-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if MlctLigandsHybridizationTerm then
    N_L2 = NewOperator("Number", NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_4d_L2_i = $Delta(4d,L2)_i_value
    E_4d_i = U_4d_4d_i * (-NElectrons_4d + 1) / 2
    E_L2_i = Delta_4d_L2_i + U_4d_4d_i * NElectrons_4d / 2 - U_4d_4d_i / 2

    Delta_4d_L2_f = $Delta(4d,L2)_f_value
    E_4d_f = -(U_4d_4d_f * NElectrons_4d^2 + 3 * U_4d_4d_f * NElectrons_4d + 4 * U_4s_4d_f) / (2 * NElectrons_4d + 4)
    E_4s_f = NElectrons_4d * (U_4d_4d_f * NElectrons_4d + U_4d_4d_f - 2 * U_4s_4d_f * NElectrons_4d - 2 * U_4s_4d_f) / (2 * (NElectrons_4d + 2))
    E_L2_f = (2 * Delta_4d_L2_f * NElectrons_4d + 4 * Delta_4d_L2_f + U_4d_4d_f * NElectrons_4d^2 - U_4d_4d_f * NElectrons_4d - 4 * U_4d_4d_f + 4 * U_4s_4d_f * NElectrons_4d + 4 * U_4s_4d_f) / (2 * (NElectrons_4d + 2))

    H_i = H_i + Chop(
          E_4d_i * N_4d
        + E_L2_i * N_L2)

    H_f = H_f + Chop(
          E_4d_f * N_4d
        + E_4s_f * N_4s
        + E_L2_f * N_L2)

    Dq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_4d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_4d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_4d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_4d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L2_i = $10Dq(L2)_i_value / 10.0
    Ds_L2_i = $Ds(L2)_i_value
    Dt_L2_i = $Dt(L2)_i_value
    Va1g_4d_L2_i = $Va1g(4d,L2)_i_value
    Vb1g_4d_L2_i = $Vb1g(4d,L2)_i_value
    Vb2g_4d_L2_i = $Vb2g(4d,L2)_i_value
    Veg_4d_L2_i = $Veg(4d,L2)_i_value

    Dq_L2_f = $10Dq(L2)_f_value / 10.0
    Ds_L2_f = $Ds(L2)_f_value
    Dt_L2_f = $Dt(L2)_f_value
    Va1g_4d_L2_f = $Va1g(4d,L2)_f_value
    Vb1g_4d_L2_f = $Vb1g(4d,L2)_f_value
    Vb2g_4d_L2_f = $Vb2g(4d,L2)_f_value
    Veg_4d_L2_f = $Veg(4d,L2)_f_value

    H_i = H_i + Chop(
          Dq_L2_i * Dq_L2
        + Ds_L2_i * Ds_L2
        + Dt_L2_i * Dt_L2
        + Va1g_4d_L2_i * Va1g_4d_L2
        + Vb1g_4d_L2_i * Vb1g_4d_L2
        + Vb2g_4d_L2_i * Vb2g_4d_L2
        + Veg_4d_L2_i  * Veg_4d_L2)

    H_f = H_f + Chop(
          Dq_L2_f * Dq_L2
        + Ds_L2_f * Ds_L2
        + Dt_L2_f * Dt_L2
        + Va1g_4d_L2_f * Va1g_4d_L2
        + Vb1g_4d_L2_f * Vb1g_4d_L2
        + Vb2g_4d_L2_f * Vb2g_4d_L2
        + Veg_4d_L2_f  * Veg_4d_L2)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4d = NewOperator("Sx", NFermions, IndexUp_4d, IndexDn_4d)
Sy_4d = NewOperator("Sy", NFermions, IndexUp_4d, IndexDn_4d)
Sz_4d = NewOperator("Sz", NFermions, IndexUp_4d, IndexDn_4d)
Ssqr_4d = NewOperator("Ssqr", NFermions, IndexUp_4d, IndexDn_4d)
Splus_4d = NewOperator("Splus", NFermions, IndexUp_4d, IndexDn_4d)
Smin_4d = NewOperator("Smin", NFermions, IndexUp_4d, IndexDn_4d)

Lx_4d = NewOperator("Lx", NFermions, IndexUp_4d, IndexDn_4d)
Ly_4d = NewOperator("Ly", NFermions, IndexUp_4d, IndexDn_4d)
Lz_4d = NewOperator("Lz", NFermions, IndexUp_4d, IndexDn_4d)
Lsqr_4d = NewOperator("Lsqr", NFermions, IndexUp_4d, IndexDn_4d)
Lplus_4d = NewOperator("Lplus", NFermions, IndexUp_4d, IndexDn_4d)
Lmin_4d = NewOperator("Lmin", NFermions, IndexUp_4d, IndexDn_4d)

Jx_4d = NewOperator("Jx", NFermions, IndexUp_4d, IndexDn_4d)
Jy_4d = NewOperator("Jy", NFermions, IndexUp_4d, IndexDn_4d)
Jz_4d = NewOperator("Jz", NFermions, IndexUp_4d, IndexDn_4d)
Jsqr_4d = NewOperator("Jsqr", NFermions, IndexUp_4d, IndexDn_4d)
Jplus_4d = NewOperator("Jplus", NFermions, IndexUp_4d, IndexDn_4d)
Jmin_4d = NewOperator("Jmin", NFermions, IndexUp_4d, IndexDn_4d)

Tx_4d = NewOperator("Tx", NFermions, IndexUp_4d, IndexDn_4d)
Ty_4d = NewOperator("Ty", NFermions, IndexUp_4d, IndexDn_4d)
Tz_4d = NewOperator("Tz", NFermions, IndexUp_4d, IndexDn_4d)

Sx = Sx_4d
Sy = Sy_4d
Sz = Sz_4d

Lx = Lx_4d
Ly = Ly_4d
Lz = Lz_4d

Jx = Jx_4d
Jy = Jy_4d
Jz = Jz_4d

Tx = Tx_4d
Ty = Ty_4d
Tz = Tz_4d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if MagneticFieldTerm then
    -- The values are in eV, and not Tesla. To convert from Tesla to eV multiply
    -- the value with EnergyUnits.Tesla.value.
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if ExchangeFieldTerm then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_4s, NElectrons_4s},
                                           {"00 1111111111", NElectrons_4d, NElectrons_4d}}

FinalRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_4s - 1, NElectrons_4s - 1},
                                         {"00 1111111111", NElectrons_4d, NElectrons_4d}}

CalculationRestrictions = nil

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"11 0000000000 0000000000", NElectrons_4s, NElectrons_4s},
                                               {"00 1111111111 0000000000", NElectrons_4d, NElectrons_4d},
                                               {"00 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {"11 0000000000 0000000000", NElectrons_4s - 1, NElectrons_4s - 1},
                                             {"00 1111111111 0000000000", NElectrons_4d, NElectrons_4d},
                                             {"00 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {"00 0000000000 1111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

if MlctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"11 0000000000 0000000000", NElectrons_4s, NElectrons_4s},
                                               {"00 1111111111 0000000000", NElectrons_4d, NElectrons_4d},
                                               {"00 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    FinalRestrictions = {NFermions, NBosons, {"11 0000000000 0000000000", NElectrons_4s - 1, NElectrons_4s - 1},
                                             {"00 1111111111 0000000000", NElectrons_4d, NElectrons_4d},
                                             {"00 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    CalculationRestrictions = {NFermions, NBosons, {"00 0000000000 1111111111", NElectrons_L2, NElectrons_L2 + (NConfigurations - 1)}}
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

Sk = DotProduct(WaveVector, {Sx, Sy, Sz})
Lk = DotProduct(WaveVector, {Lx, Ly, Lz})
Jk = DotProduct(WaveVector, {Jx, Jy, Jz})
Tk = DotProduct(WaveVector, {Tx, Ty, Tz})

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_4s, N_4d, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_4s>    <N_4d>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n"

if LmctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_4s, N_4d, N_L1, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_4s>    <N_4d>    <N_L1>          dZ\n"
    Header = Header .. "===========================================================================================================================================\n"
    Footer = "===========================================================================================================================================\n"
end

if MlctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_4s, N_4d, N_L2, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_4s>    <N_4d>    <N_L2>          dZ\n"
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
T_4s_4d = {}
for i = 1, NElectrons_4s / 2 do
    T_4s_4d[2*i - 1] = NewOperator("An", NFermions, IndexDn_4s[i])
    T_4s_4d[2*i]     = NewOperator("An", NFermions, IndexUp_4s[i])
end

if ShiftSpectra then
    Emin = Emin - (ZeroShift + ExperimentalShift)
    Emax = Emax - (ZeroShift + ExperimentalShift)
end

if CalculationRestrictions == nil then
    G_4s_4d = CreateSpectra(H_f, T_4s_4d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"DenseBorder", DenseBorder}})
else
    G_4s_4d = CreateSpectra(H_f, T_4s_4d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

if ShiftSpectra then
    G_4s_4d.Shift(ZeroShift + ExperimentalShift)
end

-- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
local dZ_4s_4d = {}
for _ in ipairs(T_4s_4d) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_4s_4d, dZ_i[j])
    end
end

-- Subtract the broadening used in the spectra calculations from the Lorentzian table.
for i, _ in ipairs(Lorentzian) do
    -- The FWHM is the second value in each pair.
    Lorentzian[i][2] = Lorentzian[i][2] - Gamma
end

Spectrum = "Photoemission"
if ValueInTable(Spectrum, SpectraToCalculate) then
    SpectrumIds = {}
    c = 1
    for i, Operator in ipairs(T_4s_4d) do
        table.insert(SpectrumIds, c)
        c = c + 1
    end

    Giso = GetSpectrum(G_4s_4d, SpectrumIds, dZ_4s_4d, #T_4s_4d, #Psis_i)
    SaveSpectrum(Giso, Prefix .. "_pho", Gaussian, Lorentzian)
end
