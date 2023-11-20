--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 3d
-- symmetry: C3v
-- experiment: XAS
-- edge: K (1s)
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
PdHybridizationTerm = $PdHybridizationTerm
MagneticFieldTerm = $MagneticFieldTerm
ExchangeFieldTerm = $ExchangeFieldTerm

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 12

NElectrons_1s = 2
NElectrons_3d = $NElectrons_3d

IndexDn_1s = {0}
IndexUp_1s = {1}
IndexDn_3d = {2, 4, 6, 8, 10}
IndexUp_3d = {3, 5, 7, 9, 11}

if PdHybridizationTerm then
    NFermions = 18

    NElectrons_4p = 0

    IndexDn_4p = {12, 14, 16}
    IndexUp_4p = {13, 15, 17}
end

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_1s = NewOperator("Number", NFermions, IndexUp_1s, IndexUp_1s, {1})
     + NewOperator("Number", NFermions, IndexDn_1s, IndexDn_1s, {1})

N_3d = NewOperator("Number", NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

if AtomicTerm then
    F0_3d_3d = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
    F2_3d_3d = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
    F4_3d_3d = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

    F0_1s_3d = NewOperator("U", NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {1}, {0})
    G2_1s_3d = NewOperator("U", NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {0}, {1})

    U_3d_3d_i = $U(3d,3d)_i_value
    F2_3d_3d_i = $F2(3d,3d)_i_value * $F2(3d,3d)_i_scaleFactor
    F4_3d_3d_i = $F4(3d,3d)_i_value * $F4(3d,3d)_i_scaleFactor
    F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

    U_3d_3d_f = $U(3d,3d)_f_value
    F2_3d_3d_f = $F2(3d,3d)_f_value * $F2(3d,3d)_f_scaleFactor
    F4_3d_3d_f = $F4(3d,3d)_f_value * $F4(3d,3d)_f_scaleFactor
    F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
    U_1s_3d_f = $U(1s,3d)_f_value
    G2_1s_3d_f = $G2(1s,3d)_f_value * $G2(1s,3d)_f_scaleFactor
    F0_1s_3d_f = U_1s_3d_f + 1 / 10 * G2_1s_3d_f

    H_i = H_i + Chop(
          F0_3d_3d_i * F0_3d_3d
        + F2_3d_3d_i * F2_3d_3d
        + F4_3d_3d_i * F4_3d_3d)

    H_f = H_f + Chop(
          F0_3d_3d_f * F0_3d_3d
        + F2_3d_3d_f * F2_3d_3d
        + F4_3d_3d_f * F4_3d_3d
        + F0_1s_3d_f * F0_1s_3d
        + G2_1s_3d_f * G2_1s_3d)

    ldots_3d = NewOperator("ldots", NFermions, IndexUp_3d, IndexDn_3d)

    zeta_3d_i = $zeta(3d)_i_value * $zeta(3d)_i_scaleFactor

    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_3d_i * ldots_3d)

    H_f = H_f + Chop(
          zeta_3d_f * ldots_3d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Dq_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}})
    Dsigma_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, {{2, 0, -7}})
    Dtau_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, {{4, 0, -21}})

    Dq_3d_i = $10Dq(3d)_i_value / 10.0
    Dsigma_3d_i = $Dsigma(3d)_i_value
    Dtau_3d_i = $Dtau(3d)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1(t2g) %8.3f\n", -4 * Dq_3d_i - 2 * Dsigma_3d_i - 6 * Dtau_3d_i))
    io.write(string.format("e(t2g)  %8.3f\n", -4 * Dq_3d_i + Dsigma_3d_i + 2 / 3 * Dtau_3d_i))
    io.write(string.format("e(eg)   %8.3f\n", 6 * Dq_3d_i + 7 / 3 * Dtau_3d_i))
    io.write("================\n")
    io.write("For the C3v symmetry, the crystal field Hamiltonian is not necessarily diagonal in\n")
    io.write("the basis of the irreducible representations. See the König and Kremer book, page 56.\n")
    io.write(string.format("The non-digonal element <e(t2g)|H|e(eg)> is %.3f.\n", -math.sqrt(2) / 3 * (3 * Dsigma_3d_i - 5 * Dtau_3d_i)))
    io.write("\n")

    Dq_3d_f = $10Dq(3d)_f_value / 10.0
    Dsigma_3d_f = $Dsigma(3d)_f_value
    Dtau_3d_f = $Dtau(3d)_f_value

    H_i = H_i + Chop(
          Dq_3d_i * Dq_3d
        + Dsigma_3d_i * Dsigma_3d
        + Dtau_3d_i * Dtau_3d)

    H_f = H_f + Chop(
          Dq_3d_f * Dq_3d
        + Dsigma_3d_f * Dsigma_3d
        + Dtau_3d_f * Dtau_3d)
