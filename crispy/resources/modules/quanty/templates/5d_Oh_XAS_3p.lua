--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 5d transition metals
-- symmetry: Oh
-- experiment: XAS
-- edge: M2,3 (3p)
--------------------------------------------------------------------------------
Verbosity(0x00FF)

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
H_coulomb             = $H_coulomb
H_soc                 = $H_soc
H_cf                  = $H_cf
H_5d_Ld_hybridization = 0

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_3p = 6
NElectrons_5d = $NElectrons_5d

IndexDn_3p = {0, 2, 4}
IndexUp_3p = {1, 3, 5}
IndexDn_5d = {6, 8, 10, 12, 14}
IndexUp_5d = {7, 9, 11, 13, 15}

if H_5d_Ld_hybridization == 1 then
    NFermions = 26

    NElectrons_Ld = 10

    IndexDn_Ld = {16, 18, 20, 22, 24}
    IndexUp_Ld = {17, 19, 21, 23, 25}
end

--------------------------------------------------------------------------------
-- Define the Coulomb term.
--------------------------------------------------------------------------------
F0_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {1, 0, 0})
F2_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 1, 0})
F4_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 0, 1})

F0_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {1, 0}, {0, 0})
F2_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {0, 1}, {0, 0})
G1_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {0, 0}, {1, 0})
G3_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {0, 0}, {0, 1})

N_3p = NewOperator('Number', NFermions, IndexUp_3p, IndexUp_3p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3p, IndexDn_3p, {1, 1, 1})

N_5d = NewOperator('Number', NFermions, IndexUp_5d, IndexUp_5d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_5d, IndexDn_5d, {1, 1, 1, 1, 1})

if H_coulomb == 1 then
    U_5d_5d_i  = $U(5d,5d)_i_value * $U(5d,5d)_i_scaling
    F2_5d_5d_i = $F2(5d,5d)_i_value * $F2(5d,5d)_i_scaling
    F4_5d_5d_i = $F4(5d,5d)_i_value * $F4(5d,5d)_i_scaling
    F0_5d_5d_i = U_5d_5d_i + 2 / 63 * F2_5d_5d_i + 2 / 63 * F4_5d_5d_i

    U_5d_5d_f  = $U(5d,5d)_f_value * $U(5d,5d)_f_scaling
    F2_5d_5d_f = $F2(5d,5d)_f_value * $F2(5d,5d)_f_scaling
    F4_5d_5d_f = $F4(5d,5d)_f_value * $F4(5d,5d)_f_scaling
    F0_5d_5d_f = U_5d_5d_f + 2 / 63 * F2_5d_5d_f + 2 / 63 * F4_5d_5d_f
    U_3p_5d_f  = $U(3p,5d)_f_value * $U(3p,5d)_f_scaling
    F2_3p_5d_f = $F2(3p,5d)_f_value * $F2(3p,5d)_f_scaling
    G1_3p_5d_f = $G1(3p,5d)_f_value * $G1(3p,5d)_f_scaling
    G3_3p_5d_f = $G3(3p,5d)_f_value * $G3(3p,5d)_f_scaling
    F0_3p_5d_f = U_3p_5d_f + 1 / 15 * G1_3p_5d_f + 3 / 70 * G3_3p_5d_f

    H_i = H_i
        + F0_5d_5d_i * F0_5d_5d
        + F2_5d_5d_i * F2_5d_5d
        + F4_5d_5d_i * F4_5d_5d

    H_f = H_f
        + F0_5d_5d_f * F0_5d_5d
        + F2_5d_5d_f * F2_5d_5d
        + F4_5d_5d_f * F4_5d_5d
        + F0_3p_5d_f * F0_3p_5d
        + F2_3p_5d_f * F2_3p_5d
        + G1_3p_5d_f * G1_3p_5d
        + G3_3p_5d_f * G3_3p_5d
end

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling term.
--------------------------------------------------------------------------------
ldots_5d = NewOperator('ldots', NFermions, IndexUp_5d, IndexDn_5d)

ldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

if H_soc == 1 then
    zeta_5d_i = $zeta(5d)_i_value * $zeta(5d)_i_scaling

    zeta_5d_f = $zeta(5d)_f_value * $zeta(5d)_f_scaling
    zeta_3p_f = $zeta(3p)_f_value * $zeta(3p)_f_scaling

    H_i = H_i
        + zeta_5d_i * ldots_5d

    H_f = H_f
        + zeta_5d_f * ldots_5d
        + zeta_3p_f * ldots_3p
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
tenDq_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

if H_cf == 1 then
    tenDq_5d_i = $10Dq(5d)_i_value * $10Dq(5d)_i_scaling

    tenDq_5d_f = $10Dq(5d)_f_value * $10Dq(5d)_f_scaling

    H_i = H_i
        + tenDq_5d_i * tenDq_5d

    H_f = H_f
        + tenDq_5d_f * tenDq_5d
end

