--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4f
-- symmetry: Oh
-- experiment: XPS
-- edge: M4,5 (3d)
--------------------------------------------------------------------------------
Verbosity($Verbosity)

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
H_atomic = $H_atomic
H_crystal_field = $H_crystal_field
H_4f_ligands_hybridization_lmct = $H_4f_ligands_hybridization_lmct
H_magnetic_field = $H_magnetic_field
H_exchange_field = $H_exchange_field

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 24

NElectrons_3d = 10
NElectrons_4f = $NElectrons_4f

IndexDn_3d = {0, 2, 4, 6, 8}
IndexUp_3d = {1, 3, 5, 7, 9}
IndexDn_4f = {10, 12, 14, 16, 18, 20, 22}
IndexUp_4f = {11, 13, 15, 17, 19, 21, 23}

if H_4f_ligands_hybridization_lmct == 1 then
    NFermions = 38

    NElectrons_L1 = 14

    IndexDn_L1 = {24, 26, 28, 30, 32, 34, 36}
    IndexUp_L1 = {25, 27, 29, 31, 33, 35, 37}
end

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

    U_4f_4f_i = $U(4f,4f)_i_value
    F2_4f_4f_i = $F2(4f,4f)_i_value * $F2(4f,4f)_i_scale
    F4_4f_4f_i = $F4(4f,4f)_i_value * $F4(4f,4f)_i_scale
    F6_4f_4f_i = $F6(4f,4f)_i_value * $F6(4f,4f)_i_scale
    F0_4f_4f_i = U_4f_4f_i + 4 / 195 * F2_4f_4f_i + 2 / 143 * F4_4f_4f_i + 100 / 5577 * F6_4f_4f_i

    U_4f_4f_f = $U(4f,4f)_f_value
    F2_4f_4f_f = $F2(4f,4f)_f_value * $F2(4f,4f)_f_scale
    F4_4f_4f_f = $F4(4f,4f)_f_value * $F4(4f,4f)_f_scale
    F6_4f_4f_f = $F6(4f,4f)_f_value * $F6(4f,4f)_f_scale
    F0_4f_4f_f = U_4f_4f_f + 4 / 195 * F2_4f_4f_f + 2 / 143 * F4_4f_4f_f + 100 / 5577 * F6_4f_4f_f
    U_3d_4f_f = $U(3d,4f)_f_value
    F2_3d_4f_f = $F2(3d,4f)_f_value * $F2(3d,4f)_f_scale
    F4_3d_4f_f = $F4(3d,4f)_f_value * $F4(3d,4f)_f_scale
    G1_3d_4f_f = $G1(3d,4f)_f_value * $G1(3d,4f)_f_scale
    G3_3d_4f_f = $G3(3d,4f)_f_value * $G3(3d,4f)_f_scale
    G5_3d_4f_f = $G5(3d,4f)_f_value * $G5(3d,4f)_f_scale
    F0_3d_4f_f = U_3d_4f_f + 3 / 70 * G1_3d_4f_f + 2 / 105 * G3_3d_4f_f + 5 / 231 * G5_3d_4f_f

    H_i = H_i + Chop(
          F0_4f_4f_i * F0_4f_4f
        + F2_4f_4f_i * F2_4f_4f
        + F4_4f_4f_i * F4_4f_4f
        + F6_4f_4f_i * F6_4f_4f)

    H_f = H_f + Chop(
          F0_4f_4f_f * F0_4f_4f
        + F2_4f_4f_f * F2_4f_4f
        + F4_4f_4f_f * F4_4f_4f
        + F6_4f_4f_f * F6_4f_4f
        + F0_3d_4f_f * F0_3d_4f
        + F2_3d_4f_f * F2_3d_4f
        + F4_3d_4f_f * F4_3d_4f
        + G1_3d_4f_f * G1_3d_4f
        + G3_3d_4f_f * G3_3d_4f
        + G5_3d_4f_f * G5_3d_4f)

    ldots_4f = NewOperator('ldots', NFermions, IndexUp_4f, IndexDn_4f)

    ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

    zeta_4f_i = $zeta(4f)_i_value * $zeta(4f)_i_scale

    zeta_4f_f = $zeta(4f)_f_value * $zeta(4f)_f_scale
    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scale

    H_i = H_i + Chop(
          zeta_4f_i * ldots_4f)

    H_f = H_f + Chop(
          zeta_4f_f * ldots_4f
        + zeta_3d_f * ldots_3d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_crystal_field == 1 then
    -- PotentialExpandedOnClm('Oh', 3, {Ea2u, Et1u, Et2u})
    -- Ea2u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {1, 0, 0}))
    -- Et2u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 1, 0}))
    -- Et1u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 0, 1}))

    B40_4f_i = $B40(4f)_i_value
    B60_4f_i = $B60(4f)_i_value

    Akm_4f_i = {
        {4,  0, B40_4f_i},
        {4, -4, math.sqrt(5/14) * B40_4f_i},
        {4,  4, math.sqrt(5/14) * B40_4f_i},
        {6,  0, B60_4f_i},
        {6, -4, -math.sqrt(7/2) * B60_4f_i},
        {6,  4, -math.sqrt(7/2) * B60_4f_i},
    }

    io.write('Energies of the 4f orbitals in the initial Hamiltonian (crystal field term only):\n')
    io.write('================\n')
    io.write('Irrep.        E\n')
    io.write('================\n')
    io.write(string.format('a2u     %8.3f\n', -4 / 11 * B40_4f_i +  80 / 143 * B60_4f_i))
    io.write(string.format('t1u     %8.3f\n',  2 / 11 * B40_4f_i + 100 / 429 * B60_4f_i))
    io.write(string.format('t2u     %8.3f\n', -2 / 33 * B40_4f_i -  60 / 143 * B60_4f_i))
    io.write('================\n')
    io.write('\n')

    B40_4f_f = $B40(4f)_f_value
    B60_4f_f = $B60(4f)_f_value

    Akm_4f_f = {
        {4,  0, B40_4f_f},
        {4, -4, math.sqrt(5/14) * B40_4f_f},
        {4,  4, math.sqrt(5/14) * B40_4f_f},
        {6,  0, B60_4f_f},
        {6, -4, -math.sqrt(7/2) * B60_4f_f},
        {6,  4, -math.sqrt(7/2) * B60_4f_f},
    }

    H_i = H_i + Chop(NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_i))

    H_f = H_f + Chop(NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, Akm_4f_f))