end

--------------------------------------------------------------------------------
-- Define the 3d-4p hybridization term.
--------------------------------------------------------------------------------
if PdHybridizationTerm then
  F0_3d_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
  F2_3d_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
  G1_3d_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
  G3_3d_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})
  G1_1s_4p = NewOperator("U", NFermions, IndexUp_1s, IndexDn_1s, IndexUp_4p, IndexDn_4p, {0}, {1})

  F2_3d_4p_i = $F2(3d,4p)_i_value * $F2(3d,4p)_i_scaleFactor
  G1_3d_4p_i = $G1(3d,4p)_i_value * $G1(3d,4p)_i_scaleFactor
  G3_3d_4p_i = $G3(3d,4p)_i_value * $G3(3d,4p)_i_scaleFactor

  F2_3d_4p_f = $F2(3d,4p)_i_value * $F2(3d,4p)_i_scaleFactor
  G1_3d_4p_f = $G1(3d,4p)_i_value * $G1(3d,4p)_i_scaleFactor
  G3_3d_4p_f = $G3(3d,4p)_i_value * $G3(3d,4p)_i_scaleFactor
  G1_1s_4p_f = $G1(1s,4p)_f_value * $G1(1s,4p)_f_scaleFactor

  H_i = H_i + Chop(
        F2_3d_4p_i * F2_3d_4p
      + G1_3d_4p_i * G1_3d_4p
      + G3_3d_4p_i * G3_3d_4p)

  H_f = H_f + Chop(
        F2_3d_4p_f * F2_3d_4p
      + G1_3d_4p_f * G1_3d_4p
      + G3_3d_4p_f * G3_3d_4p
      + G1_1s_4p_f * G1_1s_4p)

  ldots_4p = NewOperator("ldots", NFermions, IndexUp_4p, IndexDn_4p)

  zeta_4p_i = $zeta(4p)_i_value

  zeta_4p_f = $zeta(4p)_f_value

  H_i = H_i + Chop(
        zeta_4p_i * ldots_4p)

  H_f = H_f + Chop(
        zeta_4p_f * ldots_4p)

  N_4p = NewOperator("Number", NFermions, IndexUp_4p, IndexUp_4p, {1, 1, 1})
       + NewOperator("Number", NFermions, IndexDn_4p, IndexDn_4p, {1, 1, 1})

  Delta_3d_4p_i = $Delta(3d,4p)_i_value
  e_3d_i = -(NElectrons_3d - 1) * U_3d_3d_i / 2
  e_4p_i =  (NElectrons_3d - 1) * U_3d_3d_i / 2 + Delta_3d_4p_i

  Delta_3d_4p_f = $Delta(3d,4p)_f_value
  e_3d_f= -(NElectrons_3d - 1) * U_3d_3d_f / 2
  e_4p_f=  (NElectrons_3d - 1) * U_3d_3d_f / 2 + Delta_3d_4p_f

  H_i = H_i + Chop(
        e_3d_i * N_3d
      + e_4p_i * N_4p)

  H_f = H_f + Chop(
        e_3d_f * N_3d
      + e_4p_f * N_4p)

  Akm = {{1, 0, -math.sqrt(3 / 5)}, {3, 0, -7 / math.sqrt(15)}}
  Va1_3d_4p = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
            + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

  Akm = {{1, 0, math.sqrt(6 / 5)}, {3, 0, -14 / 3 * math.sqrt(2 / 15)}, {3, 3, -7 / 3 / math.sqrt(3)}, {3, -3, 7 / 3 / math.sqrt(3)}}
  Ve_eg_3d_4p = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
              + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

  Akm = {{1, 0, math.sqrt(3 / 5)}, {3, 0, -14 / 3 / math.sqrt(15)}, {3, 3, 7 / 3 * math.sqrt(2 / 3)}, {3, -3, -7 / 3 * math.sqrt(2 / 3)}}
  Ve_t2g_3d_4p = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
               + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

  Va1_3d_4p_i = $Va1(3d,4p)_i_value
  Ve_eg_3d_4p_i = $Ve(eg)(3d,4p)_i_value
  Ve_t2g_3d_4p_i = $Ve(t2g)(3d,4p)_i_value

  Va1_3d_4p_f = $Va1(3d,4p)_f_value
  Ve_eg_3d_4p_f = $Ve(eg)(3d,4p)_f_value
  Ve_t2g_3d_4p_f = $Ve(t2g)(3d,4p)_f_value

  H_i = H_i + Chop(
        Va1_3d_4p_i * Va1_3d_4p
      + Ve_eg_3d_4p_i * Ve_eg_3d_4p
      + Ve_t2g_3d_4p_i * Ve_t2g_3d_4p)

  H_f = H_f + Chop(
        Va1_3d_4p_f * Va1_3d_4p
      + Ve_eg_3d_4p_f * Ve_eg_3d_4p
      + Ve_t2g_3d_4p_f * Ve_t2g_3d_4p)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_3d = NewOperator("Sx", NFermions, IndexUp_3d, IndexDn_3d)
