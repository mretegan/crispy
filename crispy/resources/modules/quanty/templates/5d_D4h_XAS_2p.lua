--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 5d transition metals
-- symmetry: D4h
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
H_atomic         = $H_atomic
H_cf             = $H_cf
H_magnetic_field = $H_magnetic_field
H_exchange_field = $H_exchange_field

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_2p = 6
NElectrons_5d = $NElectrons_5d

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_5d = {6, 8, 10, 12, 14}
IndexUp_5d = {7, 9, 11, 13, 15}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2p = NewOperator('Number', NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_5d = NewOperator('Number', NFermions, IndexUp_5d, IndexUp_5d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_5d, IndexDn_5d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {1, 0, 0})
    F2_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 1, 0})
    F4_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 0, 1})

    F0_2p_5d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {1, 0}, {0, 0})
    F2_2p_5d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {0, 1}, {0, 0})
    G1_2p_5d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {0, 0}, {1, 0})
    G3_2p_5d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {0, 0}, {0, 1})

    U_5d_5d_i  = $U(5d,5d)_i_value * $U(5d,5d)_i_scaling
    F2_5d_5d_i = $F2(5d,5d)_i_value * $F2(5d,5d)_i_scaling
    F4_5d_5d_i = $F4(5d,5d)_i_value * $F4(5d,5d)_i_scaling
    F0_5d_5d_i = U_5d_5d_i + 2 / 63 * F2_5d_5d_i + 2 / 63 * F4_5d_5d_i

    U_5d_5d_f  = $U(5d,5d)_f_value * $U(5d,5d)_f_scaling
    F2_5d_5d_f = $F2(5d,5d)_f_value * $F2(5d,5d)_f_scaling
    F4_5d_5d_f = $F4(5d,5d)_f_value * $F4(5d,5d)_f_scaling
    F0_5d_5d_f = U_5d_5d_f + 2 / 63 * F2_5d_5d_f + 2 / 63 * F4_5d_5d_f
    U_2p_5d_f  = $U(2p,5d)_f_value * $U(2p,5d)_f_scaling
    F2_2p_5d_f = $F2(2p,5d)_f_value * $F2(2p,5d)_f_scaling
    G1_2p_5d_f = $G1(2p,5d)_f_value * $G1(2p,5d)_f_scaling
    G3_2p_5d_f = $G3(2p,5d)_f_value * $G3(2p,5d)_f_scaling
    F0_2p_5d_f = U_2p_5d_f + 1 / 15 * G1_2p_5d_f + 3 / 70 * G3_2p_5d_f

    H_i = H_i
        + F0_5d_5d_i * F0_5d_5d
        + F2_5d_5d_i * F2_5d_5d
        + F4_5d_5d_i * F4_5d_5d

    H_f = H_f
        + F0_5d_5d_f * F0_5d_5d
        + F2_5d_5d_f * F2_5d_5d
        + F4_5d_5d_f * F4_5d_5d
        + F0_2p_5d_f * F0_2p_5d
        + F2_2p_5d_f * F2_2p_5d
        + G1_2p_5d_f * G1_2p_5d
        + G3_2p_5d_f * G3_2p_5d

    ldots_5d = NewOperator('ldots', NFermions, IndexUp_5d, IndexDn_5d)

    ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

    zeta_5d_i = $zeta(5d)_i_value * $zeta(5d)_i_scaling

    zeta_5d_f = $zeta(5d)_f_value * $zeta(5d)_f_scaling
    zeta_2p_f = $zeta(2p)_f_value * $zeta(2p)_f_scaling

    H_i = H_i
        + zeta_5d_i * ldots_5d

    H_f = H_f
        + zeta_5d_f * ldots_5d
        + zeta_2p_f * ldots_2p
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('D4h', 2, {Ea1g, Eb1g, Eb2g, Eeg})
    Dq_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('D4h', 2, { 6,  6, -4, -4}))
    Ds_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('D4h', 2, {-2,  2,  2, -1}))
    Dt_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('D4h', 2, {-6, -1, -1,  4}))

    Dq_5d_i = $Dq(5d)_i_value
    Ds_5d_i = $Ds(5d)_i_value
    Dt_5d_i = $Dt(5d)_i_value

    Dq_5d_f = $Dq(5d)_f_value
    Ds_5d_f = $Ds(5d)_f_value
    Dt_5d_f = $Dt(5d)_f_value

    H_i = H_i
        + Dq_5d_i * Dq_5d
        + Ds_5d_i * Ds_5d
        + Dt_5d_i * Dt_5d

    H_f = H_f
        + Dq_5d_f * Dq_5d
        + Ds_5d_f * Ds_5d
        + Dt_5d_f * Dt_5d
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_5d    = NewOperator('Sx'   , NFermions, IndexUp_5d, IndexDn_5d)
Sy_5d    = NewOperator('Sy'   , NFermions, IndexUp_5d, IndexDn_5d)
Sz_5d    = NewOperator('Sz'   , NFermions, IndexUp_5d, IndexDn_5d)
Ssqr_5d  = NewOperator('Ssqr' , NFermions, IndexUp_5d, IndexDn_5d)
Splus_5d = NewOperator('Splus', NFermions, IndexUp_5d, IndexDn_5d)
Smin_5d  = NewOperator('Smin' , NFermions, IndexUp_5d, IndexDn_5d)

