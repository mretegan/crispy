--------------------------------------------------------------------------------
-- Analyze the initial Hamiltonian.
--------------------------------------------------------------------------------
Temperature = Temperature * EnergyUnits.Kelvin.value

Sk = DotProduct(WaveVector, {Sx, Sy, Sz})
Lk = DotProduct(WaveVector, {Lx, Ly, Lz})
Jk = DotProduct(WaveVector, {Jx, Jy, Jz})
Tk = DotProduct(WaveVector, {Tx, Ty, Tz})

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#m, N_#i, N_#m, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#m>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n"

if LmctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#m, N_#i, N_#m, N_L1, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#m>    <N_L1>          dZ\n"
    Header = Header .. "===========================================================================================================================================\n"
    Footer = "===========================================================================================================================================\n"
end

if MlctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#m, N_#i, N_#m, N_L2, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#m>    <N_L2>          dZ\n"
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

-- Operators that annihilate a #i electron to create the core-hole state.
Tu_#i = NewOperator("An", NFermions, IndexUp_#i[1])
Td_#i = NewOperator("An", NFermions, IndexDn_#i[1])
T_#i = {Tu_#i, Td_#i}

-- Emission dipole operators for the radiative #f to #i decay.
Tx_#f_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {{1, -1, t}, {1, 1, -t}})
Ty_#f_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {{1, -1, t * I}, {1, 1, t * I}})
Tz_#f_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {{1, 0, 1}})

-- Right- and left-circular emission polarizations, perpendicular to the emission wave
-- vector.
Epsh = Eps
Epsv = {WaveVector[2] * Epsh[3] - WaveVector[3] * Epsh[2],
        WaveVector[3] * Epsh[1] - WaveVector[1] * Epsh[3],
        WaveVector[1] * Epsh[2] - WaveVector[2] * Epsh[1]}
Epsr = {t * (Epsh[1] - I * Epsv[1]),
        t * (Epsh[2] - I * Epsv[2]),
        t * (Epsh[3] - I * Epsv[3])}
Epsl = {-t * (Epsh[1] + I * Epsv[1]),
        -t * (Epsh[2] + I * Epsv[2]),
        -t * (Epsh[3] + I * Epsv[3])}

local TCartesian = {Tx_#f_#i, Ty_#f_#i, Tz_#f_#i}
Tr_#f_#i = CalculateT(TCartesian, Epsr)
Tl_#f_#i = CalculateT(TCartesian, Epsl)

-- Available spectra and the operators required to calculate them.
SpectraAndOperators = {
    ["Emission"] = {Tx_#f_#i, Ty_#f_#i, Tz_#f_#i},
    ["Circular Dichroic"] = {Tr_#f_#i, Tl_#f_#i},
}

-- Create an unordered set with the required operators.
local T_#f_#i = {}
for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        for _, Operator in pairs(Operators) do
            T_#f_#i[Operator] = true
        end
    end
end

-- Give the operators table the form required by Quanty's functions.
local T = {}
for Operator, _ in pairs(T_#f_#i) do
    table.insert(T, Operator)
end
T_#f_#i = T

-- Create the core-hole states by annihilating a #i electron from each initial state and
-- relax them to the ground state of the intermediate Hamiltonian. We assume the core-hole
-- state has time to fully relax before it decays.
local Psis_m = {}
local dZ_m = {}
for i = 1, #Psis_i do
    for _, Op in ipairs(T_#i) do
        local Psi = Op * Psis_i[i]
        Eigensystem(H_m, Psi)
        table.insert(Psis_m, Psi)
        table.insert(dZ_m, dZ_i[i])
    end
end

if ShiftSpectra then
    -- Pin the main line to ExperimentalShift: subtract the core-hole -> final-ground
    -- transition energy (the high-energy edge of the spectrum, since H is negated).
    Psis_f, _ = WavefunctionsAndBoltzmannFactors(H_f, 1, false, 0, nil, FinalRestrictions, nil)
    ZeroShift = Psis_f[1] * H_f * Psis_f[1] - Psis_m[1] * H_f * Psis_m[1]
    Emin = Emin - (ZeroShift + ExperimentalShift)
    Emax = Emax - (ZeroShift + ExperimentalShift)
end

-- Negate H for the emission-energy axis.
if CalculationRestrictions == nil then
    G_#f_#i = CreateSpectra(-H_f, T_#f_#i, Psis_m, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"DenseBorder", DenseBorder}})
else
    G_#f_#i = CreateSpectra(-H_f, T_#f_#i, Psis_m, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

if ShiftSpectra then
    G_#f_#i.Shift(ZeroShift + ExperimentalShift)
end

-- Create a list with the Boltzmann probabilities, one for each operator-state spectrum.
local dZ_#f_#i = {}
for _ in ipairs(T_#f_#i) do
    for j in ipairs(Psis_m) do
        table.insert(dZ_#f_#i, dZ_m[j])
    end
end

-- Map each operator to its index in the (unordered) operators table.
local Ids = {}
for k, v in pairs(T_#f_#i) do
    Ids[v] = k
end

-- Subtract the broadening used in the spectra calculations from the Lorentzian table.
for i, _ in ipairs(Lorentzian) do
    -- The FWHM is the second value in each pair.
    Lorentzian[i][2] = Lorentzian[i][2] - Gamma
end

for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        SpectrumIds = {}
        for _, Operator in pairs(Operators) do
            table.insert(SpectrumIds, Ids[Operator])
        end

        if Spectrum == "Emission" then
            -- Single-crystal emission summed over the emission polarizations; no isotropic
            -- or powder averaging is performed.
            Gemi = GetSpectrum(G_#f_#i, SpectrumIds, dZ_#f_#i, #T_#f_#i, #Psis_m)
            SaveSpectrum(Gemi, Prefix .. "_emi", Gaussian, Lorentzian)
        end

        if Spectrum == "Circular Dichroic" then
            Gr = GetSpectrum(G_#f_#i, SpectrumIds[1], dZ_#f_#i, #T_#f_#i, #Psis_m)
            Gl = GetSpectrum(G_#f_#i, SpectrumIds[2], dZ_#f_#i, #T_#f_#i, #Psis_m)
            SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian)
            SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian)
            SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
        end
    end
end