end

--------------------------------------------------------------------------------
-- Define the 4f-ligands hybridization term.
--------------------------------------------------------------------------------
if H_4f_ligands_hybridization_lmct == 1 then
    N_L1 = NewOperator('Number', NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1, 1, 1})

    Delta_4f_L1_i = $Delta(4f,L1)_i_value
    e_4f_i = (28 * Delta_4f_L1_i - 27 * U_4f_4f_i * NElectrons_4f - U_4f_4f_i * NElectrons_4f^2) / (2 * (14 + NElectrons_4f))
    e_L1_i = NElectrons_4f * (-2 * Delta_4f_L1_i + U_4f_4f_i * NElectrons_4f + U_4f_4f_i) / (2 * (NElectrons_4f + 14))

    Delta_4f_L1_f = $Delta(4f,L1)_f_value
    e_4f_f = (28 * Delta_4f_L1_f - 460 * U_3d_4f_f - U_4f_4f_f * NElectrons_4f^2 - 47 * U_4f_4f_f * NElectrons_4f) / (2 * (NElectrons_4f + 24))
    e_3d_f = (28 * Delta_4f_L1_f - 2 * U_3d_4f_f * NElectrons_4f^2 - 30 * U_3d_4f_f * NElectrons_4f - 28 * U_3d_4f_f + U_4f_4f_f * NElectrons_4f^2 + U_4f_4f_f * NElectrons_4f) / (2 * (NElectrons_4f + 24))
    e_L1_f = (-2 * Delta_4f_L1_f * NElectrons_4f - 20 * Delta_4f_L1_f + 20 * U_3d_4f_f * NElectrons_4f + 20 * U_3d_4f_f + U_4f_4f_f * NElectrons_4f^2 + U_4f_4f_f * NElectrons_4f) / (2 * (NElectrons_4f + 24))

    H_i = H_i + Chop(
          e_4f_i * N_4f
        + e_L1_i * N_L1)

    H_f = H_f + Chop(
          e_4f_f * N_4f
        + e_3d_f * N_3d
        + e_L1_f * N_L1)

    B40_L1_i = $B40(L1)_i_value
    B60_L1_i = $B60(L1)_i_value

    Akm_L1_i = {
        {4,  0, B40_L1_i},
        {4, -4, math.sqrt(5/14) * B40_L1_i},
        {4,  4, math.sqrt(5/14) * B40_L1_i},
        {6,  0, B60_L1_i},
        {6, -4, -math.sqrt(7/2) * B60_L1_i},
        {6,  4, -math.sqrt(7/2) * B60_L1_i},
    }

    H_i = H_i + Chop(NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_i))

    B40_L1_f = $B40(L1)_f_value
    B60_L1_f = $B60(L1)_f_value

    Akm_L1_f = {
        {4,  0, B40_L1_f},
        {4, -4, math.sqrt(5/14) * B40_L1_f},
        {4,  4, math.sqrt(5/14) * B40_L1_f},
        {6,  0, B60_L1_f},
        {6, -4, -math.sqrt(7/2) * B60_L1_f},
        {6,  4, -math.sqrt(7/2) * B60_L1_f},
    }

    H_f = H_f + Chop(NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_f))

    -- Mixing of the f-orbitals with the ligands.
    Va2u_4f_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {1, 0, 0}))
               + NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Oh', 3, {1, 0, 0}))

    Vt2u_4f_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 1, 0}))
               + NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Oh', 3, {0, 1, 0}))

    Vt1u_4f_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 0, 1}))
               + NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Oh', 3, {0, 0, 1}))

    Va2u_4f_L1_i = $Va2u(4f,L1)_i_value
    Vt2u_4f_L1_i = $Vt2u(4f,L1)_i_value
    Vt1u_4f_L1_i = $Vt1u(4f,L1)_i_value

    Va2u_4f_L1_f = $Va2u(4f,L1)_f_value
    Vt2u_4f_L1_f = $Vt2u(4f,L1)_f_value
    Vt1u_4f_L1_f = $Vt1u(4f,L1)_f_value

    H_i = H_i + Chop(
        Va2u_4f_L1_i * Va2u_4f_L1
      + Vt2u_4f_L1_i * Vt2u_4f_L1
      + Vt1u_4f_L1_i * Vt1u_4f_L1)

    H_f = H_f + Chop(
        Va2u_4f_L1_f * Va2u_4f_L1
      + Vt2u_4f_L1_f * Vt2u_4f_L1
      + Vt1u_4f_L1_f * Vt1u_4f_L1)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4f = NewOperator('Sx', NFermions, IndexUp_4f, IndexDn_4f)
