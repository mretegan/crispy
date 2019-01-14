--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 5d
-- symmetry: Td
-- experiment: RIXS
-- edge: L2,3-O4,5 (2p5d)
--------------------------------------------------------------------------------
Verbosity($Verbosity)

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
H_crystal_field = $H_crystal_field
H_5d_ligands_hybridization_lmct = $H_5d_ligands_hybridization_lmct
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

if H_5d_ligands_hybridization_lmct == 1 then
    NFermions = 26

    NElectrons_L1 = 10

    IndexDn_L1 = {16, 18, 20, 22, 24}
    IndexUp_L1 = {17, 19, 21, 23, 25}
end

if H_5d_ligands_hybridization_mlct == 1 then
    NFermions = 26

    NElectrons_L2 = 10

    IndexDn_L2 = {16, 18, 20, 22, 24}
    IndexUp_L2 = {17, 19, 21, 23, 25}
end

if H_5d_ligands_hybridization_lmct == 1 and H_5d_ligands_hybridization_mlct == 1 then
    return
end

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

    U_5d_5d_i = $U(5d,5d)_i_value
    F2_5d_5d_i = $F2(5d,5d)_i_value * $F2(5d,5d)_i_scale
    F4_5d_5d_i = $F4(5d,5d)_i_value * $F4(5d,5d)_i_scale
    F0_5d_5d_i = U_5d_5d_i + 2 / 63 * F2_5d_5d_i + 2 / 63 * F4_5d_5d_i

    U_5d_5d_m = $U(5d,5d)_m_value
    F2_5d_5d_m = $F2(5d,5d)_m_value * $F2(5d,5d)_m_scale
    F4_5d_5d_m = $F4(5d,5d)_m_value * $F4(5d,5d)_m_scale
    F0_5d_5d_m = U_5d_5d_m + 2 / 63 * F2_5d_5d_m + 2 / 63 * F4_5d_5d_m
    U_2p_5d_m = $U(2p,5d)_m_value
    F2_2p_5d_m = $F2(2p,5d)_m_value * $F2(2p,5d)_m_scale
    G1_2p_5d_m = $G1(2p,5d)_m_value * $G1(2p,5d)_m_scale
    G3_2p_5d_m = $G3(2p,5d)_m_value * $G3(2p,5d)_m_scale
    F0_2p_5d_m = U_2p_5d_m + 1 / 15 * G1_2p_5d_m + 3 / 70 * G3_2p_5d_m

    U_5d_5d_f = $U(5d,5d)_f_value
    F2_5d_5d_f = $F2(5d,5d)_f_value * $F2(5d,5d)_f_scale
    F4_5d_5d_f = $F4(5d,5d)_f_value * $F4(5d,5d)_f_scale
    F0_5d_5d_f = U_5d_5d_f + 2 / 63 * F2_5d_5d_f + 2 / 63 * F4_5d_5d_f

    H_i = H_i + Chop(
          F0_5d_5d_i * F0_5d_5d
        + F2_5d_5d_i * F2_5d_5d
        + F4_5d_5d_i * F4_5d_5d)

    H_m = H_m + Chop(
          F0_5d_5d_m * F0_5d_5d
        + F2_5d_5d_m * F2_5d_5d
        + F4_5d_5d_m * F4_5d_5d
        + F0_2p_5d_m * F0_2p_5d
        + F2_2p_5d_m * F2_2p_5d
        + G1_2p_5d_m * G1_2p_5d
        + G3_2p_5d_m * G3_2p_5d)

    H_f = H_f + Chop(
          F0_5d_5d_f * F0_5d_5d
        + F2_5d_5d_f * F2_5d_5d
        + F4_5d_5d_f * F4_5d_5d)

    ldots_5d = NewOperator('ldots', NFermions, IndexUp_5d, IndexDn_5d)

    ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

    zeta_5d_i = $zeta(5d)_i_value * $zeta(5d)_i_scale

    zeta_5d_m = $zeta(5d)_m_value * $zeta(5d)_m_scale
    zeta_2p_m = $zeta(2p)_m_value * $zeta(2p)_m_scale

    zeta_5d_f = $zeta(5d)_f_value * $zeta(5d)_f_scale

    H_i = H_i + Chop(
          zeta_5d_i * ldots_5d)

    H_m = H_m + Chop(
          zeta_5d_m * ldots_5d
        + zeta_2p_m * ldots_2p)

    H_f = H_f + Chop(
          zeta_5d_f * ldots_5d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_crystal_field == 1 then
    -- PotentialExpandedOnClm('Td', 2, {Ee, Et2})
    -- tenDq_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Akm = {{4, 0, -2.1}, {4, -4, -1.5 * sqrt(0.7)}, {4, 4, -1.5 * sqrt(0.7)}}
    tenDq_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, Akm)

    tenDq_5d_i = $10Dq(5d)_i_value

    io.write('Energies of the 5d orbitals in the initial Hamiltonian (crystal field term only):\n')
    io.write('================\n')
    io.write('Irrep.         E\n')
    io.write('================\n')
    io.write(string.format('e       %8.3f\n', -0.6 * tenDq_5d_i))
    io.write(string.format('t2      %8.3f\n',  0.4 * tenDq_5d_i))
    io.write('================\n')
    io.write('\n')

    tenDq_5d_m = $10Dq(5d)_m_value

    tenDq_5d_f = $10Dq(5d)_f_value

    H_i = H_i + Chop(
          tenDq_5d_i * tenDq_5d)

    H_m = H_m + Chop(
          tenDq_5d_m * tenDq_5d)

    H_f = H_f + Chop(
          tenDq_5d_f * tenDq_5d)
