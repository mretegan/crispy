--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 4d transition metals
-- symmetry: Oh
-- experiment: XAS
-- edge: L2,3 (2p)
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
H_4d_Ld_hybridization = $H_4d_Ld_hybridization
H_magnetic_field      = $H_magnetic_field
H_exchange_field      = $H_exchange_field

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

if H_4d_Ld_hybridization == 1 then
    NFermions = 26

    NElectrons_Ld = 10

    IndexDn_Ld = {16, 18, 20, 22, 24}
    IndexUp_Ld = {17, 19, 21, 23, 25}
end

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2p = NewOperator('Number', NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_4d = NewOperator('Number', NFermions, IndexUp_4d, IndexUp_4d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_4d, IndexDn_4d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_4d_4d = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, {1, 0, 0})
    F2_4d_4d = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, {0, 1, 0})
    F4_4d_4d = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, {0, 0, 1})

    F0_2p_4d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {1, 0}, {0, 0})
    F2_2p_4d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {0, 1}, {0, 0})
    G1_2p_4d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {0, 0}, {1, 0})
    G3_2p_4d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4d, IndexDn_4d, {0, 0}, {0, 1})

    U_4d_4d_i  = $U(4d,4d)_i_value * $U(4d,4d)_i_scaling
    F2_4d_4d_i = $F2(4d,4d)_i_value * $F2(4d,4d)_i_scaling
    F4_4d_4d_i = $F4(4d,4d)_i_value * $F4(4d,4d)_i_scaling
    F0_4d_4d_i = U_4d_4d_i + 2 / 63 * F2_4d_4d_i + 2 / 63 * F4_4d_4d_i

    U_4d_4d_f  = $U(4d,4d)_f_value * $U(4d,4d)_f_scaling
    F2_4d_4d_f = $F2(4d,4d)_f_value * $F2(4d,4d)_f_scaling
    F4_4d_4d_f = $F4(4d,4d)_f_value * $F4(4d,4d)_f_scaling
    F0_4d_4d_f = U_4d_4d_f + 2 / 63 * F2_4d_4d_f + 2 / 63 * F4_4d_4d_f
    U_2p_4d_f  = $U(2p,4d)_f_value * $U(2p,4d)_f_scaling
    F2_2p_4d_f = $F2(2p,4d)_f_value * $F2(2p,4d)_f_scaling
    G1_2p_4d_f = $G1(2p,4d)_f_value * $G1(2p,4d)_f_scaling
    G3_2p_4d_f = $G3(2p,4d)_f_value * $G3(2p,4d)_f_scaling
    F0_2p_4d_f = U_2p_4d_f + 1 / 15 * G1_2p_4d_f + 3 / 70 * G3_2p_4d_f

    H_i = H_i
        + F0_4d_4d_i * F0_4d_4d
        + F2_4d_4d_i * F2_4d_4d
        + F4_4d_4d_i * F4_4d_4d

    H_f = H_f
        + F0_4d_4d_f * F0_4d_4d
        + F2_4d_4d_f * F2_4d_4d
        + F4_4d_4d_f * F4_4d_4d
        + F0_2p_4d_f * F0_2p_4d
        + F2_2p_4d_f * F2_2p_4d
        + G1_2p_4d_f * G1_2p_4d
        + G3_2p_4d_f * G3_2p_4d

    ldots_4d = NewOperator('ldots', NFermions, IndexUp_4d, IndexDn_4d)

    ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

    zeta_4d_i = $zeta(4d)_i_value * $zeta(4d)_i_scaling

    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scaling
    zeta_2p_f = $zeta(2p)_f_value * $zeta(2p)_f_scaling

    H_i = H_i
        + zeta_4d_i * ldots_4d

    H_f = H_f
        + zeta_4d_f * ldots_4d
        + zeta_2p_f * ldots_2p
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('Oh', 2, {Eeg, Et2g})
    tenDq_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

    tenDq_4d_i = $10Dq(4d)_i_value

    tenDq_4d_f = $10Dq(4d)_f_value

    H_i = H_i
        + tenDq_4d_i * tenDq_4d

    H_f = H_f
        + tenDq_4d_f * tenDq_4d
end

