--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: lathanides
-- symmetry: Oh
-- experiment: XAS
-- edge: M4,5 (3d)
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
NFermions = 24
NBosons = 0

NElectrons_3d = 10
NElectrons_4f = $NElectrons_4f

IndexDn_3d = {0, 2, 4, 6, 8}
IndexUp_3d = {1, 3, 5, 7, 9}
IndexDn_4f = {10, 12, 14, 16, 18, 20, 22}
IndexUp_4f = {11, 13, 15, 17, 19, 21, 23}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

N_4f = NewOperator('Number', NFermions, IndexUp_4f, IndexUp_4f, {1, 1, 1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_4f, IndexDn_4f, {1, 1, 1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {1, 0, 0, 0})
    F2_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 1, 0, 0})
    F4_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 1, 0})
    F6_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 0, 1})

    F0_3d_4f = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {1, 0, 0}, {0, 0, 0});
    F2_3d_4f = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 1, 0}, {0, 0, 0});
    F4_3d_4f = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 1}, {0, 0, 0});
    G1_3d_4f = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {1, 0, 0});
    G3_3d_4f = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 1, 0});
    G5_3d_4f = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 0, 1});

    U_4f_4f_i  = $U(4f,4f)_i_value * $U(4f,4f)_i_scaling
    F2_4f_4f_i = $F2(4f,4f)_i_value * $F2(4f,4f)_i_scaling
    F4_4f_4f_i = $F4(4f,4f)_i_value * $F4(4f,4f)_i_scaling
    F6_4f_4f_i = $F6(4f,4f)_i_value * $F6(4f,4f)_i_scaling
    F0_4f_4f_i = U_4f_4f_i + 4 / 195 * F2_4f_4f_i + 2 / 143 * F4_4f_4f_i + 100 / 5577 * F6_4f_4f_i

    U_4f_4f_f  = $U(4f,4f)_f_value * $U(4f,4f)_f_scaling
    F2_4f_4f_f = $F2(4f,4f)_f_value * $F2(4f,4f)_f_scaling
    F4_4f_4f_f = $F4(4f,4f)_f_value * $F4(4f,4f)_f_scaling
    F6_4f_4f_f = $F6(4f,4f)_f_value * $F6(4f,4f)_f_scaling
    F0_4f_4f_f = U_4f_4f_f + 4 / 195 * F2_4f_4f_f + 2 / 143 * F4_4f_4f_f + 100 / 5577 * F6_4f_4f_f
    U_3d_4f_f  = $U(3d,4f)_f_value * $U(3d,4f)_f_scaling
    F2_3d_4f_f = $F2(3d,4f)_f_value * $F2(3d,4f)_f_scaling
    F4_3d_4f_f = $F4(3d,4f)_f_value * $F4(3d,4f)_f_scaling
    G1_3d_4f_f = $G1(3d,4f)_f_value * $G1(3d,4f)_f_scaling
    G3_3d_4f_f = $G3(3d,4f)_f_value * $G3(3d,4f)_f_scaling
    G5_3d_4f_f = $G5(3d,4f)_f_value * $G5(3d,4f)_f_scaling
    F0_3d_4f_f = U_3d_4f_f + 3 / 70 * G1_3d_4f_f + 2 / 105 * G3_3d_4f_f + 5 / 231 * G5_3d_4f_f

    H_i = H_i
        + F0_4f_4f_i * F0_4f_4f
        + F2_4f_4f_i * F2_4f_4f
        + F4_4f_4f_i * F4_4f_4f
        + F6_4f_4f_i * F6_4f_4f

    H_f = H_f
        + F0_4f_4f_f * F0_4f_4f
        + F2_4f_4f_f * F2_4f_4f
        + F4_4f_4f_f * F4_4f_4f
        + F6_4f_4f_f * F6_4f_4f
        + F0_3d_4f_f * F0_3d_4f
        + F2_3d_4f_f * F2_3d_4f
        + F4_3d_4f_f * F4_3d_4f
        + G1_3d_4f_f * G1_3d_4f
        + G3_3d_4f_f * G3_3d_4f
        + G5_3d_4f_f * G5_3d_4f

    ldots_4f = NewOperator('ldots', NFermions, IndexUp_4f, IndexDn_4f)

    ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

    zeta_4f_i = $zeta(4f)_i_value * $zeta(4f)_i_scaling

    zeta_4f_f = $zeta(4f)_f_value * $zeta(4f)_f_scaling
    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scaling

    H_i = H_i
        + zeta_4f_i * ldots_4f

    H_f = H_f
        + zeta_4f_f * ldots_4f
        + zeta_3d_f * ldots_3d
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('Oh', 3, {Ea2u, Et1u, Et2u})
    Ea2u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {1, 0, 0}))
    Et2u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 1, 0}))
    Et1u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 0, 1}))

    Ea2u_4f_i = $Ea2u(4f)_i_value
    Et2u_4f_i = $Et2u(4f)_i_value
    Et1u_4f_i = $Et1u(4f)_i_value

    Ea2u_4f_f = $Ea2u(4f)_f_value
    Et2u_4f_f = $Et2u(4f)_f_value
    Et1u_4f_f = $Et1u(4f)_f_value

    -- Set to zero the barycenter of the orbital energies.
    E_4f_i = (Ea2u_4f_i + 3 * Et2u_4f_i + 3 * Et1u_4f_i) / 7
    Ea2u_4f_i = Ea2u_4f_i - E_4f_i
    Et2u_4f_i = Et2u_4f_i - E_4f_i
    Et1u_4f_i = Et1u_4f_i - E_4f_i

    E_4f_f = (Ea2u_4f_f + 3 * Et2u_4f_f + 3 * Et1u_4f_f) / 7
    Ea2u_4f_f = Ea2u_4f_f - E_4f_f
    Et2u_4f_f = Et2u_4f_f - E_4f_f
    Et1u_4f_f = Et1u_4f_f - E_4f_f

    H_i = H_i
        + Ea2u_4f_i * Ea2u_4f
        + Et2u_4f_i * Et2u_4f
        + Et1u_4f_i * Et1u_4f

    H_f = H_f
        + Ea2u_4f_f * Ea2u_4f
        + Et2u_4f_f * Et2u_4f
        + Et1u_4f_f * Et1u_4f
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4f    = NewOperator('Sx'   , NFermions, IndexUp_4f, IndexDn_4f)
Sy_4f    = NewOperator('Sy'   , NFermions, IndexUp_4f, IndexDn_4f)
Sz_4f    = NewOperator('Sz'   , NFermions, IndexUp_4f, IndexDn_4f)
Ssqr_4f  = NewOperator('Ssqr' , NFermions, IndexUp_4f, IndexDn_4f)
Splus_4f = NewOperator('Splus', NFermions, IndexUp_4f, IndexDn_4f)
Smin_4f  = NewOperator('Smin' , NFermions, IndexUp_4f, IndexDn_4f)