end

--------------------------------------------------------------------------------
-- Define the 5d-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if H_5d_ligands_hybridization_lmct == 1 then
    N_L1 = NewOperator('Number', NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_5d_L1_i = $Delta(5d,L1)_i_value
    e_5d_i = (10 * Delta_5d_L1_i - NElectrons_5d * (19 + NElectrons_5d) * U_5d_5d_i / 2) / (10 + NElectrons_5d)
    e_L1_i = NElectrons_5d * ((1 + NElectrons_5d) * U_5d_5d_i / 2 - Delta_5d_L1_i) / (10 + NElectrons_5d)

    Delta_5d_L1_m = $Delta(5d,L1)_m_value
    e_5d_m = (10 * Delta_5d_L1_m - NElectrons_5d * (31 + NElectrons_5d) * U_5d_5d_m / 2 - 90 * U_2p_5d_m) / (16 + NElectrons_5d)
    e_2p_m = (10 * Delta_5d_L1_m + (1 + NElectrons_5d) * (NElectrons_5d * U_5d_5d_m / 2 - (10 + NElectrons_5d) * U_2p_5d_m)) / (16 + NElectrons_5d)
    e_L1_m = ((1 + NElectrons_5d) * (NElectrons_5d * U_5d_5d_m / 2 + 6 * U_2p_5d_m) - (6 + NElectrons_5d) * Delta_5d_L1_m) / (16 + NElectrons_5d)

    Delta_5d_L1_f = $Delta(5d,L1)_f_value
    e_5d_f = (10 * Delta_5d_L1_f - NElectrons_5d * (19 + NElectrons_5d) * U_5d_5d_f / 2) / (10 + NElectrons_5d)
    e_L1_f = NElectrons_5d * ((1 + NElectrons_5d) * U_5d_5d_f / 2 - Delta_5d_L1_f) / (10 + NElectrons_5d)

    H_i = H_i + Chop(
          e_5d_i * N_5d
        + e_L1_i * N_L1)

    H_m = H_m + Chop(
          e_5d_m * N_5d
        + e_2p_m * N_2p
        + e_L1_m * N_L1)

    H_f = H_f + Chop(
          e_5d_f * N_5d
        + e_L1_f * N_L1)

    tenDq_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Ve_5d_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {1, 0}))
             + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Td', 2, {1, 0}))

    Vt2_5d_L1 = NewOperator('CF', NFermions, IndexUp_L1, IndexDn_L1, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {0, 1}))
              + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm('Td', 2, {0, 1}))

    tenDq_L1_i = $10Dq(L1)_i_value
    Ve_5d_L1_i = $Ve(5d,L1)_i_value
    Vt2_5d_L1_i = $Vt2(5d,L1)_i_value

    tenDq_L1_m = $10Dq(L1)_m_value
    Ve_5d_L1_m = $Ve(5d,L1)_m_value
    Vt2_5d_L1_m = $Vt2(5d,L1)_m_value

    tenDq_L1_f = $10Dq(L1)_f_value
    Ve_5d_L1_f = $Ve(5d,L1)_f_value
    Vt2_5d_L1_f = $Vt2(5d,L1)_f_value

    H_i = H_i + Chop(
          tenDq_L1_i * tenDq_L1
        + Ve_5d_L1_i * Ve_5d_L1
        + Vt2_5d_L1_i * Vt2_5d_L1)

    H_m = H_m + Chop(
          tenDq_L1_m * tenDq_L1
        + Ve_5d_L1_m * Ve_5d_L1
        + Vt2_5d_L1_m * Vt2_5d_L1)

    H_f = H_f + Chop(
          tenDq_L1_f * tenDq_L1
        + Ve_5d_L1_f * Ve_5d_L1
        + Vt2_5d_L1_f * Vt2_5d_L1)