--------------------------------------------------------------------------------
-- Define the 4d-Ld hybridization term.
--------------------------------------------------------------------------------
if H_4d_Ld_hybridization == 1 then
    N_Ld = NewOperator('Number', NFermions, IndexUp_Ld, IndexUp_Ld, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_Ld, IndexDn_Ld, {1, 1, 1, 1, 1})

    Delta_4d_Ld_i = $Delta(4d,Ld)_i_value
    e_4d_i  = (10 * Delta_4d_Ld_i - NElectrons_4d * (19 + NElectrons_4d) * U_4d_4d_i / 2) / (10 + NElectrons_4d)
    e_Ld_i  = NElectrons_4d * ((1 + NElectrons_4d) * U_4d_4d_i / 2 - Delta_4d_Ld_i) / (10 + NElectrons_4d)

    Delta_4d_Ld_f = $Delta(4d,Ld)_f_value
    e_2p_f = (10 * Delta_4d_Ld_f + (1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 - (10 + NElectrons_4d) * U_2p_4d_f)) / (16 + NElectrons_4d)
    e_4d_f = (10 * Delta_4d_Ld_f - NElectrons_4d * (31 + NElectrons_4d) * U_4d_4d_f / 2 - 90 * U_2p_4d_f) / (16 + NElectrons_4d)
    e_Ld_f = ((1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 + 6 * U_2p_4d_f) - (6 + NElectrons_4d) * Delta_4d_Ld_f) / (16 + NElectrons_4d)

    H_i = H_i
        + e_4d_i * N_4d
        + e_Ld_i * N_Ld

    H_f = H_f
        + e_2p_f * N_2p
        + e_4d_f * N_4d
        + e_Ld_f * N_Ld

    tenDq_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

    Vt2g_4d_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Oh', 2, {0, 1}))
               + NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {0, 1}))

    Veg_4d_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Oh', 2, {1, 0}))
              + NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {1, 0}))

    tenDq_Ld_i   = $10Dq(Ld)_i_value
    Veg_4d_Ld_i  = $Veg(4d,Ld)_i_value
    Vt2g_4d_Ld_i = $Vt2g(4d,Ld)_i_value

    tenDq_Ld_f   = $10Dq(Ld)_f_value
    Veg_4d_Ld_f  = $Veg(4d,Ld)_f_value
    Vt2g_4d_Ld_f = $Vt2g(4d,Ld)_f_value

    H_i = H_i
        + tenDq_Ld_i   * tenDq_Ld
        + Veg_4d_Ld_i  * Veg_4d_Ld
        + Vt2g_4d_Ld_i * Vt2g_4d_Ld

    H_f = H_f
        + tenDq_Ld_f   * tenDq_Ld
        + Veg_4d_Ld_f  * Veg_4d_Ld
        + Vt2g_4d_Ld_f * Vt2g_4d_Ld
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4d    = NewOperator('Sx'   , NFermions, IndexUp_4d, IndexDn_4d)
Sy_4d    = NewOperator('Sy'   , NFermions, IndexUp_4d, IndexDn_4d)
Sz_4d    = NewOperator('Sz'   , NFermions, IndexUp_4d, IndexDn_4d)
Ssqr_4d  = NewOperator('Ssqr' , NFermions, IndexUp_4d, IndexDn_4d)
Splus_4d = NewOperator('Splus', NFermions, IndexUp_4d, IndexDn_4d)
Smin_4d  = NewOperator('Smin' , NFermions, IndexUp_4d, IndexDn_4d)

Lx_4d    = NewOperator('Lx'   , NFermions, IndexUp_4d, IndexDn_4d)
Ly_4d    = NewOperator('Ly'   , NFermions, IndexUp_4d, IndexDn_4d)
Lz_4d    = NewOperator('Lz'   , NFermions, IndexUp_4d, IndexDn_4d)
Lsqr_4d  = NewOperator('Lsqr' , NFermions, IndexUp_4d, IndexDn_4d)
Lplus_4d = NewOperator('Lplus', NFermions, IndexUp_4d, IndexDn_4d)
Lmin_4d  = NewOperator('Lmin' , NFermions, IndexUp_4d, IndexDn_4d)

Jx_4d    = NewOperator('Jx'   , NFermions, IndexUp_4d, IndexDn_4d)
Jy_4d    = NewOperator('Jy'   , NFermions, IndexUp_4d, IndexDn_4d)
Jz_4d    = NewOperator('Jz'   , NFermions, IndexUp_4d, IndexDn_4d)
Jsqr_4d  = NewOperator('Jsqr' , NFermions, IndexUp_4d, IndexDn_4d)
Jplus_4d = NewOperator('Jplus', NFermions, IndexUp_4d, IndexDn_4d)
Jmin_4d  = NewOperator('Jmin' , NFermions, IndexUp_4d, IndexDn_4d)

Sx = Sx_4d
Sy = Sy_4d
Sz = Sz_4d

Lx = Lx_4d
Ly = Ly_4d
Lz = Lz_4d

