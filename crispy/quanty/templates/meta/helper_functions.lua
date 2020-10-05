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

function SaveSpectrum(G, Filename, Gaussian, Lorentzian, Pcl)
    if Pcl == nil then
        Pcl = 1
    end
    G = -1 / math.pi / Pcl * G
    G.Broaden(Gaussian, Lorentzian)
    G.Print({{"file", Filename .. ".spec"}})
end

function CalculateT(Operators, Vec1, Vec2)
    -- Calculate the transition operator for an arbitrary orientation.
    --
    -- @param: Operators: table of operators used as basis.
    -- @param: Vec1: first cartesian 3D vector
    -- @param: Vec2: second cartesian 3D vector

    if #Operators == 3 then
        -- Dipolar operators in the order x, y, z.
        T = Vec1[1] * Operators[1]
          + Vec1[2] * Operators[2]
          + Vec1[3] * Operators[3]
    elseif #Operators == 5 then 
        -- Quadrupolar operators in the order xy, xz, yz, x2y2, z2.
        T = (Vec1[1] * Vec2[2] + Vec1[2] * Vec2[1]) * Operators[1] / math.sqrt(3)
          + (Vec1[1] * Vec2[3] + Vec1[3] * Vec2[1]) * Operators[2] / math.sqrt(3)
          + (Vec1[2] * Vec2[3] + Vec1[3] * Vec2[2]) * Operators[3] / math.sqrt(3)
          + (Vec1[1] * Vec2[1] - Vec1[2] * Vec2[2]) * Operators[4] / math.sqrt(3)
          + Vec1[3] * Vec2[3] * Operators[5]
    end
    return Chop(T)
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
