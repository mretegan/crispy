--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4d
-- symmetry: D4h
-- experiment: XAS
-- edge: M2,3 (3p)
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

Emin = $XEmin  -- minimum value of the energy range (eV)
Emax = $XEmax  -- maximum value of the energy range (eV)
NPoints = $XNPoints  -- number of points of the spectra
ExperimentalShift = $XExperimentalShift  -- experimental edge energy (eV)
ZeroShift = $XZeroShift  -- energy required to shift the calculated spectrum to start from approximately zero (eV)
Gaussian = $XGaussian  -- Gaussian FWHM (eV)
Lorentzian = $XLorentzian  -- Lorentzian FWHM (eV)

WaveVector = $XWaveVector  -- wave vector
Ev = $XFirstPolarization  -- vertical polarization
Eh = $XSecondPolarization  -- horizontal polarization

SpectraToCalculate = $SpectraToCalculate  -- types of spectra to calculate
DenseBorder = $DenseBorder -- number of determinants where we switch from dense methods to sparse methods

Prefix = "$Prefix"  -- file name prefix

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

NElectrons_3p = 6
NElectrons_4d = $NElectrons_4d

IndexDn_3p = {0, 2, 4}
IndexUp_3p = {1, 3, 5}
IndexDn_4d = {6, 8, 10, 12, 14}
IndexUp_4d = {7, 9, 11, 13, 15}

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
H_f = 0

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_3p = NewOperator("Number", NFermions, IndexUp_3p, IndexUp_3p, {1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_3p, IndexDn_3p, {1, 1, 1})

N_4d = NewOperator("Number", NFermions, IndexUp_4d, IndexUp_4d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_4d, IndexDn_4d, {1, 1, 1, 1, 1})

if AtomicTerm then
    F0_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {1, 0, 0})
    F2_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {0, 1, 0})
    F4_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {0, 0, 1})

    F0_3p_4d = NewOperator("U", NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {1, 0}, {0, 0})
    F2_3p_4d = NewOperator("U", NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {0, 1}, {0, 0})
    G1_3p_4d = NewOperator("U", NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {0, 0}, {1, 0})
    G3_3p_4d = NewOperator("U", NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {0, 0}, {0, 1})

    U_4d_4d_i = $U(4d,4d)_i_value
    F2_4d_4d_i = $F2(4d,4d)_i_value * $F2(4d,4d)_i_scaleFactor
    F4_4d_4d_i = $F4(4d,4d)_i_value * $F4(4d,4d)_i_scaleFactor
    F0_4d_4d_i = U_4d_4d_i + 2 / 63 * F2_4d_4d_i + 2 / 63 * F4_4d_4d_i

    U_4d_4d_f = $U(4d,4d)_f_value
    F2_4d_4d_f = $F2(4d,4d)_f_value * $F2(4d,4d)_f_scaleFactor
    F4_4d_4d_f = $F4(4d,4d)_f_value * $F4(4d,4d)_f_scaleFactor
    F0_4d_4d_f = U_4d_4d_f + 2 / 63 * F2_4d_4d_f + 2 / 63 * F4_4d_4d_f
    U_3p_4d_f = $U(3p,4d)_f_value
    F2_3p_4d_f = $F2(3p,4d)_f_value * $F2(3p,4d)_f_scaleFactor
    G1_3p_4d_f = $G1(3p,4d)_f_value * $G1(3p,4d)_f_scaleFactor
    G3_3p_4d_f = $G3(3p,4d)_f_value * $G3(3p,4d)_f_scaleFactor
    F0_3p_4d_f = U_3p_4d_f + 1 / 15 * G1_3p_4d_f + 3 / 70 * G3_3p_4d_f

    H_i = H_i + Chop(
          F0_4d_4d_i * F0_4d_4d
        + F2_4d_4d_i * F2_4d_4d
        + F4_4d_4d_i * F4_4d_4d)

    H_f = H_f + Chop(
          F0_4d_4d_f * F0_4d_4d
        + F2_4d_4d_f * F2_4d_4d
        + F4_4d_4d_f * F4_4d_4d
        + F0_3p_4d_f * F0_3p_4d
        + F2_3p_4d_f * F2_3p_4d
        + G1_3p_4d_f * G1_3p_4d
        + G3_3p_4d_f * G3_3p_4d)

    ldots_4d = NewOperator("ldots", NFermions, IndexUp_4d, IndexDn_4d)

    ldots_3p = NewOperator("ldots", NFermions, IndexUp_3p, IndexDn_3p)

    zeta_4d_i = $zeta(4d)_i_value * $zeta(4d)_i_scaleFactor

    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scaleFactor
    zeta_3p_f = $zeta(3p)_f_value * $zeta(3p)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_4d_i * ldots_4d)

    H_f = H_f + Chop(
          zeta_4d_f * ldots_4d
        + zeta_3p_f * ldots_3p)
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
    e_4d_i = (10 * Delta_4d_L1_i - NElectrons_4d * (19 + NElectrons_4d) * U_4d_4d_i / 2) / (10 + NElectrons_4d)
    e_L1_i = NElectrons_4d * ((1 + NElectrons_4d) * U_4d_4d_i / 2 - Delta_4d_L1_i) / (10 + NElectrons_4d)

    Delta_4d_L1_f = $Delta(4d,L1)_f_value
    e_4d_f = (10 * Delta_4d_L1_f - NElectrons_4d * (31 + NElectrons_4d) * U_4d_4d_f / 2 - 90 * U_3p_4d_f) / (16 + NElectrons_4d)
    e_3p_f = (10 * Delta_4d_L1_f + (1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 - (10 + NElectrons_4d) * U_3p_4d_f)) / (16 + NElectrons_4d)
    e_L1_f = ((1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 + 6 * U_3p_4d_f) - (6 + NElectrons_4d) * Delta_4d_L1_f) / (16 + NElectrons_4d)

    H_i = H_i + Chop(
          e_4d_i * N_4d
        + e_L1_i * N_L1)

    H_f = H_f + Chop(
          e_4d_f * N_4d
        + e_3p_f * N_3p
        + e_L1_f * N_L1)

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
    e_4d_i = U_4d_4d_i * (-NElectrons_4d + 1) / 2
    e_L2_i = Delta_4d_L2_i - U_4d_4d_i * NElectrons_4d / 2 - U_4d_4d_i / 2

    Delta_4d_L2_f = $Delta(4d,L2)_f_value
    e_4d_f = -(U_4d_4d_f * NElectrons_4d^2 + 11 * U_4d_4d_f * NElectrons_4d + 60 * U_3p_4d_f) / (2 * NElectrons_4d + 12)
    e_3p_f = NElectrons_4d * (U_4d_4d_f * NElectrons_4d + U_4d_4d_f - 2 * U_3p_4d_f * NElectrons_4d - 2 * U_3p_4d_f) / (2 * (NElectrons_4d + 6))
    e_L2_f = (2 * Delta_4d_L2_f * NElectrons_4d + 12 * Delta_4d_L2_f + U_4d_4d_f * NElectrons_4d^2 - U_4d_4d_f * NElectrons_4d - 12 * U_4d_4d_f + 12 * U_3p_4d_f * NElectrons_4d + 12 * U_3p_4d_f) / (2 * (NElectrons_4d + 6))

    H_i = H_i + Chop(
          e_4d_i * N_4d
        + e_L2_i * N_L2)

    H_f = H_f + Chop(
          e_4d_f * N_4d
        + e_3p_f * N_3p
        + e_L2_f * N_L2)

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
    Bx_i = $Bx_i_value * EnergyUnits.Tesla.value
    By_i = $By_i_value * EnergyUnits.Tesla.value
    Bz_i = $Bz_i_value * EnergyUnits.Tesla.value

    Bx_f = $Bx_f_value * EnergyUnits.Tesla.value
    By_f = $By_f_value * EnergyUnits.Tesla.value
    Bz_f = $Bz_f_value * EnergyUnits.Tesla.value

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
    -- Extract the spectrum corresponding to the operators identified
    -- using the Ids argument. The returned spectrum is a weighted
    -- sum where the weights are the Boltzmann probabilities.
    --
    -- @param G: spectrum object as returned by the functions defined in Quanty, i.e. one spectrum
    --           for each operator and each wavefunction.
    -- @param Ids: indexes of the operators that are considered in the returned spectrum
    -- @param dZ: Boltzmann prefactors for each of the spectrum in the spectra object
    -- @param NOperators: number of transition operators
    -- @param NPsis: number of wavefunctions

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