Sy_4f = NewOperator('Sy', NFermions, IndexUp_4f, IndexDn_4f)
Sz_4f = NewOperator('Sz', NFermions, IndexUp_4f, IndexDn_4f)
Ssqr_4f = NewOperator('Ssqr', NFermions, IndexUp_4f, IndexDn_4f)
Splus_4f = NewOperator('Splus', NFermions, IndexUp_4f, IndexDn_4f)
Smin_4f = NewOperator('Smin', NFermions, IndexUp_4f, IndexDn_4f)

Lx_4f = NewOperator('Lx', NFermions, IndexUp_4f, IndexDn_4f)
Ly_4f = NewOperator('Ly', NFermions, IndexUp_4f, IndexDn_4f)
Lz_4f = NewOperator('Lz', NFermions, IndexUp_4f, IndexDn_4f)
Lsqr_4f = NewOperator('Lsqr', NFermions, IndexUp_4f, IndexDn_4f)
Lplus_4f = NewOperator('Lplus', NFermions, IndexUp_4f, IndexDn_4f)
Lmin_4f = NewOperator('Lmin', NFermions, IndexUp_4f, IndexDn_4f)

Jx_4f = NewOperator('Jx', NFermions, IndexUp_4f, IndexDn_4f)
Jy_4f = NewOperator('Jy', NFermions, IndexUp_4f, IndexDn_4f)
Jz_4f = NewOperator('Jz', NFermions, IndexUp_4f, IndexDn_4f)
Jsqr_4f = NewOperator('Jsqr', NFermions, IndexUp_4f, IndexDn_4f)
Jplus_4f = NewOperator('Jplus', NFermions, IndexUp_4f, IndexDn_4f)
Jmin_4f = NewOperator('Jmin', NFermions, IndexUp_4f, IndexDn_4f)