Lx_4f    = NewOperator('Lx'   , NFermions, IndexUp_4f, IndexDn_4f)
Ly_4f    = NewOperator('Ly'   , NFermions, IndexUp_4f, IndexDn_4f)
Lz_4f    = NewOperator('Lz'   , NFermions, IndexUp_4f, IndexDn_4f)
Lsqr_4f  = NewOperator('Lsqr' , NFermions, IndexUp_4f, IndexDn_4f)
Lplus_4f = NewOperator('Lplus', NFermions, IndexUp_4f, IndexDn_4f)
Lmin_4f  = NewOperator('Lmin' , NFermions, IndexUp_4f, IndexDn_4f)

Jx_4f    = NewOperator('Jx'   , NFermions, IndexUp_4f, IndexDn_4f)
Jy_4f    = NewOperator('Jy'   , NFermions, IndexUp_4f, IndexDn_4f)
Jz_4f    = NewOperator('Jz'   , NFermions, IndexUp_4f, IndexDn_4f)
Jsqr_4f  = NewOperator('Jsqr' , NFermions, IndexUp_4f, IndexDn_4f)
Jplus_4f = NewOperator('Jplus', NFermions, IndexUp_4f, IndexDn_4f)
Jmin_4f  = NewOperator('Jmin' , NFermions, IndexUp_4f, IndexDn_4f)