function SaveSpectrum(G, Filename, Gaussian, Lorentzian)
    G = -1 * G
    G.Broaden(Gaussian, Lorentzian)
    G.Print({{"file", Filename .. ".spec"}})
end

function DotProduct(a, b)
    return Chop(a[1] * b[1] + a[2] * b[2] + a[3] * b[3])
end

function WavefunctionsAndBoltzmannFactors(H, NPsis, NPsisAuto, Temperature, Threshold, StartRestrictions, CalculationRestrictions)
    -- Calculate the wavefunctions and Boltzmann factors of a Hamiltonian.
    --
    -- @param H: Hamiltonian for which to calculate the wavefunctions
    -- @param NPsis: number of wavefunctions
    -- @param NPsisAuto: determine automatically the number of wavefunctions that are populated at the specified
    --                   temperature and within the threshold
    -- @param Temperature: temperature in eV
    -- @param Threshold: threshold used to determine the number of wavefunction in the automatic procedure
    -- @param StartRestrictions: occupancy restrictions at the start of the calculation
    -- @param CalculationRestrictions: restrictions during the calculation
    -- @return Psis: wavefunctions
    -- @return dZ: Boltzmann factors

    if Threshold == nil then
        Threshold = 1e-8
    end

    local dZ = {}
    local Z = 0
    local Psis

    if NPsisAuto == true and NPsis ~= 1 then
        NPsis = 4
        local NpsisIncrement = 8
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
                NPsis = NPsis + NpsisIncrement
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
        for j, operator in ipairs(Operators) do
            if j == 1 then
                io.write(string.format("%12.6f", Complex.Re(Psi * operator * Psi)))
            elseif operator == "dZ" then
                io.write(string.format("%12.2e", dZ[i]))
            else
                io.write(string.format("%10.4f", Complex.Re(Psi * operator * Psi)))
            end
        end
        io.write("\n")
    end
    io.write(Footer)
