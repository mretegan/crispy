--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 4d
-- symmetry: Td
-- experiment: XAS
-- edge: M2,3 (3p)
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
H_4d_ligands_hybridization_lmct = $H_4d_ligands_hybridization_lmct
H_4d_ligands_hybridization_mlct = $H_4d_ligands_hybridization_mlct
H_magnetic_field = $H_magnetic_field
H_exchange_field = $H_exchange_field

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_3p = 6
NElectrons_4d = $NElectrons_4d

IndexDn_3p = {0, 2, 4}
IndexUp_3p = {1, 3, 5}
IndexDn_4d = {6, 8, 10, 12, 14}
IndexUp_4d = {7, 9, 11, 13, 15}

if H_4d_ligands_hybridization_lmct == 1 then
    NFermions = 26

    NElectrons_L1 = 10

    IndexDn_L1 = {16, 18, 20, 22, 24}
    IndexUp_L1 = {17, 19, 21, 23, 25}
end

if H_4d_ligands_hybridization_mlct == 1 then
    NFermions = 26

    NElectrons_L2 = 0

    IndexDn_L2 = {16, 18, 20, 22, 24}
    IndexUp_L2 = {17, 19, 21, 23, 25}
end

if H_4d_ligands_hybridization_lmct == 1 and H_4d_ligands_hybridization_mlct == 1 then
    return
end

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_3p = NewOperator('Number', NFermions, IndexUp_3p, IndexUp_3p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3p, IndexDn_3p, {1, 1, 1})

N_4d = NewOperator('Number', NFermions, IndexUp_4d, IndexUp_4d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_4d, IndexDn_4d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_4d_4d = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, {1, 0, 0})
    F2_4d_4d = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, {0, 1, 0})
    F4_4d_4d = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, {0, 0, 1})

    F0_3p_4d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {1, 0}, {0, 0})
    F2_3p_4d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {0, 1}, {0, 0})
    G1_3p_4d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {0, 0}, {1, 0})
    G3_3p_4d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_4d, IndexDn_4d, {0, 0}, {0, 1})

    U_4d_4d_i = $U(4d,4d)_i_value
    F2_4d_4d_i = $F2(4d,4d)_i_value * $F2(4d,4d)_i_scale
    F4_4d_4d_i = $F4(4d,4d)_i_value * $F4(4d,4d)_i_scale
    F0_4d_4d_i = U_4d_4d_i + 2 / 63 * F2_4d_4d_i + 2 / 63 * F4_4d_4d_i

    U_4d_4d_f = $U(4d,4d)_f_value
    F2_4d_4d_f = $F2(4d,4d)_f_value * $F2(4d,4d)_f_scale
    F4_4d_4d_f = $F4(4d,4d)_f_value * $F4(4d,4d)_f_scale
    F0_4d_4d_f = U_4d_4d_f + 2 / 63 * F2_4d_4d_f + 2 / 63 * F4_4d_4d_f
    U_3p_4d_f = $U(3p,4d)_f_value
    F2_3p_4d_f = $F2(3p,4d)_f_value * $F2(3p,4d)_f_scale
    G1_3p_4d_f = $G1(3p,4d)_f_value * $G1(3p,4d)_f_scale
    G3_3p_4d_f = $G3(3p,4d)_f_value * $G3(3p,4d)_f_scale
    F0_3p_4d_f = U_3p_4d_f + 1 / 15 * G1_3p_4d_f + 3 / 70 * G3_3p_4d_f

    H_i = H_i + Chop(
          F0_4d_4d_i * F0_4d_4d
        + F2_4d_4d_i * F2_4d_4d
        + F4_4d_4d_i * F4_4d_4d)

    H_f = H_f + Chop(
          F0_4d_4d_f * F0_4d_4d
        + F2_4d_4d_f * F2_4d_4d
        + F4_4d_4d_f * F4_4d_4d
        + F0_3p_4d_f * F0_3p_4d
        + F2_3p_4d_f * F2_3p_4d
        + G1_3p_4d_f * G1_3p_4d
        + G3_3p_4d_f * G3_3p_4d)

    ldots_4d = NewOperator('ldots', NFermions, IndexUp_4d, IndexDn_4d)

    ldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

    zeta_4d_i = $zeta(4d)_i_value * $zeta(4d)_i_scale

    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scale
    zeta_3p_f = $zeta(3p)_f_value * $zeta(3p)_f_scale

    H_i = H_i + Chop(
          zeta_4d_i * ldots_4d)

    H_f = H_f + Chop(
          zeta_4d_f * ldots_4d
        + zeta_3p_f * ldots_3p)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_crystal_field == 1 then
    -- PotentialExpandedOnClm('Td', 2, {Ee, Et2})
    -- tenDq_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Akm = {{4, 0, -2.1}, {4, -4, -1.5 * sqrt(0.7)}, {4, 4, -1.5 * sqrt(0.7)}}
    tenDq_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, Akm)

    tenDq_4d_i = $10Dq(4d)_i_value

    io.write('Energies of the 4d orbitals in the initial Hamiltonian (crystal field term only):\n')
    io.write('================\n')
    io.write('Irrep.         E\n')
    io.write('================\n')
    io.write(string.format('e       %8.3f\n', -0.6 * tenDq_4d_i))
    io.write(string.format('t2      %8.3f\n',  0.4 * tenDq_4d_i))
    io.write('================\n')
    io.write('\n')

    tenDq_4d_f = $10Dq(4d)_f_value

    H_i = H_i + Chop(
          tenDq_4d_i * tenDq_4d)

    H_f = H_f + Chop(
          tenDq_4d_f * tenDq_4d)