end

--------------------------------------------------------------------------------
-- Define the 5d-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if H_5d_ligands_hybridization_mlct == 1 then
    N_L2 = NewOperator('Number', NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_5d_L2_i = $Delta(5d,L2)_i_value
    e_5d_i = U_5d_5d_i * (-NElectrons_5d + 1) / 2
    e_L2_i = Delta_5d_L2_i - U_5d_5d_i * NElectrons_5d / 2 - U_5d_5d_i / 2

    Delta_5d_L2_m = $Delta(5d,L2)_m_value
    e_5d_m = -(U_5d_5d_m * NElectrons_5d^2 + 11 * U_5d_5d_m * NElectrons_5d + 60 * U_2p_5d_m) / (2 * NElectrons_5d + 12)
    e_2p_m = NElectrons_5d * (U_5d_5d_m * NElectrons_5d + U_5d_5d_m - 2 * U_2p_5d_m * NElectrons_5d - 2 * U_2p_5d_m) / (2 * (NElectrons_5d + 6))
    e_L2_m = (2 * Delta_5d_L2_m * NElectrons_5d + 12 * Delta_5d_L2_m - U_5d_5d_m * NElectrons_5d^2 - U_5d_5d_m * NElectrons_5d - 12 * U_2p_5d_m * NElectrons_5d - 12 * U_2p_5d_m) / (2 * (NElectrons_5d + 6))

    Delta_5d_L2_f = $Delta(5d,L2)_f_value
    e_5d_f = U_5d_5d_f * (-NElectrons_5d + 1) / 2
    e_L2_f = Delta_5d_L2_f - U_5d_5d_f * NElectrons_5d / 2 - U_5d_5d_f / 2

    H_i = H_i + Chop(
          e_5d_i * N_5d
        + e_L2_i * N_L2)

    H_m = H_m + Chop(
          e_5d_m * N_5d
        + e_2p_m * N_2p
        + e_L2_m * N_L2)

    H_f = H_f + Chop(
          e_5d_f * N_5d
        + e_L2_f * N_L2)

    tenDq_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Ve_5d_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {1, 0}))
             + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Td', 2, {1, 0}))

    Vt2_5d_L2 = NewOperator('CF', NFermions, IndexUp_L2, IndexDn_L2, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {0, 1}))
              + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm('Td', 2, {0, 1}))

    tenDq_L2_i = $10Dq(L2)_i_value
    Ve_5d_L2_i = $Ve(5d,L2)_i_value
    Vt2_5d_L2_i = $Vt2(5d,L2)_i_value

    tenDq_L2_m = $10Dq(L2)_m_value
    Ve_5d_L2_m = $Ve(5d,L2)_m_value
    Vt2_5d_L2_m = $Vt2(5d,L2)_m_value

    tenDq_L2_f = $10Dq(L2)_f_value
    Ve_5d_L2_f = $Ve(5d,L2)_f_value
    Vt2_5d_L2_f = $Vt2(5d,L2)_f_value

    H_i = H_i + Chop(
          tenDq_L2_i * tenDq_L2
        + Ve_5d_L2_i * Ve_5d_L2
        + Vt2_5d_L2_i * Vt2_5d_L2)

    H_m = H_m + Chop(
          tenDq_L2_m * tenDq_L2
        + Ve_5d_L2_m * Ve_5d_L2
        + Vt2_5d_L2_m * Vt2_5d_L2)

    H_f = H_f + Chop(
          tenDq_L2_f * tenDq_L2
        + Ve_5d_L2_f * Ve_5d_L2
        + Vt2_5d_L2_f * Vt2_5d_L2)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_5d = NewOperator('Sx', NFermions, IndexUp_5d, IndexDn_5d)
