--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 3d transition metals
-- symmetry: D4h
-- experiment: RIXS
-- edge: K1-L2,3 (1s2p)
--------------------------------------------------------------------------------
Verbosity(0x00FF)

--------------------------------------------------------------------------------
-- Define the state of the Hamiltonian terms.
--------------------------------------------------------------------------------
H_coulomb_state  = $H_coulomb_state
H_soc_state      = $H_soc_state
H_cf_state       = $H_cf_state
H_lf_state       = 0

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NFermions = 28
NBosons = 0

NElectrons_1s = $NElectrons_1s
NElectrons_2p = $NElectrons_2p
NElectrons_3d = $NElectrons_3d
NElectrons_Ld = 10

IndexDn_1s = {0}
IndexUp_1s = {1}
IndexDn_2p = {2, 4, 6}
IndexUp_2p = {3, 5, 7}
IndexDn_3d = {8, 10, 12, 14, 16}
IndexUp_3d = {9, 11, 13, 15, 17}
IndexDn_Ld = {18, 20, 22, 24, 26}
IndexUp_Ld = {19, 21, 23, 25, 27}

--------------------------------------------------------------------------------
-- Define the Coulomb term.
--------------------------------------------------------------------------------
F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

F0_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
F2_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
G1_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
G3_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

F0_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {1}, {0})
G2_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {0}, {1})

NUp_1s = NewOperator('Number', NFermions, IndexUp_1s, IndexUp_1s, {1})
NDn_1s = NewOperator('Number', NFermions, IndexDn_1s, IndexDn_1s, {1})
N_1s   = NUp_1s + NDn_1s

NUp_2p = NewOperator('Number', NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
NDn_2p = NewOperator('Number', NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})
N_2p   = NUp_2p + NDn_2p

NUp_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
NDn_3d = NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})
N_3d   = NUp_3d + NDn_3d

NUp_Ld = NewOperator('Number', NFermions, IndexUp_Ld, IndexUp_Ld, {1, 1, 1, 1, 1})
NDn_Ld = NewOperator('Number', NFermions, IndexDn_Ld, IndexDn_Ld, {1, 1, 1, 1, 1})
N_Ld   = NUp_Ld + NDn_Ld

Delta_ic    = $Delta_ic_value * $Delta_ic_scaling
U_3d_3d_ic  = $U(3d,3d)_ic_value * $U(3d,3d)_ic_scaling
F2_3d_3d_ic = $F2(3d,3d)_ic_value * $F2(3d,3d)_ic_scaling
F4_3d_3d_ic = $F4(3d,3d)_ic_value * $F4(3d,3d)_ic_scaling
F0_3d_3d_ic = U_3d_3d_ic + 2 / 63 * F2_3d_3d_ic + 2 / 63 * F4_3d_3d_ic
e_3d_ic     = (10 * Delta_ic - NElectrons_3d * (19 + NElectrons_3d) * U_3d_3d_ic / 2) / (10 + NElectrons_3d)
e_Ld_ic     = NElectrons_3d * ((1 + NElectrons_3d) * U_3d_3d_ic / 2 - Delta_ic) / (10 + NElectrons_3d)

Delta_nc    = $Delta_nc_value * $Delta_nc_scaling
U_3d_3d_nc  = $U(3d,3d)_nc_value * $U(3d,3d)_nc_scaling
F2_3d_3d_nc = $F2(3d,3d)_nc_value * $F2(3d,3d)_nc_scaling
F4_3d_3d_nc = $F4(3d,3d)_nc_value * $F4(3d,3d)_nc_scaling
F0_3d_3d_nc = U_3d_3d_nc + 2 / 63 * F2_3d_3d_nc + 2 / 63 * F4_3d_3d_nc
U_1s_3d_nc  = $U(1s,3d)_nc_value * $U(1s,3d)_nc_scaling
G2_1s_3d_nc = $G2(1s,3d)_nc_value * $G2(1s,3d)_nc_scaling
F0_1s_3d_nc = U_1s_3d_nc + 1 / 10 * G2_1s_3d_nc
F0_1s_3d_nc = U_1s_3d_nc + 1 / 10 * G2_1s_3d_nc
e_1s_nc = (10 * Delta_nc + (1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_nc / 2 - (10 + NElectrons_3d) * U_1s_3d_nc)) / (12 + NElectrons_3d)
e_3d_nc = (10 * Delta_nc - NElectrons_3d * (23 + NElectrons_3d) * U_3d_3d_nc / 2 - 22 * U_1s_3d_nc) / (12 + NElectrons_3d)
e_Ld_nc = ((1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_nc / 2 + 2 * U_1s_3d_nc) - (2 + NElectrons_3d) * Delta_nc) / (12 + NElectrons_3d)