end

--------------------------------------------------------------------------------
-- Define the 4d-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if H_4d_ligands_hybridization_lmct == 1 then
    N_L1 = NewOperator('Number', NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_4d_L1_i = $Delta(4d,L1)_i_value
    e_4d_i = (10 * Delta_4d_L1_i - NElectrons_4d * (19 + NElectrons_4d) * U_4d_4d_i / 2) / (10 + NElectrons_4d)
    e_L1_i = NElectrons_4d * ((1 + NElectrons_4d) * U_4d_4d_i / 2 - Delta_4d_L1_i) / (10 + NElectrons_4d)

    Delta_4d_L1_f = $Delta(4d,L1)_f_value
    e_4d_f = (10 * Delta_4d_L1_f - NElectrons_4d * (31 + NElectrons_4d) * U_4d_4d_f / 2 - 90 * U_3p_4d_f) / (16 + NElectrons_4d)
    e_3p_f = (10 * Delta_4d_L1_f + (1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 - (10 + NElectrons_4d) * U_3p_4d_f)) / (16 + NElectrons_4d)
    e_L1_f = ((1 + NElectrons_4d) * (NElectrons_4d * U_4d_4d_f / 2 + 6 * U_3p_4d_f) - (6 + NElectrons_4d) * Delta_4d_L1_f) / (16 + NElectrons_4d)

    H_i = H_i + Chop(
          e_4d_i * N_4d
        + e_L1_i * N_L1)

    H_f = H_f + Chop(
          e_4d_f * N_4d
        + e_3p_f * N_3p
        + e_L1_f * N_L1)

    tenDq_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Ve_4d_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Td', 2, {1, 0}))
             + NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Td', 2, {1, 0}))

    Vt2_4d_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Td', 2, {0, 1}))
              + NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Td', 2, {0, 1}))

    tenDq_L1_i = $10Dq(L1)_i_value
    Ve_4d_L1_i = $Ve(4d,L1)_i_value
    Vt2_4d_L1_i = $Vt2(4d,L1)_i_value

    tenDq_L1_f = $10Dq(L1)_f_value
    Ve_4d_L1_f = $Ve(4d,L1)_f_value
    Vt2_4d_L1_f = $Vt2(4d,L1)_f_value

    H_i = H_i + Chop(
          tenDq_L1_i * tenDq_L1
        + Ve_4d_L1_i * Ve_4d_L1
        + Vt2_4d_L1_i * Vt2_4d_L1)

    H_f = H_f + Chop(
          tenDq_L1_f * tenDq_L1
        + Ve_4d_L1_f * Ve_4d_L1
        + Vt2_4d_L1_f * Vt2_4d_L1)
end
--------------------------------------------------------------------------------
-- Define the 4d-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if H_4d_ligands_hybridization_mlct == 1 then
    N_L2 = NewOperator('Number', NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_4d_L2_i = $Delta(4d,L2)_i_value
    e_4d_i = U_4d_4d_i * (-NElectrons_4d + 1) / 2
    e_L2_i = Delta_4d_L2_i - U_4d_4d_i * NElectrons_4d / 2 - U_4d_4d_i / 2

    Delta_4d_L2_f = $Delta(4d,L2)_f_value
    e_4d_f = -(U_4d_4d_f * NElectrons_4d^2 + 11 * U_4d_4d_f * NElectrons_4d + 60 * U_3p_4d_f) / (2 * NElectrons_4d + 12)
    e_3p_f = NElectrons_4d * (U_4d_4d_f * NElectrons_4d + U_4d_4d_f - 2 * U_3p_4d_f * NElectrons_4d - 2 * U_3p_4d_f) / (2 * (NElectrons_4d + 6))
    e_L2_f = (2 * Delta_4d_L2_f * NElectrons_4d + 12 * Delta_4d_L2_f - U_4d_4d_f * NElectrons_4d^2 - U_4d_4d_f * NElectrons_4d - 12 * U_3p_4d_f * NElectrons_4d - 12 * U_3p_4d_f) / (2 * (NElectrons_4d + 6))

    H_i = H_i + Chop(
          e_4d_i * N_4d
        + e_L2_i * N_L2)

    H_f = H_f + Chop(
          e_4d_f * N_4d
        + e_3p_f * N_3p
        + e_L2_f * N_L2)

    tenDq_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Ve_4d_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Td', 2, {1, 0}))
             + NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Td', 2, {1, 0}))

    Vt2_4d_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, IndexUp_4d, IndexDn_4d, PotentialExpandedOnClm('Td', 2, {0, 1}))
              + NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Td', 2, {0, 1}))

    tenDq_L2_i = $10Dq(L2)_i_value
    Ve_4d_L2_i = $Ve(4d,L2)_i_value
    Vt2_4d_L2_i = $Vt2(4d,L2)_i_value

    tenDq_L2_f = $10Dq(L2)_f_value
    Ve_4d_L2_f = $Ve(4d,L2)_f_value
    Vt2_4d_L2_f = $Vt2(4d,L2)_f_value

    H_i = H_i + Chop(
          tenDq_L2_i * tenDq_L2
        + Ve_4d_L2_i * Ve_4d_L2
        + Vt2_4d_L2_i * Vt2_4d_L2)

    H_f = H_f + Chop(
          tenDq_L2_f * tenDq_L2
        + Ve_4d_L2_f * Ve_4d_L2
        + Vt2_4d_L2_f * Vt2_4d_L2)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4d = NewOperator('Sx', NFermions, IndexUp_4d, IndexDn_4d)
Sy_4d = NewOperator('Sy', NFermions, IndexUp_4d, IndexDn_4d)
Sz_4d = NewOperator('Sz', NFermions, IndexUp_4d, IndexDn_4d)
Ssqr_4d = NewOperator('Ssqr', NFermions, IndexUp_4d, IndexDn_4d)
Splus_4d = NewOperator('Splus', NFermions, IndexUp_4d, IndexDn_4d)
Smin_4d = NewOperator('Smin', NFermions, IndexUp_4d, IndexDn_4d)

Lx_4d = NewOperator('Lx', NFermions, IndexUp_4d, IndexDn_4d)
Ly_4d = NewOperator('Ly', NFermions, IndexUp_4d, IndexDn_4d)
Lz_4d = NewOperator('Lz', NFermions, IndexUp_4d, IndexDn_4d)
Lsqr_4d = NewOperator('Lsqr', NFermions, IndexUp_4d, IndexDn_4d)
Lplus_4d = NewOperator('Lplus', NFermions, IndexUp_4d, IndexDn_4d)
Lmin_4d = NewOperator('Lmin', NFermions, IndexUp_4d, IndexDn_4d)

Jx_4d = NewOperator('Jx', NFermions, IndexUp_4d, IndexDn_4d)
Jy_4d = NewOperator('Jy', NFermions, IndexUp_4d, IndexDn_4d)
Jz_4d = NewOperator('Jz', NFermions, IndexUp_4d, IndexDn_4d)
Jsqr_4d = NewOperator('Jsqr', NFermions, IndexUp_4d, IndexDn_4d)
Jplus_4d = NewOperator('Jplus', NFermions, IndexUp_4d, IndexDn_4d)
Jmin_4d = NewOperator('Jmin', NFermions, IndexUp_4d, IndexDn_4d)

Tx_4d = NewOperator('Tx', NFermions, IndexUp_4d, IndexDn_4d)
Ty_4d = NewOperator('Ty', NFermions, IndexUp_4d, IndexDn_4d)
Tz_4d = NewOperator('Tz', NFermions, IndexUp_4d, IndexDn_4d)

Sx = Sx_4d
Sy = Sy_4d
Sz = Sz_4d

Lx = Lx_4d
Ly = Ly_4d
Lz = Lz_4d

Jx = Jx_4d
Jy = Jy_4d
Jz = Jz_4d

Tx = Tx_4d
Ty = Ty_4d
Tz = Tz_4d

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
InitialRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p, NElectrons_3p},
                                           {'000000 1111111111', NElectrons_4d, NElectrons_4d}}

FinalRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p - 1, NElectrons_3p - 1},
                                         {'000000 1111111111', NElectrons_4d + 1, NElectrons_4d + 1}}

if H_4d_ligands_hybridization_lmct == 1 then
    InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_3p, NElectrons_3p},
                                               {'000000 1111111111 0000000000', NElectrons_4d, NElectrons_4d},
                                               {'000000 0000000000 1111111111', NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_3p - 1, NElectrons_3p - 1},
                                             {'000000 1111111111 0000000000', NElectrons_4d + 1, NElectrons_4d + 1},
                                             {'000000 0000000000 1111111111', NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {'000000 0000000000 1111111111', NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

if H_4d_ligands_hybridization_mlct == 1 then
    InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_3p, NElectrons_3p},
                                               {'000000 1111111111 0000000000', NElectrons_4d, NElectrons_4d},
                                               {'000000 0000000000 1111111111', NElectrons_L2, NElectrons_L2}}

    FinalRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_3p - 1, NElectrons_3p - 1},
                                             {'000000 1111111111 0000000000', NElectrons_4d + 1, NElectrons_4d + 1},
                                             {'000000 0000000000 1111111111', NElectrons_L2, NElectrons_L2}}

    CalculationRestrictions = {NFermions, NBosons, {'000000 0000000000 1111111111', NElectrons_L2, NElectrons_L2 + (NConfigurations - 1)}}
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
t = math.sqrt(1/2)