Sy_5d = NewOperator('Sy', NFermions, IndexUp_5d, IndexDn_5d)
Sz_5d = NewOperator('Sz', NFermions, IndexUp_5d, IndexDn_5d)
Ssqr_5d = NewOperator('Ssqr', NFermions, IndexUp_5d, IndexDn_5d)
Splus_5d = NewOperator('Splus', NFermions, IndexUp_5d, IndexDn_5d)
Smin_5d = NewOperator('Smin', NFermions, IndexUp_5d, IndexDn_5d)

Lx_5d = NewOperator('Lx', NFermions, IndexUp_5d, IndexDn_5d)
Ly_5d = NewOperator('Ly', NFermions, IndexUp_5d, IndexDn_5d)
Lz_5d = NewOperator('Lz', NFermions, IndexUp_5d, IndexDn_5d)
Lsqr_5d = NewOperator('Lsqr', NFermions, IndexUp_5d, IndexDn_5d)
Lplus_5d = NewOperator('Lplus', NFermions, IndexUp_5d, IndexDn_5d)
Lmin_5d = NewOperator('Lmin', NFermions, IndexUp_5d, IndexDn_5d)

Jx_5d = NewOperator('Jx', NFermions, IndexUp_5d, IndexDn_5d)
Jy_5d = NewOperator('Jy', NFermions, IndexUp_5d, IndexDn_5d)
Jz_5d = NewOperator('Jz', NFermions, IndexUp_5d, IndexDn_5d)
Jsqr_5d = NewOperator('Jsqr', NFermions, IndexUp_5d, IndexDn_5d)
Jplus_5d = NewOperator('Jplus', NFermions, IndexUp_5d, IndexDn_5d)
Jmin_5d = NewOperator('Jmin', NFermions, IndexUp_5d, IndexDn_5d)

Tx_5d = NewOperator('Tx', NFermions, IndexUp_5d, IndexDn_5d)
Ty_5d = NewOperator('Ty', NFermions, IndexUp_5d, IndexDn_5d)
Tz_5d = NewOperator('Tz', NFermions, IndexUp_5d, IndexDn_5d)

Sx = Sx_5d
Sy = Sy_5d
Sz = Sz_5d

Lx = Lx_5d
Ly = Ly_5d
Lz = Lz_5d

Jx = Jx_5d
Jy = Jy_5d
Jz = Jz_5d

Tx = Tx_5d
Ty = Ty_5d
Tz = Tz_5d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if H_magnetic_field == 1 then
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_m = $Bx_m_value
    By_m = $By_m_value
    Bz_m = $Bz_m_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_m = H_m + Chop(
          Bx_m * (2 * Sx + Lx)
        + By_m * (2 * Sy + Ly)
        + Bz_m * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if H_exchange_field == 1 then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_m = $Hx_m_value
    Hy_m = $Hy_m_value
    Hz_m = $Hz_m_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_m = H_m + Chop(
          Hx_m * Sx
        + Hy_m * Sy
        + Hz_m * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end


NConfigurations = $NConfigurations

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_2p, NElectrons_2p},
                                           {'000000 1111111111', NElectrons_5d, NElectrons_5d}}

IntermediateRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                                {'000000 1111111111', NElectrons_5d + 1, NElectrons_5d + 1}}

FinalRestrictions = InitialRestrictions

if H_5d_ligands_hybridization_lmct == 1 then
    InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_2p, NElectrons_2p},
                                               {'000000 1111111111 0000000000', NElectrons_5d, NElectrons_5d},
                                               {'000000 0000000000 1111111111', NElectrons_L1, NElectrons_L1}}

    IntermediateRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                                    {'000000 1111111111 0000000000', NElectrons_5d + 1, NElectrons_5d + 1},
                                                    {'000000 0000000000 1111111111', NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = InitialRestrictions

    CalculationRestrictions = {NFermions, NBosons, {'000000 0000000000 1111111111', NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

if H_5d_ligands_hybridization_mlct == 1 then
    InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_2p, NElectrons_2p},
                                               {'000000 1111111111 0000000000', NElectrons_5d, NElectrons_5d},
                                               {'000000 0000000000 1111111111', NElectrons_L2, NElectrons_L2}}

    IntermediateRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                                    {'000000 1111111111 0000000000', NElectrons_5d + 1, NElectrons_5d + 1},
                                                    {'000000 0000000000 1111111111', NElectrons_L2, NElectrons_L2}}

    FinalRestrictions = InitialRestrictions

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
-- Define the transition operators.
--------------------------------------------------------------------------------
t = math.sqrt(1/2)