Lx_5d    = NewOperator('Lx'   , NFermions, IndexUp_5d, IndexDn_5d)
Ly_5d    = NewOperator('Ly'   , NFermions, IndexUp_5d, IndexDn_5d)
Lz_5d    = NewOperator('Lz'   , NFermions, IndexUp_5d, IndexDn_5d)
Lsqr_5d  = NewOperator('Lsqr' , NFermions, IndexUp_5d, IndexDn_5d)
Lplus_5d = NewOperator('Lplus', NFermions, IndexUp_5d, IndexDn_5d)
Lmin_5d  = NewOperator('Lmin' , NFermions, IndexUp_5d, IndexDn_5d)

Jx_5d    = NewOperator('Jx'   , NFermions, IndexUp_5d, IndexDn_5d)
Jy_5d    = NewOperator('Jy'   , NFermions, IndexUp_5d, IndexDn_5d)
Jz_5d    = NewOperator('Jz'   , NFermions, IndexUp_5d, IndexDn_5d)
Jsqr_5d  = NewOperator('Jsqr' , NFermions, IndexUp_5d, IndexDn_5d)
Jplus_5d = NewOperator('Jplus', NFermions, IndexUp_5d, IndexDn_5d)
Jmin_5d  = NewOperator('Jmin' , NFermions, IndexUp_5d, IndexDn_5d)

Sx = Sx_5d
Sy = Sy_5d
Sz = Sz_5d

Lx = Lx_5d
Ly = Ly_5d
Lz = Lz_5d

Jx = Jx_5d
Jy = Jy_5d
Jz = Jz_5d

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
                                           {'000000 1111111111', NElectrons_5d, NElectrons_5d}}

FinalRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                         {'000000 1111111111', NElectrons_5d + 1, NElectrons_5d + 1}}

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2p, N_5d}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2p>    <N_5d>\n'
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
    Z = 0
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

Tx_2p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2p, IndexDn_2p, {{1, -1, t    }, {1, 1, -t    }})
Ty_2p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2p, IndexDn_2p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_2p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2p, IndexDn_2p, {{1,  0, 1    }                })

Tein1_2p_5d = ein1[1] * Tx_2p_5d + ein1[2] * Ty_2p_5d + ein1[3] * Tz_2p_5d
Tein2_2p_5d = ein2[1] * Tx_2p_5d + ein2[2] * Ty_2p_5d + ein2[3] * Tz_2p_5d

Tr_2p_5d =  t * (Tein1_2p_5d - I * Tein2_2p_5d)
Tl_2p_5d = -t * (Tein1_2p_5d + I * Tein2_2p_5d)

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
        Giso = Giso + CreateSpectra(H_f, {Tx_2p_5d, Ty_2p_5d, Tz_2p_5d}, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    end

    if calculateCD == 1 then
        Gr = Gr + CreateSpectra(H_f, Tr_2p_5d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        Gl = Gl + CreateSpectra(H_f, Tl_2p_5d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    end

    if calculateLD == 1 then
        Gein1 = Gein1 + CreateSpectra(H_f, Tein1_2p_5d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        Gein2 = Gein2 + CreateSpectra(H_f, Tein2_2p_5d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
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