Sy_3d = NewOperator("Sy", NFermions, IndexUp_3d, IndexDn_3d)
Sz_3d = NewOperator("Sz", NFermions, IndexUp_3d, IndexDn_3d)
Ssqr_3d = NewOperator("Ssqr", NFermions, IndexUp_3d, IndexDn_3d)
Splus_3d = NewOperator("Splus", NFermions, IndexUp_3d, IndexDn_3d)
Smin_3d = NewOperator("Smin", NFermions, IndexUp_3d, IndexDn_3d)

Lx_3d = NewOperator("Lx", NFermions, IndexUp_3d, IndexDn_3d)
Ly_3d = NewOperator("Ly", NFermions, IndexUp_3d, IndexDn_3d)
Lz_3d = NewOperator("Lz", NFermions, IndexUp_3d, IndexDn_3d)
Lsqr_3d = NewOperator("Lsqr", NFermions, IndexUp_3d, IndexDn_3d)
Lplus_3d = NewOperator("Lplus", NFermions, IndexUp_3d, IndexDn_3d)
Lmin_3d = NewOperator("Lmin", NFermions, IndexUp_3d, IndexDn_3d)

Jx_3d = NewOperator("Jx", NFermions, IndexUp_3d, IndexDn_3d)
Jy_3d = NewOperator("Jy", NFermions, IndexUp_3d, IndexDn_3d)
Jz_3d = NewOperator("Jz", NFermions, IndexUp_3d, IndexDn_3d)
Jsqr_3d = NewOperator("Jsqr", NFermions, IndexUp_3d, IndexDn_3d)
Jplus_3d = NewOperator("Jplus", NFermions, IndexUp_3d, IndexDn_3d)
Jmin_3d = NewOperator("Jmin", NFermions, IndexUp_3d, IndexDn_3d)

