--------------------------------------------------------------------------------
-- Analyze the initial Hamiltonian.
--------------------------------------------------------------------------------
Temperature = Temperature * EnergyUnits.Kelvin.value

Sk = DotProduct(WaveVectorIn, {Sx, Sy, Sz})
Lk = DotProduct(WaveVectorIn, {Lx, Ly, Lz})
Jk = DotProduct(WaveVectorIn, {Jx, Jy, Jz})
Tk = DotProduct(WaveVectorIn, {Tx, Ty, Tz})

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#m, N_#i, N_#m, "dZ"}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#m>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = '=================================================================================================================================\n'

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

Tx_#i_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{1, -1, t    }, {1, 1, -t    }})
Ty_#i_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_#i_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{1,  0, 1    }                })

Tx_#m_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#m, IndexDn_#m, {{1, -1, t    }, {1, 1, -t    }})
Ty_#m_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#m, IndexDn_#m, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_#m_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#m, IndexDn_#m, {{1,  0, 1    }                })

if ShiftSpectra then
    Emin1 = Emin1 - (ZeroShift1 + ExperimentalShift1)
    Emax1 = Emax1 - (ZeroShift1 + ExperimentalShift1)
    Emin2 = Emin2 - (ZeroShift2 + ExperimentalShift2)
    Emax2 = Emax2 - (ZeroShift2 + ExperimentalShift2)
end

-- The Gaussian broadening is done using the same value for the two dimensions.
Gaussian = math.min(Gaussian1, Gaussian2)

-- Single-crystal resonant inelastic scattering for the chosen incident and
-- scattered polarizations.
if ValueInTable("Resonant Inelastic", SpectraToCalculate) then
    T_#i_#m = {CalculateT({Tx_#i_#m, Ty_#i_#m, Tz_#i_#m}, EpsIn, WaveVectorIn)}
    T_#m_#i = {CalculateT({Tx_#m_#i, Ty_#m_#i, Tz_#m_#i}, EpsOut, WaveVectorOut)}

    if CalculationRestrictions == nil then
        G = CreateResonantSpectra(H_m, H_f, T_#i_#m, T_#m_#i, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"DenseBorder", DenseBorder}})
    else
        G = CreateResonantSpectra(H_m, H_f, T_#i_#m, T_#m_#i, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"Restrictions1", CalculationRestrictions}, {"Restrictions2", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
    end

    G = GetResonantSpectrum(G, dZ_i, #T_#i_#m * #T_#m_#i, #Psis_i, NPoints1)
    SaveSpectrum(G, Prefix .. "_k", Gaussian, 0.0)
end

-- Powder-averaged (isotropic) resonant inelastic scattering. The two fundamental
-- spectra A and B are obtained from the full 9 x 9 polarization grid (the
-- four-measurement scheme) and combined with a geometry factor that depends only
-- on the incident and scattered polarizations. Valid for dipole-in/dipole-out
-- edges only.
if ValueInTable("Isotropic Resonant Inelastic", SpectraToCalculate) then
    T_#i_#m = {Tx_#i_#m, Ty_#i_#m, Tz_#i_#m,
               (Tx_#i_#m + Ty_#i_#m) * t, (Tx_#i_#m + Tz_#i_#m) * t, (Ty_#i_#m + Tz_#i_#m) * t,
               (Tx_#i_#m - Ty_#i_#m) * t, (Tx_#i_#m - Tz_#i_#m) * t, (Ty_#i_#m - Tz_#i_#m) * t}
    T_#m_#i = {Tx_#m_#i, Ty_#m_#i, Tz_#m_#i,
               (Tx_#m_#i + Ty_#m_#i) * t, (Tx_#m_#i + Tz_#m_#i) * t, (Ty_#m_#i + Tz_#m_#i) * t,
               (Tx_#m_#i - Ty_#m_#i) * t, (Tx_#m_#i - Tz_#m_#i) * t, (Ty_#m_#i - Tz_#m_#i) * t}

    if CalculationRestrictions == nil then
        G = CreateResonantSpectra(H_m, H_f, T_#i_#m, T_#m_#i, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"DenseBorder", DenseBorder}})
    else
        G = CreateResonantSpectra(H_m, H_f, T_#i_#m, T_#m_#i, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"Restrictions1", CalculationRestrictions}, {"Restrictions2", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
    end

    local A, B = GetFundamentalSpectra(G, dZ_i, #Psis_i, NPoints1)

    -- Combine the fundamental spectra with a geometry factor. When the outgoing
    -- polarization is analyzed it is the squared projection of the incident onto
    -- the scattered polarization; otherwise it is averaged over the (unresolved)
    -- outgoing polarization.
    local GeometryFactor
    if $YAnalyzePolarization then
        GeometryFactor = DotProduct(EpsIn, EpsOut)^2
    else
        GeometryFactor = 0.5 * (1 - DotProduct(EpsIn, WaveVectorOut)^2)
    end
    local Giso = A + B * GeometryFactor

    SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, 0.0)
end
