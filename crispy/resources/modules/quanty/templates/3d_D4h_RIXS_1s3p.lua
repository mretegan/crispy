--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 3d transition metals
-- symmetry: D4h
-- experiment: RIXS
-- edge: K-M2,3 (1s3p)
--------------------------------------------------------------------------------
Verbosity($verbosity)

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_m = 0
H_f = 0

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
H_atomic = $H_atomic
H_cf     = $H_cf

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 18

NElectrons_1s = 2
NElectrons_3p = 6
NElectrons_3d = $NElectrons_3d

IndexDn_1s = {0}
IndexUp_1s = {1}
IndexDn_3p = {2, 4, 6}
IndexUp_3p = {3, 5, 7}
IndexDn_3d = {8, 10, 12, 14, 16}
IndexUp_3d = {9, 11, 13, 15, 17}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_1s = NewOperator('Number', NFermions, IndexUp_1s, IndexUp_1s, {1})
     + NewOperator('Number', NFermions, IndexDn_1s, IndexDn_1s, {1})

N_3p = NewOperator('Number', NFermions, IndexUp_3p, IndexUp_3p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3p, IndexDn_3p, {1, 1, 1})

N_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
    F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
    F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

    F0_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
    F2_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
    G1_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
    G3_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

    F0_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {1}, {0})
    G2_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {0}, {1})

    U_3d_3d_i  = $U(3d,3d)_i_value * $U(3d,3d)_i_scaling
    F2_3d_3d_i = $F2(3d,3d)_i_value * $F2(3d,3d)_i_scaling
    F4_3d_3d_i = $F4(3d,3d)_i_value * $F4(3d,3d)_i_scaling
    F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

    U_3d_3d_m  = $U(3d,3d)_m_value * $U(3d,3d)_m_scaling
    F2_3d_3d_m = $F2(3d,3d)_m_value * $F2(3d,3d)_m_scaling
    F4_3d_3d_m = $F4(3d,3d)_m_value * $F4(3d,3d)_m_scaling
    F0_3d_3d_m = U_3d_3d_m + 2 / 63 * F2_3d_3d_m + 2 / 63 * F4_3d_3d_m
    U_1s_3d_m  = $U(1s,3d)_m_value * $U(1s,3d)_m_scaling
    G2_1s_3d_m = $G2(1s,3d)_m_value * $G2(1s,3d)_m_scaling
    F0_1s_3d_m = U_1s_3d_m + 1 / 10 * G2_1s_3d_m

    U_3d_3d_f  = $U(3d,3d)_f_value * $U(3d,3d)_f_scaling
    F2_3d_3d_f = $F2(3d,3d)_f_value * $F2(3d,3d)_f_scaling
    F4_3d_3d_f = $F4(3d,3d)_f_value * $F4(3d,3d)_f_scaling
    F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
    U_3p_3d_f  = $U(3p,3d)_f_value * $U(3p,3d)_f_scaling
    F2_3p_3d_f = $F2(3p,3d)_f_value * $F2(3p,3d)_f_scaling
    G1_3p_3d_f = $G1(3p,3d)_f_value * $G1(3p,3d)_f_scaling
    G3_3p_3d_f = $G3(3p,3d)_f_value * $G3(3p,3d)_f_scaling
    F0_3p_3d_f = U_3p_3d_f + 1 / 15 * G1_3p_3d_f + 3 / 70 * G3_3p_3d_f

    H_i = H_i
        + F0_3d_3d_i * F0_3d_3d
        + F2_3d_3d_i * F2_3d_3d
        + F4_3d_3d_i * F4_3d_3d

    H_m = H_m
        + F0_3d_3d_m * F0_3d_3d
        + F2_3d_3d_m * F2_3d_3d
        + F4_3d_3d_m * F4_3d_3d
        + F0_1s_3d_m * F0_1s_3d
        + G2_1s_3d_m * G2_1s_3d

    H_f = H_f
        + F0_3d_3d_f * F0_3d_3d
        + F2_3d_3d_f * F2_3d_3d
        + F4_3d_3d_f * F4_3d_3d
        + F0_3p_3d_f * F0_3p_3d
        + F2_3p_3d_f * F2_3p_3d
        + G1_3p_3d_f * G1_3p_3d
        + G3_3p_3d_f * G3_3p_3d

    ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

    ldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

    zeta_3d_i = $zeta(3d)_i_value * $zeta(3d)_i_scaling

    zeta_3d_m = $zeta(3d)_m_value * $zeta(3d)_m_scaling

    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scaling
    zeta_3p_f = $zeta(3p)_f_value * $zeta(3p)_f_scaling

    H_i = H_i
        + zeta_3d_i * ldots_3d

    H_m = H_m
        + zeta_3d_m * ldots_3d

    H_f = H_f
        + zeta_3d_f * ldots_3d
        + zeta_3p_f * ldots_3p
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('D4h', 2, {Ea1g, Eb1g, Eb2g, Eeg})
    Dq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, { 6,  6, -4, -4}))
    Ds_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-2,  2,  2, -1}))
    Dt_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-6, -1, -1,  4}))

    Dq_3d_i = $Dq(3d)_i_value
    Ds_3d_i = $Ds(3d)_i_value
    Dt_3d_i = $Dt(3d)_i_value

    Dq_3d_m = $Dq(3d)_m_value
    Ds_3d_m = $Ds(3d)_m_value
    Dt_3d_m = $Dt(3d)_m_value

    Dq_3d_f = $Dq(3d)_f_value
    Ds_3d_f = $Ds(3d)_f_value
    Dt_3d_f = $Dt(3d)_f_value

    H_i = H_i
        + Dq_3d_i * Dq_3d
        + Ds_3d_i * Ds_3d
        + Dt_3d_i * Dt_3d

    H_m = H_m
        + Dq_3d_m * Dq_3d
        + Ds_3d_m * Ds_3d
        + Dt_3d_m * Dt_3d

    H_f = H_f
        + Dq_3d_f * Dq_3d
        + Ds_3d_f * Ds_3d
        + Dt_3d_f * Dt_3d