Tx_2p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2p, IndexDn_2p, {{1, -1, t    }, {1, 1, -t    }})
Ty_2p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2p, IndexDn_2p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_2p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2p, IndexDn_2p, {{1,  0, 1    }                })

Tx_5d_2p = NewOperator('CF', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {{1, -1, t    }, {1, 1, -t    }})
Ty_5d_2p = NewOperator('CF', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_5d_2p = NewOperator('CF', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5d, IndexDn_5d, {{1,  0, 1    }                })

k = $k1

-- List with the user selected spectra.
spectra = {$spectra}

--------------------------------------------------------------------------------
-- Calculate and save the spectrum.
--------------------------------------------------------------------------------
Sk = Chop(k[1] * Sx + k[2] * Sy + k[3] * Sz)
Lk = Chop(k[1] * Lx + k[2] * Ly + k[3] * Lz)
Jk = Chop(k[1] * Jx + k[2] * Jy + k[3] * Jz)
Tk = Chop(k[1] * Tx + k[2] * Ty + k[3] * Tz)

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_5d, N_2p, N_5d, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=================================================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_5d>          dZ\n'
header = header .. '=================================================================================================================================\n'
footer = '=================================================================================================================================\n'

if H_5d_ligands_hybridization_lmct == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_5d, N_2p, N_5d, N_L1, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '===========================================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_5d>    <N_L1>          dZ\n'
    header = header .. '===========================================================================================================================================\n'
    footer = '===========================================================================================================================================\n'
end

if H_5d_ligands_hybridization_mlct == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_5d, N_2p, N_5d, N_L2, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '===========================================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_5d>    <N_L2>          dZ\n'
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
    Psis_m = Eigensystem(H_m, IntermediateRestrictions, 1)
else
    Psis_m = Eigensystem(H_m, IntermediateRestrictions, 1, {{'restrictions', CalculationRestrictions}})
end
Psis_m = {Psis_m}
E_gs_m = Psis_m[1] * H_m * Psis_m[1]

Eedge1 = $Eedge1
DeltaE1 = E_gs_m - E_gs_i

Eedge2 = 0.0
DeltaE2 = 0.0

Emin1 = ($Emin1 - Eedge1) + DeltaE1
Emax1 = ($Emax1 - Eedge1) + DeltaE1
NE1 = $NE1
Gamma1 = $Gamma1

Emin2 = ($Emin2 - Eedge2) + DeltaE2
Emax2 = ($Emax2 - Eedge2) + DeltaE2
NE2 = $NE2
Gamma2 = $Gamma2

DenseBorder = $DenseBorder

G = 0

if CalculationRestrictions == nil then
    G = G + CreateResonantSpectra(H_m, H_f, {Tx_2p_5d, Ty_2p_5d, Tz_2p_5d}, {Tx_5d_2p, Ty_5d_2p, Tz_5d_2p}, Psis_i, {{'Emin1', Emin1}, {'Emax1', Emax1}, {'NE1', NE1}, {'Gamma1', Gamma1}, {'Emin2', Emin2}, {'Emax2', Emax2}, {'NE2', NE2}, {'Gamma2', Gamma2}, {'DenseBorder', DenseBorder}})
else
    G = G + CreateResonantSpectra(H_m, H_f, {Tx_2p_5d, Ty_2p_5d, Tz_2p_5d}, {Tx_5d_2p, Ty_5d_2p, Tz_5d_2p}, Psis_i, {{'Emin1', Emin1}, {'Emax1', Emax1}, {'NE1', NE1}, {'Gamma1', Gamma1}, {'Emin2', Emin2}, {'Emax2', Emax2}, {'NE2', NE2}, {'Gamma2', Gamma2}, {'restrictions1', CalculationRestrictions}, {'restrictions2', CalculationRestrictions}, {'DenseBorder', DenseBorder}})
end

Giso = 0
shift = 0

for i = 1, #Psis_i do
    for j = 1, 3 * 3 do
        Indexes = {}
        for k = 1, NE1 + 1 do
            table.insert(Indexes, k + shift)
        end
        Giso = Giso + Spectra.Element(G, Indexes) * dZ[i]
        shift = shift + NE1 + 1
    end
end

Giso = -1 * Giso

Giso.Print({{'file', '$BaseName_iso.spec'}})