Tx_3d = NewOperator("Tx", NFermions, IndexUp_3d, IndexDn_3d)
Ty_3d = NewOperator("Ty", NFermions, IndexUp_3d, IndexDn_3d)
Tz_3d = NewOperator("Tz", NFermions, IndexUp_3d, IndexDn_3d)

Sx = Sx_3d
Sy = Sy_3d
Sz = Sz_3d

Lx = Lx_3d
Ly = Ly_3d
Lz = Lz_3d

Jx = Jx_3d
Jy = Jy_3d
Jz = Jz_3d

Tx = Tx_3d
Ty = Ty_3d
Tz = Tz_3d

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
InitialRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_1s, NElectrons_1s},
                                           {"00 1111111111", NElectrons_3d, NElectrons_3d}}

FinalRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_1s - 1, NElectrons_1s - 1},
                                         {"00 1111111111", NElectrons_3d + 1, NElectrons_3d + 1}}

CalculationRestrictions = nil

if PdHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"11 0000000000 000000", NElectrons_1s, NElectrons_1s},
                                               {"00 1111111111 000000", NElectrons_3d, NElectrons_3d},
                                               {"00 0000000000 111111", NElectrons_4p, NElectrons_4p}}

    FinalRestrictions = {NFermions, NBosons, {"11 0000000000 000000", NElectrons_1s - 1, NElectrons_1s - 1},
                                             {"00 1111111111 000000", NElectrons_3d + 1, NElectrons_3d + 1},
                                             {"00 0000000000 111111", NElectrons_4p, NElectrons_4p}}

    CalculationRestrictions = {NFermions, NBosons, {"00 0000000000 111111", NElectrons_4p, NElectrons_4p + 1}}
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

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_1s, N_3d, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_1s>    <N_3d>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n"

if PdHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_1s, N_3d, N_4p, "dZ"}
    Header = "Analysis of the initial Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_1s>    <N_3d>    <N_4p>          dZ\n"
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
if PdHybridizationTerm then
    local t = math.sqrt(1 / 2)

    -- Quadrupolar operators.
    Txy_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t * I}, {2, 2, -t * I}})
    Txz_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t    }, {2, 1, -t    }})
    Tyz_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t * I}, {2, 1,  t * I}})
    Tx2y2_1s_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t    }, {2, 2,  t    }})
    Tz2_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2,  0, 1    }                })

    Er = {t * (Eh[1] - I * Ev[1]),
          t * (Eh[2] - I * Ev[2]),
          t * (Eh[3] - I * Ev[3])}

    El = {-t * (Eh[1] + I * Ev[1]),
          -t * (Eh[2] + I * Ev[2]),
          -t * (Eh[3] + I * Ev[3])}

    local T = {Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}
    Tv_1s_3d = CalculateT(T, Ev, WaveVector)
    Th_1s_3d = CalculateT(T, Eh, WaveVector)
    Tr_1s_3d = CalculateT(T, Er, WaveVector)
    Tl_1s_3d = CalculateT(T, El, WaveVector)
    Tk_1s_3d = CalculateT(T, WaveVector, WaveVector)

    -- Initialize a table with the available spectra and the required operators.
    SpectraAndOperators_1s_3d = {
        ["Isotropic Absorption"] = {Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d},
        ["Absorption"] = {Tk_1s_3d,},
        ["Circular Dichroic"] = {Tr_1s_3d, Tl_1s_3d},
        ["Linear Dichroic"] = {Tv_1s_3d, Th_1s_3d},
    }

    -- Create an unordered set with the required operators.
    local T_1s_3d = {}
    for Spectrum, Operators in pairs(SpectraAndOperators_1s_3d) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            for _, Operator in pairs(Operators) do
                T_1s_3d[Operator] = true
            end
        end
    end

    -- Give the operators table the form required by Quanty's functions.
    local T1 = {}
    for Operator, _ in pairs(T_1s_3d) do
        table.insert(T1, Operator)
    end
    T_1s_3d = T1

    -- Dipolar operators.
    Tx_1s_4p = NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1, -1, t    }, {1, 1, -t    }})
    Ty_1s_4p = NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1, -1, t * I}, {1, 1,  t * I}})
    Tz_1s_4p = NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1,  0, 1    }                })

    local T = {Tx_1s_4p, Ty_1s_4p, Tz_1s_4p}
    Tv_1s_4p = CalculateT(T, Ev)
    Th_1s_4p = CalculateT(T, Eh)
    Tr_1s_4p = CalculateT(T, Er)
    Tl_1s_4p = CalculateT(T, El)
    Tk_1s_4p = CalculateT(T, WaveVector)

    -- Initialize a table with the available spectra and the required operators.
    SpectraAndOperators_1s_4p = {
        ["Isotropic Absorption"] = {Tk_1s_4p, Tr_1s_4p, Tl_1s_4p},
        ["Absorption"] = {Tk_1s_4p,},
        ["Circular Dichroic"] = {Tr_1s_4p, Tl_1s_4p},
        ["Linear Dichroic"] = {Tv_1s_4p, Th_1s_4p},
    }

    -- Create an unordered set with the required operators.
    local T_1s_4p = {}
    for Spectrum, Operators in pairs(SpectraAndOperators_1s_4p) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            for _, Operator in pairs(Operators) do
                T_1s_4p[Operator] = true
            end
        end
    end

    -- Give the operators table the form required by Quanty's functions.
    local T2 = {}
    for Operator, _ in pairs(T_1s_4p) do
        table.insert(T2, Operator)
    end
    T_1s_4p = T2

    Emin = Emin - (ZeroShift + ExperimentalShift)
    Emax = Emax - (ZeroShift + ExperimentalShift)

    -- Calculate the spectra. Note that the CalculationRestrictions are active in this case.
    G_1s_3d = CreateSpectra(H_f, T_1s_3d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
    G_1s_4p = CreateSpectra(H_f, T_1s_4p, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})

    -- The prefactors are described in http://dx.doi.org/10.1103/PhysRevB.94.245115.
    --
    -- prefactor_1s_3d = 4 * math.pi^2 * alpha * a0^4 / (2 * hbar * c)^2 * ExperimentalShift   * P2_1s_3d^2
    -- prefactor_1s_4p = 4 * math.pi^2 * alpha * a0^2                    * ExperimentalShift^3 * P1_1s_4p^2
    --
    -- Here we set the prefactor for the quadrupolar spectrum to 1, to more
    -- easily compare the spectra with and without hybridization. Note however
    -- that the quadrupole spectrum without hybridization can look quite
    -- different from the quadrupolar part of the spectrum with hybridization.
    -- They are identical only if all parameters of the 3d-4p interaction are zero.
    --
    -- The dipolar prefactor then becomes:
    --
    -- prefactor_1s_4p = (2 * hbar * c)^2 / (a0 * ExperimentalShift)^2 * (P1_1s_4p / P2_1s_3d)^2

    alpha = 7.2973525664E-3
    a0 = 5.2917721067E-1
    hbar = 6.582119514E-16
    c = 2.99792458E+18

    P1_1s_4p = $P1(1s,4p)
    P2_1s_3d = $P2(1s,3d)

    prefactor_1s_3d = 1
    prefactor_1s_4p = (2 * hbar * c)^2 / (a0 * ExperimentalShift)^2 * (P1_1s_4p / P2_1s_3d)^2

    io.write("\n")
    io.write("Spectra prefactors\n")
    io.write("==================\n")
    io.write(string.format("Dipolar     = %.1f\n", prefactor_1s_4p))
    io.write("Quadrupolar =  1.0\n")
    io.write("==================\n")

    G_1s_3d = prefactor_1s_3d * G_1s_3d
    G_1s_4p = prefactor_1s_4p * G_1s_4p

    if ShiftSpectra then
        G_1s_3d.Shift(ZeroShift + ExperimentalShift)
        G_1s_4p.Shift(ZeroShift + ExperimentalShift)
    end

    -- Subtract the broadening used in the spectra calculations from the Lorentzian table.
    for i, _ in ipairs(Lorentzian) do
        -- The FWHM is the second value in each pair.
        Lorentzian[i][2] = Lorentzian[i][2] - Gamma
    end

    -- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
    local dZ_1s_3d = {}
    for _ in ipairs(T_1s_3d) do
        for j in ipairs(Psis_i) do
            table.insert(dZ_1s_3d, dZ_i[j])
        end
    end

    local Ids_1s_3d = {}
    for k, v in pairs(T_1s_3d) do
        Ids_1s_3d[v] = k
    end

    for Spectrum, Operators in pairs(SpectraAndOperators_1s_3d) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            -- Find the indices of the spectrum's operators in the table used during the
            -- calculation (this is unsorted).
            SpectrumIds_1s_3d = {}
            for _, Operator in pairs(Operators) do
                table.insert(SpectrumIds_1s_3d, Ids_1s_3d[Operator])
            end

            if Spectrum == "Isotropic Absorption" then
                Giso_1s_3d = GetSpectrum(G_1s_3d, SpectrumIds_1s_3d, dZ_1s_3d, #T_1s_3d, #Psis_i)
            end

            if Spectrum == "Absorption" then
                Gk_1s_3d = GetSpectrum(G_1s_3d, SpectrumIds_1s_3d, dZ_1s_3d, #T_1s_3d, #Psis_i)
            end

            if Spectrum == "Circular Dichroic" then
                Gr_1s_3d = GetSpectrum(G_1s_3d, SpectrumIds_1s_3d[1], dZ_1s_3d, #T_1s_3d, #Psis_i)
                Gl_1s_3d = GetSpectrum(G_1s_3d, SpectrumIds_1s_3d[2], dZ_1s_3d, #T_1s_3d, #Psis_i)
            end

            if Spectrum == "Linear Dichroic" then
                Gv_1s_3d = GetSpectrum(G_1s_3d, SpectrumIds_1s_3d[1], dZ_1s_3d, #T_1s_3d, #Psis_i)
                Gh_1s_3d = GetSpectrum(G_1s_3d, SpectrumIds_1s_3d[2], dZ_1s_3d, #T_1s_3d, #Psis_i)
            end
        end
    end

    local dZ_1s_4p = {}
    for _ in ipairs(T_1s_4p) do
        for j in ipairs(Psis_i) do
            table.insert(dZ_1s_4p, dZ_i[j])
        end
    end

    -- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
    local Ids_1s_4p = {}
    for k, v in pairs(T_1s_4p) do
        Ids_1s_4p[v] = k
    end

    for Spectrum, Operators in pairs(SpectraAndOperators_1s_4p) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            -- Find the indices of the spectrum's operators in the table used during the
            -- calculation (this is unsorted).
            SpectrumIds_1s_4p = {}
            for _, Operator in pairs(Operators) do
                table.insert(SpectrumIds_1s_4p, Ids_1s_4p[Operator])
            end

            if Spectrum == "Isotropic Absorption" then
                Giso_1s_4p = GetSpectrum(G_1s_4p, SpectrumIds_1s_4p, dZ_1s_4p, #T_1s_4p, #Psis_i)
                Giso_1s_3d = Giso_1s_3d / 15
                Giso_1s_4p = Giso_1s_4p / 3
                Giso = Giso_1s_3d + Giso_1s_4p
                SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, Lorentzian)
                SaveSpectrum(Giso_1s_4p, Prefix .. "_iso_dip", Gaussian, Lorentzian)
                SaveSpectrum(Giso_1s_3d, Prefix .. "_iso_quad", Gaussian, Lorentzian)
            end

            if Spectrum == "Absorption" then
                Gk_1s_4p = GetSpectrum(G_1s_4p, SpectrumIds_1s_4p, dZ_1s_4p, #T_1s_4p, #Psis_i)
                Gk = Gk_1s_3d + Gk_1s_4p
                SaveSpectrum(Gk, Prefix .. "_k", Gaussian, Lorentzian)
                SaveSpectrum(Gk_1s_4p, Prefix .. "_k_dip", Gaussian, Lorentzian)
                SaveSpectrum(Gk_1s_3d, Prefix .. "_k_quad", Gaussian, Lorentzian)
            end

            if Spectrum == "Circular Dichroic" then
                Gr_1s_4p = GetSpectrum(G_1s_4p, SpectrumIds_1s_4p[1], dZ_1s_4p, #T_1s_4p, #Psis_i)
                Gl_1s_4p = GetSpectrum(G_1s_4p, SpectrumIds_1s_4p[2], dZ_1s_4p, #T_1s_4p, #Psis_i)
                Gr = Gr_1s_3d + Gr_1s_4p
                Gl = Gl_1s_3d + Gl_1s_4p
                SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian)
                SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian)
                SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
                SaveSpectrum(Gr_1s_4p - Gl_1s_4p, Prefix .. "_cd_dip", Gaussian, Lorentzian)
                SaveSpectrum(Gr_1s_3d - Gl_1s_3d, Prefix .. "_cd_quad", Gaussian, Lorentzian)
            end

            if Spectrum == "Linear Dichroic" then
                Gv_1s_4p = GetSpectrum(G_1s_4p, SpectrumIds_1s_4p[1], dZ_1s_4p, #T_1s_4p, #Psis_i)
                Gh_1s_4p = GetSpectrum(G_1s_4p, SpectrumIds_1s_4p[2], dZ_1s_4p, #T_1s_4p, #Psis_i)
                Gv = Gv_1s_3d + Gv_1s_4p
                Gh = Gh_1s_3d + Gh_1s_4p
                SaveSpectrum(Gv, Prefix .. "_v", Gaussian, Lorentzian)
                SaveSpectrum(Gh, Prefix .. "_h", Gaussian, Lorentzian)
                SaveSpectrum(Gv - Gh, Prefix .. "_ld", Gaussian, Lorentzian)
                SaveSpectrum(Gv_1s_4p - Gh_1s_4p, Prefix .. "_ld_dip", Gaussian, Lorentzian)
                SaveSpectrum(Gv_1s_3d - Gh_1s_3d, Prefix .. "_ld_quad", Gaussian, Lorentzian)
            end
        end
    end
else
    local t = math.sqrt(1 / 2)

    Txy_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t * I}, {2, 2, -t * I}})
    Txz_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t    }, {2, 1, -t    }})
    Tyz_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t * I}, {2, 1,  t * I}})
    Tx2y2_1s_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t    }, {2, 2,  t    }})
    Tz2_1s_3d   = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2,  0, 1    }                })

    Er = {t * (Eh[1] - I * Ev[1]),
          t * (Eh[2] - I * Ev[2]),
          t * (Eh[3] - I * Ev[3])}

    El = {-t * (Eh[1] + I * Ev[1]),
          -t * (Eh[2] + I * Ev[2]),
          -t * (Eh[3] + I * Ev[3])}

    local T = {Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}
    Tv_1s_3d = CalculateT(T, Ev, WaveVector)
    Th_1s_3d = CalculateT(T, Eh, WaveVector)
    Tr_1s_3d = CalculateT(T, Er, WaveVector)
    Tl_1s_3d = CalculateT(T, El, WaveVector)
    Tk_1s_3d = CalculateT(T, WaveVector, WaveVector)

    -- Initialize a table with the available spectra and the required operators.
    SpectraAndOperators = {
        ["Isotropic Absorption"] = {Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d},
        ["Absorption"] = {Tk_1s_3d,},
        ["Circular Dichroic"] = {Tr_1s_3d, Tl_1s_3d},
        ["Linear Dichroic"] = {Tv_1s_3d, Th_1s_3d},
    }

    -- Create an unordered set with the required operators.
    local T_1s_3d = {}
    for Spectrum, Operators in pairs(SpectraAndOperators) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            for _, Operator in pairs(Operators) do
                T_1s_3d[Operator] = true
            end
        end
    end

    -- Give the operators table the form required by Quanty's functions.
    local T = {}
    for Operator, _ in pairs(T_1s_3d) do
        table.insert(T, Operator)
    end
    T_1s_3d = T

    Emin = Emin - (ZeroShift + ExperimentalShift)
    Emax = Emax - (ZeroShift + ExperimentalShift)

    if CalculationRestrictions == nil then
        G_1s_3d = CreateSpectra(H_f, T_1s_3d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"DenseBorder", DenseBorder}})
    else
        G_1s_3d = CreateSpectra(H_f, T_1s_3d, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
    end

    if ShiftSpectra then
        G_1s_3d.Shift(ZeroShift + ExperimentalShift)
    end

    -- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
    local dZ_1s_3d = {}
    for _ in ipairs(T_1s_3d) do
        for j in ipairs(Psis_i) do
            table.insert(dZ_1s_3d, dZ_i[j])
        end
    end

    local Ids = {}
    for k, v in pairs(T_1s_3d) do
        Ids[v] = k
    end

    -- Subtract the broadening used in the spectra calculations from the Lorentzian table.
    for i, _ in ipairs(Lorentzian) do
        -- The FWHM is the second value in each pair.
        Lorentzian[i][2] = Lorentzian[i][2] - Gamma
    end

    Pcl_1s_3d = 1

    for Spectrum, Operators in pairs(SpectraAndOperators) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            -- Find the indices of the spectrum's operators in the table used during the
            -- calculation (this is unsorted).
            SpectrumIds = {}
            for _, Operator in pairs(Operators) do
                table.insert(SpectrumIds, Ids[Operator])
            end

            if Spectrum == "Isotropic Absorption" then
                Giso = GetSpectrum(G_1s_3d, SpectrumIds, dZ_1s_3d, #T_1s_3d, #Psis_i)
                Giso = Giso / 15
                SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, Lorentzian, Pcl_1s_3d)
            end

            if Spectrum == "Absorption" then
                Gk = GetSpectrum(G_1s_3d, SpectrumIds, dZ_1s_3d, #T_1s_3d, #Psis_i)
                SaveSpectrum(Gk, Prefix .. "_k", Gaussian, Lorentzian, Pcl_1s_3d)
            end

            if Spectrum == "Circular Dichroic" then
                Gr = GetSpectrum(G_1s_3d, SpectrumIds[1], dZ_1s_3d, #T_1s_3d, #Psis_i)
                Gl = GetSpectrum(G_1s_3d, SpectrumIds[2], dZ_1s_3d, #T_1s_3d, #Psis_i)
                SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian, Pcl_1s_3d)
                SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian, Pcl_1s_3d)
                SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
            end

            if Spectrum == "Linear Dichroic" then
                Gv = GetSpectrum(G_1s_3d, SpectrumIds[1], dZ_1s_3d, #T_1s_3d, #Psis_i)
                Gh = GetSpectrum(G_1s_3d, SpectrumIds[2], dZ_1s_3d, #T_1s_3d, #Psis_i)
                SaveSpectrum(Gv, Prefix .. "_v", Gaussian, Lorentzian, Pcl_1s_3d)
                SaveSpectrum(Gh, Prefix .. "_h", Gaussian, Lorentzian, Pcl_1s_3d)
                SaveSpectrum(Gv - Gh, Prefix .. "_ld", Gaussian, Lorentzian)
            end
        end
    end
end