Delta_fc    = $Delta_fc_value * $Delta_fc_scaling
U_3d_3d_fc  = $U(3d,3d)_fc_value * $U(3d,3d)_fc_scaling
F2_3d_3d_fc = $F2(3d,3d)_fc_value * $F2(3d,3d)_fc_scaling
F4_3d_3d_fc = $F4(3d,3d)_fc_value * $F4(3d,3d)_fc_scaling
F0_3d_3d_fc = U_3d_3d_fc + 2 / 63 * F2_3d_3d_fc + 2 / 63 * F4_3d_3d_fc
U_2p_3d_fc  = $U(2p,3d)_fc_value * $U(2p,3d)_fc_scaling
F2_2p_3d_fc = $F2(2p,3d)_fc_value * $F2(2p,3d)_fc_scaling
G1_2p_3d_fc = $G1(2p,3d)_fc_value * $G1(2p,3d)_fc_scaling
G3_2p_3d_fc = $G3(2p,3d)_fc_value * $G3(2p,3d)_fc_scaling
F0_2p_3d_fc = U_2p_3d_fc + 1 / 15 * G1_2p_3d_fc + 3 / 70 * G3_2p_3d_fc
e_2p_fc    = (10 * Delta_fc + (1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_fc / 2 - (10 + NElectrons_3d) * U_2p_3d_fc)) / (16 + NElectrons_3d)
e_3d_fc    = (10 * Delta_fc - NElectrons_3d * (31 + NElectrons_3d) * U_3d_3d_fc / 2 - 90 * U_2p_3d_fc) / (16 + NElectrons_3d)
e_Ld_fc    = ((1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_fc / 2 + 6 * U_2p_3d_fc) - (6 + NElectrons_3d) * Delta_fc) / (16 + NElectrons_3d)

H_coulomb_ic = F0_3d_3d_ic * F0_3d_3d
             + F2_3d_3d_ic * F2_3d_3d
             + F4_3d_3d_ic * F4_3d_3d
             + e_3d_ic     * N_3d
             + e_Ld_ic     * N_Ld

H_coulomb_nc = F0_3d_3d_nc * F0_3d_3d
             + F2_3d_3d_nc * F2_3d_3d
             + F4_3d_3d_nc * F4_3d_3d
             + F0_1s_3d_nc * F0_1s_3d
             + G2_1s_3d_nc * G2_1s_3d
             + e_1s_nc     * N_1s
             + e_3d_nc     * N_3d
             + e_Ld_nc     * N_Ld

H_coulomb_fc = F0_3d_3d_fc * F0_3d_3d
             + F2_3d_3d_fc * F2_3d_3d
             + F4_3d_3d_fc * F4_3d_3d
             + F0_2p_3d_fc * F0_2p_3d
             + F2_2p_3d_fc * F2_2p_3d
             + G1_2p_3d_fc * G1_2p_3d
             + G3_2p_3d_fc * G3_2p_3d
             + e_2p_fc     * N_2p
             + e_3d_fc     * N_3d
             + e_Ld_fc     * N_Ld

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling term.
--------------------------------------------------------------------------------
ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

zeta_3d_ic = $zeta(3d)_ic_value * $zeta(3d)_ic_scaling

zeta_3d_nc = $zeta(3d)_nc_value * $zeta(3d)_nc_scaling

zeta_3d_fc = $zeta(3d)_fc_value * $zeta(3d)_fc_scaling
zeta_2p_fc = $zeta(2p)_fc_value * $zeta(2p)_fc_scaling

H_soc_ic = zeta_3d_ic * ldots_3d

H_soc_nc = zeta_3d_nc * ldots_3d

H_soc_fc = zeta_3d_fc * ldots_3d
         + zeta_2p_fc * ldots_2p

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
tenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, { 0.6,  0.6, -0.4, -0.4}))
Ds_3d    = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-2.0,  2.0,  2.0, -1.0}))
Dt_3d    = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-6.0, -1.0, -1.0,  4.0}))

tenDq_3d_ic = $10Dq(3d)_ic_value * $10Dq(3d)_ic_scaling
Ds_3d_ic = $Ds(3d)_ic_value * $Ds(3d)_ic_scaling
Dt_3d_ic = $Dt(3d)_ic_value * $Dt(3d)_ic_scaling