Tx_3p_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_3p, IndexDn_3p, {{1, -1, t    }, {1, 1, -t    }})
Ty_3p_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_3p, IndexDn_3p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_3p_4d = NewOperator('CF', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_3p, IndexDn_3p, {{1,  0, 1    }                })

k = $k1
ev = $eps11
eh = $eps12

-- Calculate the right and left polarization vectors.
er = {t * (eh[1] - I * ev[1]),
      t * (eh[2] - I * ev[2]),
      t * (eh[3] - I * ev[3])}

el = {-t * (eh[1] + I * ev[1]),
      -t * (eh[2] + I * ev[2]),
      -t * (eh[3] + I * ev[3])}

function CalculateT(e)
    -- Calculate the transition operator for arbitrary polarization.
    T = e[1] * Tx_3p_4d + e[2] * Ty_3p_4d + e[3] * Tz_3p_4d
    return Chop(T)
end

Tv_3p_4d = CalculateT(ev)
Th_3p_4d = CalculateT(eh)
Tr_3p_4d = CalculateT(er)
Tl_3p_4d = CalculateT(el)
Tk_3p_4d = CalculateT(k)

-- List with the user selected spectra.
spectra = {$spectra}

-- Create two lists, one with the operators and the second with
-- the indices of the operators required to calculate a given
-- spectrum.
T_3p_4d = {}
indices_3p_4d = {}
c = 1