end

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_3p, NElectrons_3p},
                                           {"000000 1111111111", NElectrons_4d, NElectrons_4d}}

FinalRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_3p - 1, NElectrons_3p - 1},
                                         {"000000 1111111111", NElectrons_4d + 1, NElectrons_4d + 1}}

CalculationRestrictions = nil

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_3p, NElectrons_3p},
                                               {"000000 1111111111 0000000000", NElectrons_4d, NElectrons_4d},
                                               {"000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_3p - 1, NElectrons_3p - 1},
                                             {"000000 1111111111 0000000000", NElectrons_4d + 1, NElectrons_4d + 1},
                                             {"000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {"000000 0000000000 1111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

if MlctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_3p, NElectrons_3p},
                                               {"000000 1111111111 0000000000", NElectrons_4d, NElectrons_4d},
                                               {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    FinalRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_3p - 1, NElectrons_3p - 1},
                                             {"000000 1111111111 0000000000", NElectrons_4d + 1, NElectrons_4d + 1},
                                             {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    CalculationRestrictions = {NFermions, NBosons, {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2 + (NConfigurations - 1)}}
end

--------------------------------------------------------------------------------
-- Analyze the initial Hamiltonian.
--------------------------------------------------------------------------------
Temperature = Temperature * EnergyUnits.Kelvin.value

Sk = DotProduct(WaveVector, {Sx, Sy, Sz})
Lk = DotProduct(WaveVector, {Lx, Ly, Lz})
Jk = DotProduct(WaveVector, {Jx, Jy, Jz})
Tk = DotProduct(WaveVector, {Tx, Ty, Tz})

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_3p, N_4d, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3p>    <N_4d>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n\n"

if LmctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_3p, N_4d, N_L1, 'dZ'}
    Header = 'Analysis of the initial Hamiltonian:\n'
    Header = Header .. '===========================================================================================================================================\n'
    Header = Header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3p>    <N_4d>    <N_L1>          dZ\n'
    Header = Header .. '===========================================================================================================================================\n'
    Footer = '===========================================================================================================================================\n'
end

if MlctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_3p, N_4d, N_L2, 'dZ'}
    Header = 'Analysis of the initial Hamiltonian:\n'
    Header = Header .. '===========================================================================================================================================\n'
    Header = Header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3p>    <N_4d>    <N_L2>          dZ\n'
    Header = Header .. '===========================================================================================================================================\n'
    Footer = '===========================================================================================================================================\n'
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

Tx_3p_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_3p, IndexDn_3p, {{1, -1, t}, {1, 1, -t}})
Ty_3p_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_3p, IndexDn_3p, {{1, -1, t * I}, {1, 1, t * I}})
Tz_3p_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_3p, IndexDn_3p, {{1, 0, 1}})

