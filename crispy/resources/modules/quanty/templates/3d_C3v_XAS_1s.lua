--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 3d transition metals
-- symmetry: C3v
-- experiment: XAS
-- edge: K (1s)
--------------------------------------------------------------------------------
Verbosity($verbosity)

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
H_atomic              = $H_atomic
H_cf                  = $H_cf
H_3d_4p_hybridization = $H_3d_4p_hybridization

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

if H_3d_4p_hybridization == 1 then
    NFermions = 18

    NElectrons_4p = 0

    IndexDn_4p = {12, 14, 16}
    IndexUp_4p = {13, 15, 17}
end

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_1s = NewOperator('Number', NFermions, IndexUp_1s, IndexUp_1s, {1})
     + NewOperator('Number', NFermions, IndexDn_1s, IndexDn_1s, {1})

N_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
    F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
    F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

    F0_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {1}, {0})
    G2_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {0}, {1})

    U_3d_3d_i  = $U(3d,3d)_i_value * $U(3d,3d)_i_scaling
    F2_3d_3d_i = $F2(3d,3d)_i_value * $F2(3d,3d)_i_scaling
    F4_3d_3d_i = $F4(3d,3d)_i_value * $F4(3d,3d)_i_scaling
    F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

    U_3d_3d_f  = $U(3d,3d)_f_value * $U(3d,3d)_f_scaling
    F2_3d_3d_f = $F2(3d,3d)_f_value * $F2(3d,3d)_f_scaling
    F4_3d_3d_f = $F4(3d,3d)_f_value * $F4(3d,3d)_f_scaling
    F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
    U_1s_3d_f  = $U(1s,3d)_f_value * $U(1s,3d)_f_scaling
    G2_1s_3d_f = $G2(1s,3d)_f_value * $G2(1s,3d)_f_scaling
    F0_1s_3d_f = U_1s_3d_f + 1 / 10 * G2_1s_3d_f

    H_i = H_i
        + F0_3d_3d_i * F0_3d_3d
        + F2_3d_3d_i * F2_3d_3d
        + F4_3d_3d_i * F4_3d_3d

    H_f = H_f
        + F0_3d_3d_f * F0_3d_3d
        + F2_3d_3d_f * F2_3d_3d
        + F4_3d_3d_f * F4_3d_3d
        + F0_1s_3d_f * F0_1s_3d
        + G2_1s_3d_f * G2_1s_3d

    ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

    zeta_3d_i = $zeta(3d)_i_value * $zeta(3d)_i_scaling

    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scaling

    H_i = H_i
        + zeta_3d_i * ldots_3d

    H_f = H_f
        + zeta_3d_f * ldots_3d
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    Dq_3d     = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}})
    Dsigma_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, {{2, 0, -7}})
    Dtau_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, {{4, 0, -21}})

    Dq_3d_i     = $Dq(3d)_i_value
    Dsigma_3d_i = $Dsigma(3d)_i_value
    Dtau_3d_i   = $Dtau(3d)_i_value

    Dq_3d_f     = $Dq(3d)_f_value
    Dsigma_3d_f = $Dsigma(3d)_f_value
    Dtau_3d_f   = $Dtau(3d)_f_value

    H_i = H_i
        + Dq_3d_i * Dq_3d
        + Dsigma_3d_i * Dsigma_3d
        + Dtau_3d_i * Dtau_3d

    H_f = H_f
        + Dq_3d_f * Dq_3d
        + Dsigma_3d_f * Dsigma_3d
        + Dtau_3d_f * Dtau_3d
end