Tx_4f = NewOperator('Tx', NFermions, IndexUp_4f, IndexDn_4f)
Ty_4f = NewOperator('Ty', NFermions, IndexUp_4f, IndexDn_4f)
Tz_4f = NewOperator('Tz', NFermions, IndexUp_4f, IndexDn_4f)

Sx = Sx_4f
Sy = Sy_4f
Sz = Sz_4f

Lx = Lx_4f
Ly = Ly_4f
Lz = Lz_4f

Jx = Jx_4f
Jy = Jy_4f
Jz = Jz_4f

Tx = Tx_4f
Ty = Ty_4f
Tz = Tz_4f

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if H_magnetic_field == 1 then
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if H_exchange_field == 1 then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end

NConfigurations = $NConfigurations

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_3d, NElectrons_3d},
                                           {'0000000000 11111111111111', NElectrons_4f, NElectrons_4f}}

FinalRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_3d - 1, NElectrons_3d - 1},
                                         {'0000000000 11111111111111', NElectrons_4f, NElectrons_4f}}

if H_4f_ligands_hybridization_lmct == 1 then
    InitialRestrictions = {NFermions, NBosons, {'1111111111 00000000000000 00000000000000', NElectrons_3d, NElectrons_3d},
                                               {'0000000000 11111111111111 00000000000000', NElectrons_4f, NElectrons_4f},
                                               {'0000000000 00000000000000 11111111111111', NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {'1111111111 00000000000000 00000000000000', NElectrons_3d - 1, NElectrons_3d - 1},
                                             {'0000000000 11111111111111 00000000000000', NElectrons_4f, NElectrons_4f},
                                             {'0000000000 00000000000000 11111111111111', NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {'0000000000 00000000000000 11111111111111', NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

T = $T * EnergyUnits.Kelvin.value

-- Approximate machine epsilon for single precision arithmetics.
epsilon = 1.19e-07

NPsis = $NPsis
NPsisAuto = $NPsisAuto

dZ = {}

if NPsisAuto == 1 and NPsis ~= 1 then
    NPsis = 4
    NPsisIncrement = 8
    NPsisIsConverged = false

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

        Z = 0

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
        E_gs_i = Psis_i[1] * H_i * Psis_i[1]

    Z = 0

    for i, Psi in ipairs(Psis_i) do
        E = Psi * H_i * Psi

        if math.abs(E - E_gs_i) < epsilon then
            dZ[i] = 1
        else
            dZ[i] = math.exp(-(E - E_gs_i) / T)
        end

        Z = Z + dZ[i]
    end
end

-- Normalize dZ to unity.
for i in ipairs(dZ) do
    dZ[i] = dZ[i] / Z
end

--------------------------------------------------------------------------------
-- Define some helper function for the spectra calculation.
--------------------------------------------------------------------------------
function ValueInTable(value, table)
    -- Check if a value is in a table.
    for k, v in ipairs(table) do
        if value == v then
            return true
        end
    end
    return false
end

function GetSpectrum(G, T, Psis, indices, dZSpectra)
    -- Extract the spectra corresponding to the operators identified
    -- using the indices argument. The returned spectrum is a weighted
    -- sum, where the weights are the Boltzmann probabilities.
    if not (type(indices) == 'table') then
        indices = {indices}
    end

    c = 1
    dZSpectrum = {}

    for i in ipairs(T) do
        for k in ipairs(Psis) do
            if ValueInTable(i, indices) then
                table.insert(dZSpectrum, dZSpectra[c])
            else
                table.insert(dZSpectrum, 0)
            end
            c = c + 1
        end
    end

    return Spectra.Sum(G, dZSpectrum)
end

function SaveSpectrum(G, suffix)
    -- Scale, broaden, and save the spectrum to disk.
    G = -1 / math.pi * G

    Gmin1 = $Gmin1 - Gamma
    Gmax1 = $Gmax1 - Gamma
    Egamma1 = ($Egamma1 - Eedge1) + DeltaE
    G.Broaden(0, {{Emin, Gmin1}, {Egamma1, Gmin1}, {Egamma1, Gmax1}, {Emax, Gmax1}})

    G.Print({{'file', '$BaseName_' .. suffix .. '.spec'}})
end

--------------------------------------------------------------------------------
-- Define the transition operators.
--------------------------------------------------------------------------------
T_3d = {}
for i = 1, NElectrons_3d / 2 do
    T_3d[2*i - 1] = NewOperator('An', NFermions, IndexDn_3d[i])
    T_3d[2*i]     = NewOperator('An', NFermions, IndexUp_3d[i])
end

k = $k1

-- List with the user selected spectra.
spectra = {$spectra}

indices_3d = {}
c = 1

spectrum = 'Isotropic'
if ValueInTable(spectrum, spectra) then
    indices_3d[spectrum] = {}
    for j, operator in ipairs(T_3d) do
        table.insert(indices_3d[spectrum], c)
        c = c + 1
    end
end

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
Sk = Chop(k[1] * Sx + k[2] * Sy + k[3] * Sz)
Lk = Chop(k[1] * Lx + k[2] * Ly + k[3] * Lz)
Jk = Chop(k[1] * Jx + k[2] * Jy + k[3] * Jz)
Tk = Chop(k[1] * Tx + k[2] * Ty + k[3] * Tz)

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4f, N_3d, N_4f, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=================================================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3d>    <N_4f>          dZ\n'
header = header .. '=================================================================================================================================\n'
footer = '=================================================================================================================================\n'

if H_4f_ligands_hybridization_lmct == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4f, N_3d, N_4f, N_L1, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '===========================================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3d>    <N_4f>    <N_L1>          dZ\n'
    header = header .. '===========================================================================================================================================\n'
    footer = '===========================================================================================================================================\n'
end

io.write(header)
for i, Psi in ipairs(Psis_i) do
    io.write(string.format('%5d', i))
    for j, Operator in ipairs(Operators) do
        if j == 1 then
            io.write(string.format('%12.6f', Complex.Re(Psi * Operator * Psi)))
        elseif Operator == 'dZ' then
            io.write(string.format('%12.2E', dZ[i]))
        else
            io.write(string.format('%10.4f', Complex.Re(Psi * Operator * Psi)))
        end
    end
    io.write('\n')
end
io.write(footer)


if next(spectra) == nil then
    return
end

E_gs_i = Psis_i[1] * H_i * Psis_i[1]

if CalculationRestrictions == nil then
    Psis_f = Eigensystem(H_f, FinalRestrictions, 1)
else
    Psis_f = Eigensystem(H_f, FinalRestrictions, 1, {{'restrictions', CalculationRestrictions}})
end

Psis_f = {Psis_f}
E_gs_f = Psis_f[1] * H_f * Psis_f[1]

Eedge1 = $Eedge1
DeltaE = E_gs_f - E_gs_i

Emin = ($Emin1 - Eedge1) + DeltaE
Emax = ($Emax1 - Eedge1) + DeltaE
NE = $NE1
Gamma = $Gamma1
DenseBorder = $DenseBorder

if CalculationRestrictions == nil then
    G_3d = CreateSpectra(H_f, T_3d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'DenseBorder', DenseBorder}})
else
    G_3d = CreateSpectra(H_f, T_3d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}, {'DenseBorder', DenseBorder}})
end

-- Create a list with the Boltzmann probabilities for a given operator
-- and state.
dZ_3d = {}
for i in ipairs(T_3d) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_3d, dZ[j])
    end
end

spectrum = 'Isotropic'
if ValueInTable(spectrum, spectra) then
    Giso = GetSpectrum(G_3d, T_3d, Psis_i, indices_3d[spectrum], dZ_3d)
    SaveSpectrum(Giso / #T_3d, 'iso')
end