Sx = Sx_4f
Sy = Sy_4f
Sz = Sz_4f

Lx = Lx_4f
Ly = Ly_4f
Lz = Lz_4f

Jx = Jx_4f
Jy = Jy_4f
Jz = Jz_4f

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
InitialRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_3d, NElectrons_3d},
                                           {'0000000000 11111111111111', NElectrons_4f, NElectrons_4f}}

FinalRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_3d - 1, NElectrons_3d - 1},
                                         {'0000000000 11111111111111', NElectrons_4f + 1, NElectrons_4f + 1}}

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_3d, N_4f}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_3d>    <N_4f>\n'
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

kin = $kin
ein1 = $ein1
ein2 = $ein2

Tx_3d_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_3d, IndexDn_3d, {{1, -1, t    }, {1, 1, -t    }})
Ty_3d_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_3d, IndexDn_3d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_3d_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_3d, IndexDn_3d, {{1,  0, 1    }                })

Tein1_3d_4f = ein1[1] * Tx_3d_4f + ein1[2] * Ty_3d_4f + ein1[3] * Tz_3d_4f
Tein2_3d_4f = ein2[1] * Tx_3d_4f + ein2[2] * Ty_3d_4f + ein2[3] * Tz_3d_4f

Tr_3d_4f =  t * (Tein1_3d_4f - I * Tein2_3d_4f)
Tl_3d_4f = -t * (Tein1_3d_4f + I * Tein2_3d_4f)

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
        for j, Operator in ipairs({Tx_3d_4f, Ty_3d_4f, Tz_3d_4f}) do
            Giso = Giso + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        end
    end

    if calculateCD == 1 then
        Gr = Gr + CreateSpectra(H_f, Tr_3d_4f, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        Gl = Gl + CreateSpectra(H_f, Tl_3d_4f, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    end

    if calculateLD == 1 then
        Gein1 = Gein1 + CreateSpectra(H_f, Tein1_3d_4f, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        Gein2 = Gein2 + CreateSpectra(H_f, Tein2_3d_4f, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    end
end
io.write(string.format('===============\n'))

Gmin1 = $Gmin1 - Gamma
Gmax1 = $Gmax1 - Gamma
Egamma1 = $Egamma1 - DeltaE

if calculateIso == 1 then
    Giso = Giso / Z / 3
    Giso.Broaden(0, {{Emin, Gmin1}, {Egamma1, Gmin1}, {Egamma1, Gmax1}, {Emax, Gmax1}})
    Giso.Print({{'file', '$baseName' .. '_iso.spec'}})
end

if calculateCD == 1 then
    Gr = Gr / Z
    Gl = Gl / Z
    Gcd = Gr - Gl
    Gcd.Broaden(0, {{Emin, Gmin1}, {Egamma1, Gmin1}, {Egamma1, Gmax1}, {Emax, Gmax1}})
    Gcd.Print({{'file', '$baseName' .. '_cd.spec'}})
end

if calculateLD == 1 then
    Gein1 = Gein1 / Z
    Gein2 = Gein2 / Z
    Gld = Gein1 - Gein2
    Gld.Broaden(0, {{Emin, Gmin1}, {Egamma1, Gmin1}, {Egamma1, Gmax1}, {Emax, Gmax1}})
    Gld.Print({{'file', '$baseName' .. '_ld.spec'}})
end