--------------------------------------------------------------------------------
-- Define the 3d-4p hybridization term.
--------------------------------------------------------------------------------
if H_3d_4p_hybridization == 1 then
    F0_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
    F2_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
    G1_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
    G3_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})
    G1_1s_4p = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_4p, IndexDn_4p, {0}, {1})

    F2_3d_4p_i = $F2(3d,4p)_i_value
    G1_3d_4p_i = $G1(3d,4p)_i_value
    G3_3d_4p_i = $G3(3d,4p)_i_value

    F2_3d_4p_f = $F2(3d,4p)_i_value
    G1_3d_4p_f = $G1(3d,4p)_i_value
    G3_3d_4p_f = $G3(3d,4p)_i_value
    G1_1s_4p_f = $G1(1s,4p)_f_value

    N_4p = NewOperator('Number', NFermions, IndexUp_4p, IndexUp_4p, {1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_4p, IndexDn_4p, {1, 1, 1})

    Delta_3d_4p_i = $Delta(3d,4p)_i_value
    e_3d_i= -(NElectrons_3d - 1) * U_3d_3d_i / 2
    e_4p_i=  (NElectrons_3d - 1) * U_3d_3d_i / 2 + Delta_3d_4p_i

    Delta_3d_4p_f = $Delta(3d,4p)_f_value
    e_3d_f= -(NElectrons_3d - 1) * U_3d_3d_f / 2
    e_4p_f=  (NElectrons_3d - 1) * U_3d_3d_f / 2 + Delta_3d_4p_f

    H_i = H_i
        + F2_3d_4p_i * F2_3d_4p
        + G1_3d_4p_i * G1_3d_4p
        + G3_3d_4p_i * G3_3d_4p
        + e_3d_i * N_3d
        + e_4p_i * N_4p

    H_f = H_f
        + F2_3d_4p_f * F2_3d_4p
        + G1_3d_4p_f * G1_3d_4p
        + G3_3d_4p_f * G3_3d_4p
        + G1_1s_4p_f * G1_1s_4p
        + e_3d_f * N_3d
        + e_4p_f * N_4p

    ldots_4p = NewOperator('ldots', NFermions, IndexUp_4p, IndexDn_4p)

    zeta_4p_i = $zeta(4p)_i_value

    zeta_4p_f = $zeta(4p)_f_value

    H_i = H_i
        + zeta_4p_i * ldots_4p

    H_f = H_f
        + zeta_4p_f * ldots_4p

    Akm = {{1, 0, -math.sqrt(3 / 5)}, {3, 0, -7 / math.sqrt(15)}}
    Va1_3d_4p = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
              + NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

    Akm = {{1, 0, math.sqrt(6 / 5)}, {3, 0, -14 / 3 * math.sqrt(2 / 15)}, {3, 3, -7 / 3 / math.sqrt(3)}, {3, -3, 7 / 3 / math.sqrt(3)}}
    Ve_eg_3d_4p = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
                + NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

    Akm = {{1, 0, math.sqrt(3 / 5)}, {3, 0, -14 / 3 / math.sqrt(15)}, {3, 3, 7 / 3 * math.sqrt(2 / 3)}, {3, -3, -7 / 3 * math.sqrt(2 / 3)}}
    Ve_t2g_3d_4p = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
                 + NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

	Va1_3d_4p_i    = $Va1(3d,4p)_i_value
	Ve_eg_3d_4p_i  = $Ve(eg)(3d,4p)_i_value
	Ve_t2g_3d_4p_i = $Ve(t2g)(3d,4p)_i_value

	Va1_3d_4p_f    = $Va1(3d,4p)_f_value
	Ve_eg_3d_4p_f  = $Ve(eg)(3d,4p)_f_value
	Ve_t2g_3d_4p_f = $Ve(t2g)(3d,4p)_f_value

    H_i = H_i
        + Va1_3d_4p_i * Va1_3d_4p
        + Ve_eg_3d_4p_i * Ve_eg_3d_4p
        + Ve_t2g_3d_4p_i * Ve_t2g_3d_4p

    H_f = H_f
        + Va1_3d_4p_f * Va1_3d_4p
        + Ve_eg_3d_4p_f * Ve_eg_3d_4p
        + Ve_t2g_3d_4p_f * Ve_t2g_3d_4p
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
InitialRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_1s, NElectrons_1s},
                                           {'00 1111111111', NElectrons_3d, NElectrons_3d}}

FinalRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_1s - 1, NElectrons_1s - 1},
                                         {'00 1111111111', NElectrons_3d + 1, NElectrons_3d + 1}}

