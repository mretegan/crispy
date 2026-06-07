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
