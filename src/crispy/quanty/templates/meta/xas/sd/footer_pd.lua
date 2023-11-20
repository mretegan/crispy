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

if PdHybridizationTerm then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_#f, N_#i, N_#f, N_4p, "dZ"}
    Header = "Analysis of the initial Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_#i>    <N_#f>    <N_4p>          dZ\n"
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
    SpectraAndOperators_#i_#f = {
        ["Isotropic Absorption"] = {Txy_#i_#f, Txz_#i_#f, Tyz_#i_#f, Tx2y2_#i_#f, Tz2_#i_#f},
        ["Absorption"] = {Tk_#i_#f,},
        ["Circular Dichroic"] = {Tr_#i_#f, Tl_#i_#f},
        ["Linear Dichroic"] = {Tv_#i_#f, Th_#i_#f},
    }

    -- Create an unordered set with the required operators.
    local T_#i_#f = {}
    for Spectrum, Operators in pairs(SpectraAndOperators_#i_#f) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            for _, Operator in pairs(Operators) do
                T_#i_#f[Operator] = true
            end
        end
    end

    -- Give the operators table the form required by Quanty's functions.
    local T1 = {}
    for Operator, _ in pairs(T_#i_#f) do
        table.insert(T1, Operator)
    end
    T_#i_#f = T1

    -- Dipolar operators.
    Tx_#i_4p = NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#i, IndexDn_#i, {{1, -1, t    }, {1, 1, -t    }})
    Ty_#i_4p = NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#i, IndexDn_#i, {{1, -1, t * I}, {1, 1,  t * I}})
    Tz_#i_4p = NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#i, IndexDn_#i, {{1,  0, 1    }                })

    local T = {Tx_#i_4p, Ty_#i_4p, Tz_#i_4p}
    Tv_#i_4p = CalculateT(T, Ev)
    Th_#i_4p = CalculateT(T, Eh)
    Tr_#i_4p = CalculateT(T, Er)
    Tl_#i_4p = CalculateT(T, El)
    Tk_#i_4p = CalculateT(T, WaveVector)

    -- Initialize a table with the available spectra and the required operators.
    SpectraAndOperators_#i_4p = {
        ["Isotropic Absorption"] = {Tk_#i_4p, Tr_#i_4p, Tl_#i_4p},
        ["Absorption"] = {Tk_#i_4p,},
        ["Circular Dichroic"] = {Tr_#i_4p, Tl_#i_4p},
        ["Linear Dichroic"] = {Tv_#i_4p, Th_#i_4p},
    }

    -- Create an unordered set with the required operators.
    local T_#i_4p = {}
    for Spectrum, Operators in pairs(SpectraAndOperators_#i_4p) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            for _, Operator in pairs(Operators) do
                T_#i_4p[Operator] = true
            end
        end
    end

    -- Give the operators table the form required by Quanty's functions.
    local T2 = {}
    for Operator, _ in pairs(T_#i_4p) do
        table.insert(T2, Operator)
    end
    T_#i_4p = T2

    Emin = Emin - (ZeroShift + ExperimentalShift)
    Emax = Emax - (ZeroShift + ExperimentalShift)

    -- Calculate the spectra. Note that the CalculationRestrictions are active in this case.
    G_#i_#f = CreateSpectra(H_f, T_#i_#f, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})
    G_#i_4p = CreateSpectra(H_f, T_#i_4p, Psis_i, {{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}})

    -- The prefactors are described in http://dx.doi.org/10.1103/PhysRevB.94.245115.
    --
    -- prefactor_#i_#f = 4 * math.pi^2 * alpha * a0^4 / (2 * hbar * c)^2 * ExperimentalShift   * P2_#i_#f^2
    -- prefactor_#i_4p = 4 * math.pi^2 * alpha * a0^2                    * ExperimentalShift^3 * P1_#i_4p^2
    --
    -- Here we set the prefactor for the quadrupolar spectrum to 1, to more
    -- easily compare the spectra with and without hybridization. Note however
    -- that the quadrupole spectrum without hybridization can look quite
    -- different from the quadrupolar part of the spectrum with hybridization.
    -- They are identical only if all parameters of the #f-4p interaction are zero.
    --
    -- The dipolar prefactor then becomes:
    --
    -- prefactor_#i_4p = (2 * hbar * c)^2 / (a0 * ExperimentalShift)^2 * (P1_#i_4p / P2_#i_#f)^2

    alpha = 7.2973525664E-3
    a0 = 5.2917721067E-1
    hbar = 6.582119514E-16
    c = 2.99792458E+18

    P1_#i_4p = $P1(#i,4p)
    P2_#i_#f = $P2(#i,#f)

    prefactor_#i_#f = 1
    prefactor_#i_4p = (2 * hbar * c)^2 / (a0 * ExperimentalShift)^2 * (P1_#i_4p / P2_#i_#f)^2

    io.write("\n")
    io.write("Spectra prefactors\n")
    io.write("==================\n")
    io.write(string.format("Dipolar     = %.1f\n", prefactor_#i_4p))
    io.write("Quadrupolar =  1.0\n")
    io.write("==================\n")

    G_#i_#f = prefactor_#i_#f * G_#i_#f
    G_#i_4p = prefactor_#i_4p * G_#i_4p

    if ShiftSpectra then
        G_#i_#f.Shift(ZeroShift + ExperimentalShift)
        G_#i_4p.Shift(ZeroShift + ExperimentalShift)
    end

    -- Subtract the broadening used in the spectra calculations from the Lorentzian table.
    for i, _ in ipairs(Lorentzian) do
        -- The FWHM is the second value in each pair.
        Lorentzian[i][2] = Lorentzian[i][2] - Gamma
    end

    -- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
    local dZ_#i_#f = {}
    for _ in ipairs(T_#i_#f) do
        for j in ipairs(Psis_i) do
            table.insert(dZ_#i_#f, dZ_i[j])
        end
    end

    local Ids_#i_#f = {}
    for k, v in pairs(T_#i_#f) do
        Ids_#i_#f[v] = k
    end

    for Spectrum, Operators in pairs(SpectraAndOperators_#i_#f) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            -- Find the indices of the spectrum's operators in the table used during the
            -- calculation (this is unsorted).
            SpectrumIds_#i_#f = {}
            for _, Operator in pairs(Operators) do
                table.insert(SpectrumIds_#i_#f, Ids_#i_#f[Operator])
            end

            if Spectrum == "Isotropic Absorption" then
                Giso_#i_#f = GetSpectrum(G_#i_#f, SpectrumIds_#i_#f, dZ_#i_#f, #T_#i_#f, #Psis_i)
            end

            if Spectrum == "Absorption" then
                Gk_#i_#f = GetSpectrum(G_#i_#f, SpectrumIds_#i_#f, dZ_#i_#f, #T_#i_#f, #Psis_i)
            end

            if Spectrum == "Circular Dichroic" then
                Gr_#i_#f = GetSpectrum(G_#i_#f, SpectrumIds_#i_#f[1], dZ_#i_#f, #T_#i_#f, #Psis_i)
                Gl_#i_#f = GetSpectrum(G_#i_#f, SpectrumIds_#i_#f[2], dZ_#i_#f, #T_#i_#f, #Psis_i)
            end

            if Spectrum == "Linear Dichroic" then
                Gv_#i_#f = GetSpectrum(G_#i_#f, SpectrumIds_#i_#f[1], dZ_#i_#f, #T_#i_#f, #Psis_i)
                Gh_#i_#f = GetSpectrum(G_#i_#f, SpectrumIds_#i_#f[2], dZ_#i_#f, #T_#i_#f, #Psis_i)
            end
        end
    end

    local dZ_#i_4p = {}
    for _ in ipairs(T_#i_4p) do
        for j in ipairs(Psis_i) do
            table.insert(dZ_#i_4p, dZ_i[j])
        end
    end

    -- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
    local Ids_#i_4p = {}
    for k, v in pairs(T_#i_4p) do
        Ids_#i_4p[v] = k
    end

    for Spectrum, Operators in pairs(SpectraAndOperators_#i_4p) do
        if ValueInTable(Spectrum, SpectraToCalculate) then
            -- Find the indices of the spectrum's operators in the table used during the
            -- calculation (this is unsorted).
            SpectrumIds_#i_4p = {}
            for _, Operator in pairs(Operators) do
                table.insert(SpectrumIds_#i_4p, Ids_#i_4p[Operator])
            end

            if Spectrum == "Isotropic Absorption" then
                Giso_#i_4p = GetSpectrum(G_#i_4p, SpectrumIds_#i_4p, dZ_#i_4p, #T_#i_4p, #Psis_i)
                Giso_#i_#f = Giso_#i_#f / 15
                Giso_#i_4p = Giso_#i_4p / 3
                Giso = Giso_#i_#f + Giso_#i_4p
                SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, Lorentzian)
                SaveSpectrum(Giso_#i_4p, Prefix .. "_iso_dip", Gaussian, Lorentzian)
                SaveSpectrum(Giso_#i_#f, Prefix .. "_iso_quad", Gaussian, Lorentzian)
            end

            if Spectrum == "Absorption" then
                Gk_#i_4p = GetSpectrum(G_#i_4p, SpectrumIds_#i_4p, dZ_#i_4p, #T_#i_4p, #Psis_i)
                Gk = Gk_#i_#f + Gk_#i_4p
                SaveSpectrum(Gk, Prefix .. "_k", Gaussian, Lorentzian)
                SaveSpectrum(Gk_#i_4p, Prefix .. "_k_dip", Gaussian, Lorentzian)
                SaveSpectrum(Gk_#i_#f, Prefix .. "_k_quad", Gaussian, Lorentzian)
            end

            if Spectrum == "Circular Dichroic" then
                Gr_#i_4p = GetSpectrum(G_#i_4p, SpectrumIds_#i_4p[1], dZ_#i_4p, #T_#i_4p, #Psis_i)
                Gl_#i_4p = GetSpectrum(G_#i_4p, SpectrumIds_#i_4p[2], dZ_#i_4p, #T_#i_4p, #Psis_i)
                Gr = Gr_#i_#f + Gr_#i_4p
                Gl = Gl_#i_#f + Gl_#i_4p
                SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian)
                SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian)
                SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
                SaveSpectrum(Gr_#i_4p - Gl_#i_4p, Prefix .. "_cd_dip", Gaussian, Lorentzian)
                SaveSpectrum(Gr_#i_#f - Gl_#i_#f, Prefix .. "_cd_quad", Gaussian, Lorentzian)
            end

            if Spectrum == "Linear Dichroic" then
                Gv_#i_4p = GetSpectrum(G_#i_4p, SpectrumIds_#i_4p[1], dZ_#i_4p, #T_#i_4p, #Psis_i)
                Gh_#i_4p = GetSpectrum(G_#i_4p, SpectrumIds_#i_4p[2], dZ_#i_4p, #T_#i_4p, #Psis_i)
                Gv = Gv_#i_#f + Gv_#i_4p
                Gh = Gh_#i_#f + Gh_#i_4p
                SaveSpectrum(Gv, Prefix .. "_v", Gaussian, Lorentzian)
                SaveSpectrum(Gh, Prefix .. "_h", Gaussian, Lorentzian)
                SaveSpectrum(Gv - Gh, Prefix .. "_ld", Gaussian, Lorentzian)
                SaveSpectrum(Gv_#i_4p - Gh_#i_4p, Prefix .. "_ld_dip", Gaussian, Lorentzian)
                SaveSpectrum(Gv_#i_#f - Gh_#i_#f, Prefix .. "_ld_quad", Gaussian, Lorentzian)
            end
        end
    end
else
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
end