end

--------------------------------------------------------------------------------
-- Define the spin and orbital operators.
--------------------------------------------------------------------------------
Sx_3d    = NewOperator('Sx'   , NFermions, IndexUp_3d, IndexDn_3d)
Sy_3d    = NewOperator('Sy'   , NFermions, IndexUp_3d, IndexDn_3d)
Sz_3d    = NewOperator('Sz'   , NFermions, IndexUp_3d, IndexDn_3d)
Ssqr_3d  = NewOperator('Ssqr' , NFermions, IndexUp_3d, IndexDn_3d)
Splus_3d = NewOperator('Splus', NFermions, IndexUp_3d, IndexDn_3d)
Smin_3d  = NewOperator('Smin' , NFermions, IndexUp_3d, IndexDn_3d)

Lx_3d    = NewOperator('Lx'   , NFermions, IndexUp_3d, IndexDn_3d)
Ly_3d    = NewOperator('Ly'   , NFermions, IndexUp_3d, IndexDn_3d)
Lz_3d    = NewOperator('Lz'   , NFermions, IndexUp_3d, IndexDn_3d)
Lsqr_3d  = NewOperator('Lsqr' , NFermions, IndexUp_3d, IndexDn_3d)
Lplus_3d = NewOperator('Lplus', NFermions, IndexUp_3d, IndexDn_3d)
Lmin_3d  = NewOperator('Lmin' , NFermions, IndexUp_3d, IndexDn_3d)

Jx_3d    = NewOperator('Jx'   , NFermions, IndexUp_3d, IndexDn_3d)
Jy_3d    = NewOperator('Jy'   , NFermions, IndexUp_3d, IndexDn_3d)
Jz_3d    = NewOperator('Jz'   , NFermions, IndexUp_3d, IndexDn_3d)
Jsqr_3d  = NewOperator('Jsqr' , NFermions, IndexUp_3d, IndexDn_3d)
Jplus_3d = NewOperator('Jplus', NFermions, IndexUp_3d, IndexDn_3d)
Jmin_3d  = NewOperator('Jmin' , NFermions, IndexUp_3d, IndexDn_3d)

Sx = Sx_3d
Sy = Sy_3d
Sz = Sz_3d

Lx = Lx_3d
Ly = Ly_3d
Lz = Lz_3d

Jx = Jx_3d
Jy = Jy_3d
Jz = Jz_3d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'11 000000 0000000000', NElectrons_1s, NElectrons_1s},
                                           {'00 111111 0000000000', NElectrons_3p, NElectrons_3p},
                                           {'00 000000 1111111111', NElectrons_3d, NElectrons_3d}}

IntermediateRestrictions = {NFermions, NBosons, {'11 000000 0000000000', NElectrons_1s - 1, NElectrons_1s - 1},
                                                {'00 111111 0000000000', NElectrons_3p, NElectrons_3p},
                                                {'00 000000 1111111111', NElectrons_3d + 1, NElectrons_3d + 1}}

FinalRestrictions = {NFermions, NBosons, {'11 000000 0000000000', NElectrons_1s, NElectrons_1s},
                                         {'00 111111 0000000000', NElectrons_3p - 1, NElectrons_3p - 1},
                                         {'00 000000 1111111111', NElectrons_3d + 1, NElectrons_3d + 1}}

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_1s, N_3d}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_1s>    <N_3d>\n'
header = header .. '==============================================================================================\n'
footer = '==============================================================================================\n'