--------------------------------------------------------------------------------
-- Define the 5d-Ld hybridization term.
--------------------------------------------------------------------------------
if H_5d_Ld_hybridization == 1 then

    N_Ld = NewOperator('Number', NFermions, IndexUp_Ld, IndexUp_Ld, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_Ld, IndexDn_Ld, {1, 1, 1, 1, 1})

    if H_coulomb == 1 then
        -- Delta_5d_Ld_i = $Delta(5d,Ld)_i_value * $Delta(5d,Ld)_i_scaling
        e_5d_i  = (10 * Delta_5d_Ld_i - NElectrons_5d * (19 + NElectrons_5d) * U_5d_5d_i / 2) / (10 + NElectrons_5d)
        e_Ld_i  = NElectrons_5d * ((1 + NElectrons_5d) * U_5d_5d_i / 2 - Delta_5d_Ld_i) / (10 + NElectrons_5d)

        -- Delta_5d_Ld_f = $Delta(5d,Ld)_f_value * $Delta(5d,Ld)_f_scaling
        e_3p_f = (10 * Delta_5d_Ld_f + (1 + NElectrons_5d) * (NElectrons_5d * U_5d_5d_f / 2 - (10 + NElectrons_5d) * U_3p_5d_f)) / (16 + NElectrons_5d)
        e_5d_f = (10 * Delta_5d_Ld_f - NElectrons_5d * (31 + NElectrons_5d) * U_5d_5d_f / 2 - 90 * U_3p_5d_f) / (16 + NElectrons_5d)
        e_Ld_f = ((1 + NElectrons_5d) * (NElectrons_5d * U_5d_5d_f / 2 + 6 * U_3p_5d_f) - (6 + NElectrons_5d) * Delta_5d_Ld_f) / (16 + NElectrons_5d)

        H_i = H_i
            + e_5d_i * N_5d
            + e_Ld_i * N_Ld

        H_f = H_f
            + e_3p_f * N_3p
            + e_5d_f * N_5d
            + e_Ld_f * N_Ld
    end

    tenDq_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

    Vt2g_5d_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Oh', 2, {0, 1}))
               + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {0, 1}))

    Veg_5d_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Oh', 2, {1, 0}))
              + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {1, 0}))

    -- tenDq_Ld_i   = $10Dq(Ld)_i_value * $10Dq(Ld)_i_scaling
    -- Veg_5d_Ld_i  = $Veg(5d,Ld)_i_value * $Veg(5d,Ld)_i_scaling
    -- Vt2g_5d_Ld_i = $Vt2g(5d,Ld)_i_value * $Vt2g(5d,Ld)_i_scaling

    -- tenDq_Ld_f   = $10Dq(Ld)_f_value * $10Dq(Ld)_f_scaling
    -- Veg_5d_Ld_f  = $Veg(5d,Ld)_f_value * $Veg(5d,Ld)_f_scaling
    -- Vt2g_5d_Ld_f = $Vt2g(5d,Ld)_f_value * $Vt2g(5d,Ld)_f_scaling

    H_i = H_i
        + tenDq_Ld_i   * tenDq_Ld
        + Veg_5d_Ld_i  * Veg_5d_Ld
        + Vt2g_5d_Ld_i * Vt2g_5d_Ld

    H_f = H_f
        + tenDq_Ld_f   * tenDq_Ld
        + Veg_5d_Ld_f  * Veg_5d_Ld
        + Vt2g_5d_Ld_f * Vt2g_5d_Ld
end

--------------------------------------------------------------------------------
-- Define the magnetic field term.
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

Bx = $Bx * EnergyUnits.Tesla.value
By = $By * EnergyUnits.Tesla.value
Bz = $Bz * EnergyUnits.Tesla.value

B = Bx * (2 * Sx + Lx)
  + By * (2 * Sy + Ly)
  + Bz * (2 * Sz + Lz)

H_i = H_i
    + B

H_f = H_f
    + B

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p, NElectrons_3p},
                                           {'000000 1111111111', NElectrons_5d, NElectrons_5d}}

if H_5d_Ld_hybridization == 1 then
    InitialRestrictions = {NFermions, NBosons, {'111111 0000000000 0000000000', NElectrons_3p, NElectrons_3p},
                                               {'000000 1111111111 1111111111', NElectrons_5d + NElectrons_Ld, NElectrons_5d + NElectrons_Ld}}
end

NPsis = $NPsis
Psis = Eigensystem(H_i, InitialRestrictions, NPsis)

if not (type(Psis) == 'table') then
    Psis = {Psis}
end

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_3p, N_5d}
header = '\nAnalysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_3p>    <N_5d>\n'
header = header .. '==============================================================================================\n'
footer = '==============================================================================================\n'

if H_5d_Ld_hybridization == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_3p, N_5d, N_Ld}
    header = '\nAnalysis of the initial Hamiltonian:\n'
    header = header .. '========================================================================================================\n'
    header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_3p>    <N_5d>    <N_Ld>\n'
    header = header .. '========================================================================================================\n'
    footer = '========================================================================================================\n'
end

io.write(header)
for i, Psi in ipairs(Psis) do
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

Tx_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1, -1, t    }, {1, 1, -t    }})
Ty_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1,  0, 1    }                })
Tr_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1, -1, 1    }                })
Tl_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1,  1, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

-- Initialize the partition function and the spectra.
Z = 0
G = 0
Gl = 0
Gr = 0

Emin = $Emin1
Emax = $Emax1
Gamma = $Gamma1
NE = $NE1

-- Calculate the ground state energy.
E_gs = Psis[1] * H_i * Psis[1]

for i, Psi in ipairs(Psis) do
    E = Psi * H_i * Psi

    if math.abs(E - E_gs) < 1e-12 then
        dZ = 1
    else
        dZ = math.exp(-(E - E_gs) / T)
    end

    if (dZ < 1e-8) then
        break
    end

    Z = Z + dZ

    for j, Operator in ipairs({Tx_3p_5d, Ty_3p_5d, Tz_3p_5d}) do
        G = G + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}})* dZ
    end

   Gr = Gr + CreateSpectra(H_f, Tr_3p_5d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}})* dZ
   Gl = Gl + CreateSpectra(H_f, Tl_3p_5d, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}})* dZ

end

G = G / 3 / Z
G.Print({{'file', '$baseName' .. '_iso.spec'}})

G = (Gl - Gr) / Z
G.Print({{'file', '$baseName' .. '_cd.spec'}})