spectrum = 'Isotropic'
if ValueInTable(spectrum, spectra) then
    indices_3p_4d[spectrum] = {}
    for j, operator in ipairs({Tr_3p_4d, Tl_3p_4d, Tk_3p_4d}) do
        table.insert(T_3p_4d, operator)
        table.insert(indices_3p_4d[spectrum], c)
        c = c + 1
    end
end

spectrum = 'Circular Dichroism'
if ValueInTable(spectrum, spectra) then
    indices_3p_4d[spectrum] = {}
    if ValueInTable('Isotropic', spectra) then
        table.insert(indices_3p_4d[spectrum], 1)
        table.insert(indices_3p_4d[spectrum], 2)
    else
        for j, operator in ipairs({Tr_3p_4d, Tl_3p_4d}) do
            table.insert(T_3p_4d, operator)
            table.insert(indices_3p_4d[spectrum], c)
            c = c + 1
        end
    end
end

spectrum = 'Linear Dichroism'
if ValueInTable(spectrum, spectra) then
    indices_3p_4d[spectrum] = {}
    for j, operator in ipairs({Tv_3p_4d, Th_3p_4d}) do
        table.insert(T_3p_4d, operator)
        table.insert(indices_3p_4d[spectrum], c)
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

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_3p, N_4d, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=================================================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3p>    <N_4d>          dZ\n'
header = header .. '=================================================================================================================================\n'
footer = '=================================================================================================================================\n'

if H_4d_ligands_hybridization_lmct == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_3p, N_4d, N_L1, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '===========================================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3p>    <N_4d>    <N_L1>          dZ\n'
    header = header .. '===========================================================================================================================================\n'
    footer = '===========================================================================================================================================\n'
end

if H_4d_ligands_hybridization_mlct == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_4d, N_3p, N_4d, N_L2, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '===========================================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_3p>    <N_4d>    <N_L2>          dZ\n'
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
    G_3p_4d = CreateSpectra(H_f, T_3p_4d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'DenseBorder', DenseBorder}})
else
    G_3p_4d = CreateSpectra(H_f, T_3p_4d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}, {'DenseBorder', DenseBorder}})
end

-- Create a list with the Boltzmann probabilities for a given operator
-- and state.
dZ_3p_4d = {}
for i in ipairs(T_3p_4d) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_3p_4d, dZ[j])
    end
end

Pcl_3p_4d = 2

spectrum = 'Isotropic'
if ValueInTable(spectrum, spectra) then
    Giso = GetSpectrum(G_3p_4d, T_3p_4d, Psis_i, indices_3p_4d[spectrum], dZ_3p_4d)
    Giso = Giso / 3 / Pcl_3p_4d
    SaveSpectrum(Giso, 'iso')
end

spectrum = 'Circular Dichroism'
if ValueInTable(spectrum, spectra) then
    Gr = GetSpectrum(G_3p_4d, T_3p_4d, Psis_i, indices_3p_4d[spectrum][1], dZ_3p_4d)
    Gl = GetSpectrum(G_3p_4d, T_3p_4d, Psis_i, indices_3p_4d[spectrum][2], dZ_3p_4d)
    Gr = Gr / Pcl_3p_4d
    Gl = Gl / Pcl_3p_4d
    SaveSpectrum(Gr, 'r')
    SaveSpectrum(Gl, 'l')
    SaveSpectrum(Gr - Gl, 'cd')
end

spectrum = 'Linear Dichroism'
if ValueInTable(spectrum, spectra) then
    Gv = GetSpectrum(G_3p_4d, T_3p_4d, Psis_i, indices_3p_4d[spectrum][1], dZ_3p_4d)
    Gh = GetSpectrum(G_3p_4d, T_3p_4d, Psis_i, indices_3p_4d[spectrum][2], dZ_3p_4d)
    Gv = Gv / Pcl_3p_4d
    Gh = Gh / Pcl_3p_4d
    SaveSpectrum(Gv, 'v')
    SaveSpectrum(Gh, 'h')
    SaveSpectrum(Gv - Gh, 'ld')
end