-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

 -- Approximate machine epsilon.
epsilon = 2.22e-16
Z = 0

NPsis = $NPsis
NPsisAuto = $NPsisAuto

if NPsisAuto == 1 and NPsis ~= 1 then
    NPsis = 1
    NPsisIncrement = 8
    NPsisIsConverged = false
    dZ = {}

    while not NPsisIsConverged do
        if CalculationRestrictions == nil then
            Psis_i = Eigensystem(H_i, InitialRestrictions, NPsis)
        else
            Psis_i = Eigensystem(H_i, InitialRestrictions, NPsis, {{'restrictions', CalculationRestrictions}})
        end

        if not (type(Psis_i) == 'table') then
            Psis_i = {Psis_i}
        end

        E_gs_i = Psis_i[1] * H_i * Psis_i[1]

        for i, Psi in ipairs(Psis_i) do
            E = Psi * H_i * Psi

            if math.abs(E - E_gs_i) < epsilon then
                dZ[i] = 1
            else
                dZ[i] = math.exp(-(E - E_gs_i) / T)
            end

            Z = Z + dZ[i]

            if (dZ[i] / Z) < math.sqrt(epsilon) then
                i = i - 1
                NPsisIsConverged = true
                NPsis = i
                Psis_i = {unpack(Psis_i, 1, i)}
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
            Psis_i = Eigensystem(H_i, InitialRestrictions, NPsis)
        else
            Psis_i = Eigensystem(H_i, InitialRestrictions, NPsis, {{'restrictions', CalculationRestrictions}})
        end

    if not (type(Psis_i) == 'table') then
        Psis_i = {Psis_i}
    end
end

io.write(header)
for i, Psi in ipairs(Psis_i) do
    io.write(string.format('%4d', i))
    for j, Operator in ipairs(Operators) do
        io.write(string.format('%10.4f', Complex.Re(Psi * Operator * Psi)))
    end
    io.write('\n')
end
io.write(footer)

--------------------------------------------------------------------------------
-- Define the transition operators.
--------------------------------------------------------------------------------
t = math.sqrt(1/2);

Txy_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t    }, {2, 1, -t    }})
Tyz_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_1s_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t    }, {2, 2,  t    }})
Tz2_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2,  0, 1    }                })

Tx_3p_1s = NewOperator('CF', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3p, IndexDn_3p, {{1, -1, t    }, {1, 1, -t    }})
Ty_3p_1s = NewOperator('CF', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3p, IndexDn_3p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_3p_1s = NewOperator('CF', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3p, IndexDn_3p, {{1,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
calculateIso = $calculateIso

if calculateIso == 0 then
    return
end

E_gs_i = Psis_i[1] * H_i * Psis_i[1]

Psis_m = Eigensystem(H_m, IntermediateRestrictions, 1)
Psis_m = {Psis_m}
E_gs_m = Psis_m[1] * H_m * Psis_m[1]

Psis_f = Eigensystem(H_f, FinalRestrictions, 1)
Psis_f = {Psis_f}
E_gs_f = Psis_f[1] * H_f * Psis_f[1]

Eedge1 = $Eedge1
DeltaE1 = Eedge1 + E_gs_i - E_gs_m

Eedge2 = $Eedge2
DeltaE2 = Eedge2 + E_gs_i - E_gs_f

Emin1 = $Emin1 - DeltaE1
Emax1 = $Emax1 - DeltaE1
Gamma1 = $Gamma1
NE1 = $NE1

Emin2 = $Emin2 - DeltaE2
Emax2 = $Emax2 - DeltaE2
Gamma2 = $Gamma2
NE2 = $NE2

Z = 0

Giso = 0

for i, Psi in ipairs(Psis_i) do
    E = Psi * H_i * Psi

    if math.abs(E - E_gs_i) < epsilon then
        dZ = 1
    else
        dZ = math.exp(-(E - E_gs_i) / T)
    end

    Z = Z + dZ

    if calculateIso == 1 then
        for j, OperatorIn in ipairs({Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}) do
            for k, OperatorOut in ipairs({Tx_3p_1s, Ty_3p_1s, Tz_3p_1s}) do
                Giso = Giso + CreateResonantSpectra(H_m, H_f, OperatorIn, OperatorOut, Psi, {{'Emin1', Emin1}, {'Emax1', Emax1}, {'NE1', NE1}, {'Gamma1', Gamma1}, {'Emin2', Emin2}, {'Emax2', Emax2}, {'NE2', NE2}, {'Gamma2', Gamma2}}) * dZ
            end
        end
    end
end

if calculateIso == 1 then
    Giso = Giso / Z
    Giso.Print({{'file', '$baseName' .. '_iso.spec'}})
end