if H_3d_4p_hybridization == 1 then
    InitialRestrictions = {NFermions, NBosons, {'11 0000000000 000000', NElectrons_1s, NElectrons_1s},
                                               {'00 1111111111 000000', NElectrons_3d, NElectrons_3d},
                                               {'00 0000000000 111111', NElectrons_4p, NElectrons_4p}}

    FinalRestrictions = {NFermions, NBosons, {'11 0000000000 000000', NElectrons_1s - 1, NElectrons_1s - 1},
                                             {'00 1111111111 000000', NElectrons_3d + 1, NElectrons_3d + 1},
                                             {'00 0000000000 111111', NElectrons_4p, NElectrons_4p}}

    CalculationRestrictions = {NFermions, NBosons, {'00 0000000000 111111', NElectrons_4p, NElectrons_4p + 1}}
end

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_1s, N_3d}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_1s>    <N_3d>\n'
header = header .. '==============================================================================================\n'
footer = '==============================================================================================\n'

if H_3d_4p_hybridization == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_1s, N_3d, N_4p}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '========================================================================================================\n'
    header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_1s>    <N_3d>    <N_4p>\n'
    header = header .. '========================================================================================================\n'
    footer = '========================================================================================================\n'
end

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

if H_3d_4p_hybridization == 1 then
    Tx_1s_4p = NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1, -1, t    }, {1, 1, -t    }})
    Ty_1s_4p = NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1, -1, t * I}, {1, 1,  t * I}})
    Tz_1s_4p = NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1,  0, 1    }                })
end

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
calculateIso = $calculateIso

if calculateIso == 0 then
    return
end

E_gs_i = Psis_i[1] * H_i * Psis_i[1]

Psis_f = Eigensystem(H_f, FinalRestrictions, 1)
Psis_f = {Psis_f}
E_gs_f = Psis_f[1] * H_f * Psis_f[1]

Eedge1 = $Eedge1
DeltaE = Eedge1 + E_gs_i - E_gs_f

Emin = $Emin1 - DeltaE
Emax = $Emax1 - DeltaE
Gamma = $Gamma1
NE = $NE1

Z = 0

Giso_quad = 0
Giso_dip = 0

for i, Psi in ipairs(Psis_i) do
    E = Psi * H_i * Psi

    if math.abs(E - E_gs_i) < epsilon then
        dZ = 1
    else
        dZ = math.exp(-(E - E_gs_i) / T)
    end

    Z = Z + dZ

    if calculateIso == 1 then
        if H_3d_4p_hybridization == 1 then
            for j, Operator in ipairs({Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}) do
                Giso_quad = Giso_quad + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}}) * dZ
            end
            for k, Operator in ipairs({Tx_1s_4p, Ty_1s_4p, Tz_1s_4p}) do
                Giso_dip = Giso_dip + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}}) * dZ
            end
        else
            for j, Operator in ipairs({Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}) do
                Giso_quad = Giso_quad + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
            end
        end
    end
end

alpha = 7.2973525664E-3
a0 = 5.2917721067E-1
hbar = 6.582119514E-16
c = 2.99792458E+18

P1_1s_4p = $P1(1s,4p)
P2_1s_3d = $P2(1s,3d)

Iedge1 = 1e-5 -- edge jump

if calculateIso == 1 then
    if H_3d_4p_hybridization == 1 then
        Giso_quad = (4 * math.pi^2 * alpha * a0^4 / (2 * hbar * c)^2 * P2_1s_3d^2 * Eedge1^3 / Iedge1 / math.pi) * Giso_quad / Z / 15
        Giso_dip  = (4 * math.pi^2 * alpha * a0^2                    * P1_1s_4p^2 * Eedge1   / Iedge1 / math.pi) * Giso_dip / Z / 3
    else
        Giso_quad = Giso_quad / Z / 15
    end

    Giso = Giso_quad + Giso_dip
    Giso.Print({{'file', '$baseName' .. '_iso.spec'}})
end

