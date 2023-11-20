--------------------------------------------------------------------------------
-- Analyze the initial Hamiltonian.
--------------------------------------------------------------------------------
Temperature = Temperature * EnergyUnits.Kelvin.value

Sk = DotProduct(WaveVector, {Sx, Sy, Sz})
Lk = DotProduct(WaveVector, {Lx, Ly, Lz})
Jk = DotProduct(WaveVector, {Jx, Jy, Jz})
Tk = DotProduct(WaveVector, {Tx, Ty, Tz})

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#f, N_#i, N_#f, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#f>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n"

if LmctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#f, N_#i, N_#f, N_L1, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#f>    <N_L1>          dZ\n"
    Header = Header .. "===========================================================================================================================================\n"
    Footer = "===========================================================================================================================================\n"
end

if MlctLigandsHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#f, N_#i, N_#f, N_L2, "dZ"}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#f>    <N_L2>          dZ\n"
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

Txy_#i_#f   = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#i, IndexDn_#i, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_#i_#f   = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#i, IndexDn_#i, {{2, -1, t    }, {2, 1, -t    }})
Tyz_#i_#f   = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#i, IndexDn_#i, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_#i_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#i, IndexDn_#i, {{2, -2, t    }, {2, 2,  t    }})
Tz2_#i_#f   = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#i, IndexDn_#i, {{2,  0, 1    }                })

Er = {t * (Eh[1] - I * Ev[1]),
      t * (Eh[2] - I * Ev[2]),
      t * (Eh[3] - I * Ev[3])}

El = {-t * (Eh[1] + I * Ev[1]),
      -t * (Eh[2] + I * Ev[2]),
      -t * (Eh[3] + I * Ev[3])}

local T = {Txy_#i_#f, Txz_#i_#f, Tyz_#i_#f, Tx2y2_#i_#f, Tz2_#i_#f}
Tv_#i_#f = CalculateT(T, Ev, WaveVector)
Th_#i_#f = CalculateT(T, Eh, WaveVector)
Tr_#i_#f = CalculateT(T, Er, WaveVector)
Tl_#i_#f = CalculateT(T, El, WaveVector)
Tk_#i_#f = CalculateT(T, WaveVector, WaveVector)

-- Initialize a table with the available spectra and the required operators.
SpectraAndOperators = {
    ["Isotropic Absorption"] = {Txy_#i_#f, Txz_#i_#f, Tyz_#i_#f, Tx2y2_#i_#f, Tz2_#i_#f},
    ["Absorption"] = {Tk_#i_#f,},
    ["Circular Dichroic"] = {Tr_#i_#f, Tl_#i_#f},
    ["Linear Dichroic"] = {Tv_#i_#f, Th_#i_#f},
}

-- Create an unordered set with the required operators.
local T_#i_#f = {}
for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        for _, Operator in pairs(Operators) do
            T_#i_#f[Operator] = true
        end
    end
end

-- Give the operators table the form required by Quanty's functions.
local T = {}
for Operator, _ in pairs(T_#i_#f) do
    table.insert(T, Operator)
end
T_#i_#f = T

Emin = Emin - (ZeroShift + ExperimentalShift)
Emax = Emax - (ZeroShift + ExperimentalShift)

if CalculationRestrictions == nil then
    G_#i_#f = CreateSpectra(H_f, T_#i_#f, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"DenseBorder", DenseBorder}})
else
    G_#i_#f = CreateSpectra(H_f, T_#i_#f, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

if ShiftSpectra then
    G_#i_#f.Shift(ZeroShift + ExperimentalShift)
end

-- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
local dZ_#i_#f = {}
for _ in ipairs(T_#i_#f) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_#i_#f, dZ_i[j])
    end
end

local Ids = {}
for k, v in pairs(T_#i_#f) do
    Ids[v] = k
end

-- Subtract the broadening used in the spectra calculations from the Lorentzian table.
for i, _ in ipairs(Lorentzian) do
    -- The FWHM is the second value in each pair.
    Lorentzian[i][2] = Lorentzian[i][2] - Gamma
end

Pcl_#i_#f = 1

for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        -- Find the indices of the spectrum's operators in the table used during the
        -- calculation (this is unsorted).
        SpectrumIds = {}
        for _, Operator in pairs(Operators) do
            table.insert(SpectrumIds, Ids[Operator])
        end

        if Spectrum == "Isotropic Absorption" then
            Giso = GetSpectrum(G_#i_#f, SpectrumIds, dZ_#i_#f, #T_#i_#f, #Psis_i)
            Giso = Giso / 15
            SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, Lorentzian, Pcl_#i_#f)
        end

        if Spectrum == "Absorption" then
            Gk = GetSpectrum(G_#i_#f, SpectrumIds, dZ_#i_#f, #T_#i_#f, #Psis_i)
            SaveSpectrum(Gk, Prefix .. "_k", Gaussian, Lorentzian, Pcl_#i_#f)
        end

        if Spectrum == "Circular Dichroic" then
            Gr = GetSpectrum(G_#i_#f, SpectrumIds[1], dZ_#i_#f, #T_#i_#f, #Psis_i)
            Gl = GetSpectrum(G_#i_#f, SpectrumIds[2], dZ_#i_#f, #T_#i_#f, #Psis_i)
            SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian, Pcl_#i_#f)
            SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian, Pcl_#i_#f)
            SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
        end

        if Spectrum == "Linear Dichroic" then
            Gv = GetSpectrum(G_#i_#f, SpectrumIds[1], dZ_#i_#f, #T_#i_#f, #Psis_i)
            Gh = GetSpectrum(G_#i_#f, SpectrumIds[2], dZ_#i_#f, #T_#i_#f, #Psis_i)
            SaveSpectrum(Gv, Prefix .. "_v", Gaussian, Lorentzian, Pcl_#i_#f)
            SaveSpectrum(Gh, Prefix .. "_h", Gaussian, Lorentzian, Pcl_#i_#f)
            SaveSpectrum(Gv - Gh, Prefix .. "_ld", Gaussian, Lorentzian)
        end
    end
end