tenDq_3d_nc = $10Dq(3d)_nc_value * $10Dq(3d)_nc_scaling
Ds_3d_nc = $Ds(3d)_nc_value * $Ds(3d)_nc_scaling
Dt_3d_nc = $Dt(3d)_nc_value * $Dt(3d)_nc_scaling

tenDq_3d_fc = $10Dq(3d)_fc_value * $10Dq(3d)_fc_scaling
Ds_3d_fc = $Ds(3d)_fc_value * $Ds(3d)_fc_scaling
Dt_3d_fc = $Dt(3d)_fc_value * $Dt(3d)_fc_scaling

H_cf_ic = tenDq_3d_ic * tenDq_3d
        + Ds_3d_ic * Ds_3d
        + Dt_3d_ic * Dt_3d

H_cf_nc = tenDq_3d_nc * tenDq_3d
        + Ds_3d_nc * Ds_3d
        + Dt_3d_nc * Dt_3d

H_cf_fc = tenDq_3d_fc * tenDq_3d
        + Ds_3d_fc * Ds_3d
        + Dt_3d_fc * Dt_3d

--------------------------------------------------------------------------------
-- Define the magnetic field term.
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

Sx_Ld    = NewOperator('Sx'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Sy_Ld    = NewOperator('Sy'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Sz_Ld    = NewOperator('Sz'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Ssqr_Ld  = NewOperator('Ssqr' , NFermions, IndexUp_Ld, IndexDn_Ld)
Splus_Ld = NewOperator('Splus', NFermions, IndexUp_Ld, IndexDn_Ld)
Smin_Ld  = NewOperator('Smin' , NFermions, IndexUp_Ld, IndexDn_Ld)

Lx_Ld    = NewOperator('Lx'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Ly_Ld    = NewOperator('Ly'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Lz_Ld    = NewOperator('Lz'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Lsqr_Ld  = NewOperator('Lsqr' , NFermions, IndexUp_Ld, IndexDn_Ld)
Lplus_Ld = NewOperator('Lplus', NFermions, IndexUp_Ld, IndexDn_Ld)
Lmin_Ld  = NewOperator('Lmin' , NFermions, IndexUp_Ld, IndexDn_Ld)

Jx_Ld    = NewOperator('Jx'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Jy_Ld    = NewOperator('Jy'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Jz_Ld    = NewOperator('Jz'   , NFermions, IndexUp_Ld, IndexDn_Ld)
Jsqr_Ld  = NewOperator('Jsqr' , NFermions, IndexUp_Ld, IndexDn_Ld)
Jplus_Ld = NewOperator('Jplus', NFermions, IndexUp_Ld, IndexDn_Ld)
Jmin_Ld  = NewOperator('Jmin' , NFermions, IndexUp_Ld, IndexDn_Ld)

Sx   = Sx_3d + Sx_Ld
Sy   = Sy_3d + Sy_Ld
Sz   = Sz_3d + Sz_Ld
Ssqr = Sx * Sx + Sy * Sy + Sz * Sz

Lx   = Lx_3d + Lx_Ld
Ly   = Ly_3d + Ly_Ld
Lz   = Lz_3d + Lz_Ld
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz

Jx   = Jx_3d + Jx_Ld
Jy   = Jy_3d + Jy_Ld
Jz   = Jz_3d + Jz_Ld
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

Bx = $Bx * EnergyUnits.Tesla.value
By = $By * EnergyUnits.Tesla.value
Bz = $Bz * EnergyUnits.Tesla.value

B = Bx * (2 * Sx + Lx)
  + By * (2 * Sy + Ly)
  + Bz * (2 * Sz + Lz)

--------------------------------------------------------------------------------
-- Compose the total Hamiltonian.
--------------------------------------------------------------------------------
H_ic = H_coulomb_state * H_coulomb_ic
     + H_soc_state     * H_soc_ic
     + H_cf_state      * H_cf_ic
     + B

H_nc = H_coulomb_state * H_coulomb_nc
     + H_soc_state     * H_soc_nc
     + H_cf_state      * H_cf_nc
     + B

H_fc = H_coulomb_state * H_coulomb_fc
     + H_soc_state     * H_soc_fc
     + H_cf_state      * H_cf_fc
     + B

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
if H_lf_state == 1 then
    InitialRestrictions = {NFermions, NBosons, {'11 000000 0000000000 0000000000', NElectrons_1s, NElectrons_1s},
                                               {'00 111111 0000000000 0000000000', NElectrons_2p, NElectrons_2p},
                                               {'00 000000 1111111111 1111111111', NElectrons_3d + NElectrons_Ld, NElectrons_3d + NElectrons_Ld}}

    IntermediateRestrictions = {NFermions, NBosons, {'00 111111 0000000000 0000000000', 0, NElectrons_2p},
                                                    {'00 000000 0000000000 1111111111', 0, NElectrons_Ld}}

    FinalRestrictions = {NFermions, NBosons, {'11 000000 0000000000 0000000000', 0, NElectrons_1s},
                                             {'00 000000 0000000000 1111111111', 0, NElectrons_Ld}}
else
    InitialRestrictions = {NFermions, NBosons, {'11 000000 0000000000 0000000000', NElectrons_1s, NElectrons_1s},
                                               {'00 111111 0000000000 0000000000', NElectrons_2p, NElectrons_2p},
                                               {'00 000000 1111111111 0000000000', NElectrons_3d, NElectrons_3d},
                                               {'00 000000 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}

    IntermediateRestrictions = {NFermions, NBosons, {'00 111111 0000000000 0000000000', NElectrons_2p, NElectrons_2p},
                                                    {'00 000000 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}

    FinalRestrictions = {NFermions, NBosons, {'11 000000 0000000000 0000000000', NElectrons_1s, NElectrons_1s},
                                             {'00 000000 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}
end

NPsis = $NPsis
Psis = Eigensystem(H_ic, InitialRestrictions, NPsis, {{'restrictions', IntermediateRestrictions}})

if not (type(Psis) == 'table') then
    Psis = {Psis}
end

-- Print some useful information about the calculated states.
Operators = {H_ic, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_1s, N_2p, N_3d, N_Ld}
header = '\nAnalysis of the states corresponding to the initial electron configuration:\n'
header = header .. '======================================================================================================\n'
header = header .. '  i      <E>    <S^2>    <L^2>    <J^2>     <Sz>     <Lz>     <Jz>   <N_1s>   <N_2p>   <N_3d>   <N_Ld>\n'
header = header .. '======================================================================================================\n'

io.write(header)
for i, Psi in ipairs(Psis) do
    io.write(string.format('%3d', i))
    for j, Operator in ipairs(Operators) do
        io.write(string.format('%9.4f', Complex.Re(Psi * Operator * Psi)))
    end
    io.write('\n')
end
io.write('======================================================================================================\n\n')

--------------------------------------------------------------------------------
-- Define the transition operators.
--------------------------------------------------------------------------------
t = math.sqrt(1/2);

Txy_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t    }, {2, 1, -t    }})
Tyz_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_1s_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t    }, {2, 2,  t    }})
Tz2_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2,  0, 1    }                })

Tx_2p_1s = NewOperator('CF', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_2p, IndexDn_2p, {{1, -1, t    }, {1, 1, -t    }})
Ty_2p_1s = NewOperator('CF', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_2p, IndexDn_2p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_2p_1s = NewOperator('CF', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_2p, IndexDn_2p, {{1,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

-- Initialize the partition function and the spectrum.
Z = 0
G = 0

Emin1 = $Emin1
Emax1 = $Emax1
Gamma1 = $Gamma1
NE1 = $NE1

Emin2 = $Emin2
Emax2 = $Emax2
Gamma2 = $Gamma2
NE2 = $NE2

-- Calculate the ground state energy.
E_gs = Psis[1] * H_ic * Psis[1]

for i, Psi in ipairs(Psis) do
    E = Psi * H_ic * Psi

    if math.abs(E - E_gs) < 1e-12 then
        dZ = 1
    else
        dZ = math.exp(-(E - E_gs) / T)
    end

    if (dZ < 1e-8) then
        break
    end

    Z = Z + dZ

    for j, OperatorIn in ipairs({Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}) do
        for k, OperatorOut in ipairs({Tx_2p_1s, Ty_2p_1s, Tz_2p_1s}) do
            G = G + CreateResonantSpectra(H_nc, H_fc, OperatorIn, OperatorOut, Psi, {{'Emin1', Emin1}, {'Emax1', Emax1}, {'NE1', NE1}, {'Gamma1', Gamma1}, {'Emin2', Emin2}, {'Emax2', Emax2}, {'NE2', NE2}, {'Gamma2', Gamma2}, {'restrictions1', IntermediateRestrictions}, {'restrictions2', FinalRestrictions}})
        end
    end
end

G = G / 15 / Z
G.Print({{'file', '$baseName' .. '.spec'}})