Er = {t * (Eh[1] - I * Ev[1]),
      t * (Eh[2] - I * Ev[2]),
      t * (Eh[3] - I * Ev[3])}

El = {-t * (Eh[1] + I * Ev[1]),
      -t * (Eh[2] + I * Ev[2]),
      -t * (Eh[3] + I * Ev[3])}

Tv_3p_4d = DotProduct(Ev, {Tx_3p_4d, Ty_3p_4d, Tz_3p_4d})
Th_3p_4d = DotProduct(Eh, {Tx_3p_4d, Ty_3p_4d, Tz_3p_4d})
Tr_3p_4d = DotProduct(Er, {Tx_3p_4d, Ty_3p_4d, Tz_3p_4d})
Tl_3p_4d = DotProduct(El, {Tx_3p_4d, Ty_3p_4d, Tz_3p_4d})
Tk_3p_4d = DotProduct(WaveVector, {Tx_3p_4d, Ty_3p_4d, Tz_3p_4d})

-- Initialize a table with the available spectra and the required operators.
SpectraAndOperators = {
    ["Isotropic Absorption"] = {Tk_3p_4d, Tr_3p_4d, Tl_3p_4d},
    ["Absorption"] = {Tk_3p_4d,},
    ["Circular Dichroic"] = {Tr_3p_4d, Tl_3p_4d},
    ["Linear Dichroic"] = {Tv_3p_4d, Th_3p_4d},
}

-- Create an unordered set with the required operators.
local T_3p_4d = {}
for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        for _, Operator in pairs(Operators) do
            T_3p_4d[Operator] = true
        end
    end
end

-- Give the operators table the form required by Quanty's functions.
local T = {}
for Operator, _ in pairs(T_3p_4d) do
    table.insert(T, Operator)
end
T_3p_4d = T

Gamma = 0.1

Emin = Emin - (ZeroShift + ExperimentalShift)
Emax = Emax - (ZeroShift + ExperimentalShift)

if CalculationRestrictions == nil then
    G_3p_4d = CreateSpectra(H_f, T_3p_4d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"DenseBorder", DenseBorder}})
else
    G_3p_4d = CreateSpectra(H_f, T_3p_4d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

-- Shift the calculated spectrum.
G_3p_4d.Shift(ZeroShift + ExperimentalShift)

-- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
local dZ_3p_4d = {}
for _ in ipairs(T_3p_4d) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_3p_4d, dZ_i[j])
    end
end

local Ids = {}
for k, v in pairs(T_3p_4d) do
    Ids[v] = k
end

for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        -- Find the indices of the spectrum's operators in the table used during the
        -- calculation (this is unsorted).
        SpectrumIds = {}
        for _, Operator in pairs(Operators) do
            table.insert(SpectrumIds, Ids[Operator])
        end

        if Spectrum == "Isotropic Absorption" then
            Pcl_3p_4d = 2
            Giso = GetSpectrum(G_3p_4d, SpectrumIds, dZ_3p_4d, #T_3p_4d, #Psis_i)
            Giso = Giso / 3 / Pcl_3p_4d
            SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, Lorentzian)
        end

        if Spectrum == "Absorption" then
            Gk = GetSpectrum(G_3p_4d, SpectrumIds, dZ_3p_4d, #T_3p_4d, #Psis_i)
            SaveSpectrum(Gk, Prefix .. "_k", Gaussian, Lorentzian)
        end

        if Spectrum == "Circular Dichroic" then
            Gr = GetSpectrum(G_3p_4d, SpectrumIds[1], dZ_3p_4d, #T_3p_4d, #Psis_i)
            Gl = GetSpectrum(G_3p_4d, SpectrumIds[2], dZ_3p_4d, #T_3p_4d, #Psis_i)
            SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian)
            SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian)
            SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
        end

        if Spectrum == "Linear Dichroic" then
            Gv = GetSpectrum(G_3p_4d, SpectrumIds[1], dZ_3p_4d, #T_3p_4d, #Psis_i)
            Gh = GetSpectrum(G_3p_4d, SpectrumIds[2], dZ_3p_4d, #T_3p_4d, #Psis_i)
            SaveSpectrum(Gv, Prefix .. "_v", Gaussian, Lorentzian)
            SaveSpectrum(Gh, Prefix .. "_h", Gaussian, Lorentzian)
            SaveSpectrum(Gv - Gh, Prefix .. "_ld", Gaussian, Lorentzian)
        end
    end
end