Jx = Jx_4d
Jy = Jy_4d
Jz = Jz_4d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if H_magnetic_field == 1 then
    Bx_i = $Bx_i_value * EnergyUnits.Tesla.value
    By_i = $By_i_value * EnergyUnits.Tesla.value
    Bz_i = $Bz_i_value * EnergyUnits.Tesla.value

    Bx_f = $Bx_f_value * EnergyUnits.Tesla.value
    By_f = $By_f_value * EnergyUnits.Tesla.value
    Bz_f = $Bz_f_value * EnergyUnits.Tesla.value

    H_i = H_i
        + Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz)

    H_f = H_f
        + Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz)
end

if H_exchange_field == 1 then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i
        + Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz

    H_f = H_f
        + Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz
end

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_2p, NElectrons_2p},
                                           {'000000 1111111111', NElectrons_4d, NElectrons_4d}}

FinalRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                         {'000000 1111111111', NElectrons_4d + 1, NElectrons_4d + 1}}

if H_4d_Ld_hybridization == 1 then
    InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_2p, NElectrons_2p},
                                               {'000000 1111111111 1111111111', NElectrons_4d + NElectrons_Ld, NElectrons_4d + NElectrons_Ld}}

    FinalRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                             {'000000 1111111111 1111111111', NElectrons_4d + NElectrons_Ld + 1, NElectrons_4d + NElectrons_Ld + 1}}
end

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2p, N_4d}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2p>    <N_4d>\n'
header = header .. '==============================================================================================\n'
footer = '==============================================================================================\n'

if H_4d_Ld_hybridization == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2p, N_4d, N_Ld}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '========================================================================================================\n'
    header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2p>    <N_4d>    <N_Ld>\n'
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

kin = $kin
ein1 = $ein1
ein2 = $ein2

Tx_2p_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_2p, IndexDn_2p, {{1, -1, t    }, {1, 1, -t    }})
Ty_2p_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_2p, IndexDn_2p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_2p_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_2p, IndexDn_2p, {{1,  0, 1    }                })

Tein1_2p_4d = ein1[1] * Tx_2p_4d + ein1[2] * Ty_2p_4d + ein1[3] * Tz_2p_4d
Tein2_2p_4d = ein2[1] * Tx_2p_4d + ein2[2] * Ty_2p_4d + ein2[3] * Tz_2p_4d

Tr_2p_4d =  t * (Tein1_2p_4d - I * Tein2_2p_4d)
Tl_2p_4d = -t * (Tein1_2p_4d + I * Tein2_2p_4d)

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
calculateIso = $calculateIso
calculateCD  = $calculateCD
calculateLD  = $calculateLD

if calculateIso == 0 and calculateCD == 0 and calculateLD == 0 then
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

Giso = 0

Gr = 0
Gl = 0

Gein1 = 0
Gein2 = 0

io.write(string.format('\nSpectrum calculation for each of the selected states:\n'))
io.write(string.format('===============\n'))
io.write(string.format('   i         dZ\n'))
io.write(string.format('===============\n'))

for i, Psi in ipairs(Psis_i) do
    E = Psi * H_i * Psi

    if math.abs(E - E_gs_i) < epsilon then
        dZ = 1
    else
        dZ = math.exp(-(E - E_gs_i) / T)
    end

    Z = Z + dZ

    io.write(string.format('%4d   %3.2E\n', i, dZ))

    if calculateIso == 1 then
        for j, Operator in ipairs({Tx_2p_4d, Ty_2p_4d, Tz_2p_4d}) do
            Giso = Giso + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        end
    end

    if calculateCD == 1 then
        Gr = Gr + CreateSpectra(H_f, Tr_2p_4d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        Gl = Gl + CreateSpectra(H_f, Tl_2p_4d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    end

    if calculateLD == 1 then
        Gein1 = Gein1 + CreateSpectra(H_f, Tein1_2p_4d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        Gein2 = Gein2 + CreateSpectra(H_f, Tein2_2p_4d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    end
end
io.write(string.format('===============\n'))

if calculateIso == 1 then
    Giso = Giso / Z / 3
    Giso.Print({{'file', '$baseName' .. '_iso.spec'}})
end

if calculateCD == 1 then
    Gr = Gr / Z
    Gl = Gl / Z
    Gcd = Gr - Gl
    Gcd.Print({{'file', '$baseName' .. '_cd.spec'}})
end

if calculateLD == 1 then
    Gein1 = Gein1 / Z
    Gein2 = Gein2 / Z
    Gld = Gein1 - Gein2
    Gld.Print({{'file', '$baseName' .. '_ld.spec'}})
end
