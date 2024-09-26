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

Txy_#i_#m   = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_#i_#m   = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{2, -1, t    }, {2, 1, -t    }})
Tyz_#i_#m   = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_#i_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{2, -2, t    }, {2, 2,  t    }})
Tz2_#i_#m   = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_#i, IndexDn_#i, {{2,  0, 1    }                })

Tx_#f_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {{1, -1, t    }, {1, 1, -t    }})
Ty_#f_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_#f_#i = NewOperator("CF", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {{1,  0, 1    }                })

T_#i_#m = {Txy_#i_#m, Txz_#i_#m, Tyz_#i_#m, Tx2y2_#i_#m, Tz2_#i_#m}
T_#f_#i = {Tx_#f_#i, Ty_#f_#i, Tz_#f_#i}

if ShiftSpectra then
    Emin1 = Emin1 - (ZeroShift1 + ExperimentalShift1)
    Emax1 = Emax1 - (ZeroShift1 + ExperimentalShift1)
    Emin2 = Emin2 - (ZeroShift2 + ExperimentalShift2)
    Emax2 = Emax2 - (ZeroShift2 + ExperimentalShift2)
end

if CalculationRestrictions == nil then
    G = CreateResonantSpectra(H_m, H_f, T_#i_#m, T_#f_#i, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"DenseBorder", DenseBorder}})
else
    G = CreateResonantSpectra(H_m, H_f, T_#i_#m, T_#f_#i, Psis_i, {{"Emin1", Emin1}, {"Emax1", Emax1}, {"NE1", NPoints1}, {"Gamma1", Gamma1}, {"Emin2", Emin2}, {"Emax2", Emax2}, {"NE2", NPoints2}, {"Gamma2", Gamma2}, {"Restrictions1", CalculationRestrictions}, {"Restrictions2", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
end

Giso = 0
Shift = 0
for i = 1, #Psis_i do
    for j = 1, #T_#i_#m * #T_#f_#i do
        Indexes = {}
        for k = 1, NPoints1 + 1 do
            table.insert(Indexes, k + Shift)
        end
        Giso = Giso + Spectra.Element(G, Indexes) * dZ_i[i]
        Shift = Shift + NPoints1 + 1
    end
end

-- The Gaussian broadening is done using the same value for the two dimensions.
Gaussian = math.min(Gaussian1, Gaussian2)
if Gaussian ~= 0 then
    Giso.Broaden(Gaussian, 0.0)
end

Giso = -1 / math.pi * Giso
Giso.Print({{"file", Prefix .. "_iso.spec"}})
