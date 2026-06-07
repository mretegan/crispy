--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4d
-- symmetry: D3d
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
NFermions = 16

NElectrons_2p = 6
NElectrons_4d = $NElectrons_4d

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_4d = {6, 8, 10, 12, 14}
IndexUp_4d = {7, 9, 11, 13, 15}

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

if AtomicTerm then
    F0_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {1, 0, 0})
    F2_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {0, 1, 0})
    F4_4d_4d = NewOperator("U", NFermions, IndexUp_4d, IndexDn_4d, {0, 0, 1})

    F0_2p_4d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {1, 0}, {0, 0})
    F2_2p_4d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {0, 1}, {0, 0})
    G1_2p_4d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {0, 0}, {1, 0})
    G3_2p_4d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {0, 0}, {0, 1})

    U_4d_4d_i = $U(4d,4d)_i_value
    F2_4d_4d_i = $F2(4d,4d)_i_value * $F2(4d,4d)_i_scaleFactor
    F4_4d_4d_i = $F4(4d,4d)_i_value * $F4(4d,4d)_i_scaleFactor
    F0_4d_4d_i = U_4d_4d_i + 2 / 63 * F2_4d_4d_i + 2 / 63 * F4_4d_4d_i

    U_4d_4d_m = $U(4d,4d)_m_value
    F2_4d_4d_m = $F2(4d,4d)_m_value * $F2(4d,4d)_m_scaleFactor
    F4_4d_4d_m = $F4(4d,4d)_m_value * $F4(4d,4d)_m_scaleFactor
    F0_4d_4d_m = U_4d_4d_m + 2 / 63 * F2_4d_4d_m + 2 / 63 * F4_4d_4d_m
    U_2p_4d_m = $U(2p,4d)_m_value
    F2_2p_4d_m = $F2(2p,4d)_m_value * $F2(2p,4d)_m_scaleFactor
    G1_2p_4d_m = $G1(2p,4d)_m_value * $G1(2p,4d)_m_scaleFactor
    G3_2p_4d_m = $G3(2p,4d)_m_value * $G3(2p,4d)_m_scaleFactor
    F0_2p_4d_m = U_2p_4d_m + 1 / 15 * G1_2p_4d_m + 3 / 70 * G3_2p_4d_m

    U_4d_4d_f = $U(4d,4d)_f_value
    F2_4d_4d_f = $F2(4d,4d)_f_value * $F2(4d,4d)_f_scaleFactor
    F4_4d_4d_f = $F4(4d,4d)_f_value * $F4(4d,4d)_f_scaleFactor
    F0_4d_4d_f = U_4d_4d_f + 2 / 63 * F2_4d_4d_f + 2 / 63 * F4_4d_4d_f

    H_i = H_i + Chop(
          F0_4d_4d_i * F0_4d_4d
        + F2_4d_4d_i * F2_4d_4d
        + F4_4d_4d_i * F4_4d_4d)

    H_m = H_m + Chop(
          F0_4d_4d_m * F0_4d_4d
        + F2_4d_4d_m * F2_4d_4d
        + F4_4d_4d_m * F4_4d_4d
        + F0_2p_4d_m * F0_2p_4d
        + F2_2p_4d_m * F2_2p_4d
        + G1_2p_4d_m * G1_2p_4d
        + G3_2p_4d_m * G3_2p_4d)

    H_f = H_f + Chop(
          F0_4d_4d_f * F0_4d_4d
        + F2_4d_4d_f * F2_4d_4d
        + F4_4d_4d_f * F4_4d_4d)

    ldots_4d = NewOperator("ldots", NFermions, IndexUp_4d, IndexDn_4d)

    ldots_2p = NewOperator("ldots", NFermions, IndexUp_2p, IndexDn_2p)

    zeta_4d_i = $zeta(4d)_i_value * $zeta(4d)_i_scaleFactor

    zeta_4d_m = $zeta(4d)_m_value * $zeta(4d)_m_scaleFactor
    zeta_2p_m = $zeta(2p)_m_value * $zeta(2p)_m_scaleFactor

    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_4d_i * ldots_4d)

    H_m = H_m + Chop(
          zeta_4d_m * ldots_4d
        + zeta_2p_m * ldots_2p)

    H_f = H_f + Chop(
          zeta_4d_f * ldots_4d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3d crystal field in the Zy orientation (C3 axis along z, a basal C2 axis
    -- along y), taken from the Quanty point-group tables:
    -- https://www.quanty.org/physics_chemistry/point_groups/d3d/orientation_zy
    --
    -- The five 4d orbitals split into a1g + 2 eg. The two eg pairs descend from
    -- the cubic eg (egσ) and t2g (egπ); they share the same irrep and so
    -- mix through a single off-diagonal element Meg. The on-site Hamiltonian in
    -- the (a1g, egσ, egπ) symmetry-adapted basis is
    --
    --     [ Ea1g    0      0    ]
    --     [   0    Eegσ   Meg   ]
    --     [   0    Meg    Eegπ  ]
    --
    -- The crystal-field potential expanded on the renormalized spherical
    -- harmonics is (Quanty Zy page, k = 0 monopole shift dropped):
    --
    --   {2,  0,   Ea1g + Eegsigma - 2*Eegpi}
    --   {4,  0,   (3/5)*(3*Ea1g - 4*Eegsigma + Eegpi)}
    --   {4, +-3, +-3*sqrt(7/5)*Meg}
    --
    -- Building one operator per parameter (the Akm coefficients are linear in
    -- the parameters) keeps each irrep energy independently tunable.
    Akm = {{2, 0, 1}, {4, 0, 9 / 5}}
    Ea1g_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Akm = {{2, 0, 1}, {4, 0, -12 / 5}}
    Eegsigma_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Akm = {{2, 0, -2}, {4, 0, 3 / 5}}
    Eegpi_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Akm = {{4, -3, -3 * sqrt(7 / 5)}, {4, 3, 3 * sqrt(7 / 5)}}
    Meg_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, Akm)

    Ea1g_4d_i = $Ea1g(4d)_i_value
    Eegsigma_4d_i = $Eegsigma(4d)_i_value
    Eegpi_4d_i = $Eegpi(4d)_i_value
    Meg_4d_i = $Meg(4d)_i_value

    io.write("Initial-state D3d crystal field Hamiltonian in the (a1g, egσ, egπ) basis:\n")
    io.write("=========================================\n")
    io.write("Irrep.            E\n")
    io.write("=========================================\n")
    io.write(string.format("a1g           %8.3f\n", Ea1g_4d_i))
    io.write(string.format("egσ           %8.3f\n", Eegsigma_4d_i))
    io.write(string.format("egπ           %8.3f\n", Eegpi_4d_i))
    io.write("=========================================\n")
    io.write(string.format("The eg-eg off-diagonal element <egσ|H|egπ> is %.3f.\n", Meg_4d_i))
    io.write("\n")

    Ea1g_4d_m = $Ea1g(4d)_m_value
    Eegsigma_4d_m = $Eegsigma(4d)_m_value
    Eegpi_4d_m = $Eegpi(4d)_m_value
    Meg_4d_m = $Meg(4d)_m_value

    Ea1g_4d_f = $Ea1g(4d)_f_value
    Eegsigma_4d_f = $Eegsigma(4d)_f_value
    Eegpi_4d_f = $Eegpi(4d)_f_value
    Meg_4d_f = $Meg(4d)_f_value

    H_i = H_i + Chop(
          Ea1g_4d_i * Ea1g_4d
        + Eegsigma_4d_i * Eegsigma_4d
        + Eegpi_4d_i * Eegpi_4d
        + Meg_4d_i * Meg_4d)

    H_m = H_m + Chop(
          Ea1g_4d_m * Ea1g_4d
        + Eegsigma_4d_m * Eegsigma_4d
        + Eegpi_4d_m * Eegpi_4d
        + Meg_4d_m * Meg_4d)

    H_f = H_f + Chop(
          Ea1g_4d_f * Ea1g_4d
        + Eegsigma_4d_f * Eegsigma_4d
        + Eegpi_4d_f * Eegpi_4d
        + Meg_4d_f * Meg_4d)
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
InitialRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_2p, NElectrons_2p},
                                           {"000000 1111111111", NElectrons_4d, NElectrons_4d}}

IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_2p - 1, NElectrons_2p - 1},
                                                {"000000 1111111111", NElectrons_4d + 1, NElectrons_4d + 1}}

FinalRestrictions = InitialRestrictions

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

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_2p, N_4d, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_4d>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = '=================================================================================================================================\n'

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

Tx_2p_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_2p, IndexDn_2p, {{1, -1, t    }, {1, 1, -t    }})
Ty_2p_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_2p, IndexDn_2p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_2p_4d = NewOperator("CF", NFermions, IndexUp_4d, IndexDn_4d, IndexUp_2p, IndexDn_2p, {{1,  0, 1    }                })

Tx_4d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {{1, -1, t    }, {1, 1, -t    }})
Ty_4d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_4d_2p = NewOperator("CF", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {{1,  0, 1    }                })

T_2p_4d = {CalculateT({Tx_2p_4d, Ty_2p_4d, Tz_2p_4d}, EpsIn, WaveVectorIn)}
T_4d_2p = {CalculateT({Tx_4d_2p, Ty_4d_2p, Tz_4d_2p}, EpsOut, WaveVectorOut)}

if ShiftSpectra then
    Emin1 = Emin1 - (ZeroShift1 + ExperimentalShift1)
    Emax1 = Emax1 - (ZeroShift1 + ExperimentalShift1)
    Emin2 = Emin2 - (ZeroShift2 + ExperimentalShift2)
    Emax2 = Emax2 - (ZeroShift2 + ExperimentalShift2)
end

if CalculationRestrictions == nil then
    G = CreateResonantSpectra(H_m, H_f, T_2p_4d, T_4d_2p, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"DenseBorder", DenseBorder}})
else
    G = CreateResonantSpectra(H_m, H_f, T_2p_4d, T_4d_2p, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"Restrictions1", CalculationRestrictions}, {"Restrictions2", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

-- The Gaussian broadening is done using the same value for the two dimensions.
Gaussian = math.min(Gaussian1, Gaussian2)
G = GetResonantSpectrum(G, dZ_i, #T_2p_4d * #T_4d_2p, #Psis_i, NPoints1)
SaveSpectrum(G, Prefix .. "_k", Gaussian, 0.0)
