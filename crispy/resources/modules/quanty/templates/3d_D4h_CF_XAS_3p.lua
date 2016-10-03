--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- elements: 3d transition metals
-- symmetry: Oh
-- experiment: XAS
-- edge: M2,3 (3p)
-- Hamiltonian: Coulomb, spin-orbit coupling, crystal field
-- transition operators: dipole
-- template modification date: 03/10/2016
--------------------------------------------------------------------------------
Verbosity(0x00FF)

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_3p = $NElectrons_3p
NElectrons_3d = $NElectrons_3d

IndexDn_3p = {0, 2, 4}
IndexUp_3p = {1, 3, 5}
IndexDn_3d = {6, 8, 10, 12, 14}
IndexUp_3d = {7, 9, 11, 13, 15}

--------------------------------------------------------------------------------
-- Define the Coulomb term.
--------------------------------------------------------------------------------
OppF0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
OppF2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
OppF4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

OppF0_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
OppF2_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
OppG1_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
OppG3_3p_3d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

Delta_sc    = $Delta_sc
U_3d_3d_sc  = $U(3d,3d)_sc
F2_3d_3d_sc = $F2(3d,3d)_sc
F4_3d_3d_sc = $F4(3d,3d)_sc
F0_3d_3d_sc = U_3d_3d_sc + 2 / 63 * F2_3d_3d_sc + 2 / 63 * F4_3d_3d_sc

Delta_fc    = $Delta_fc
U_3d_3d_fc  = $U(3d,3d)_fc
F2_3d_3d_fc = $F2(3d,3d)_fc
F4_3d_3d_fc = $F4(3d,3d)_fc
F0_3d_3d_fc = U_3d_3d_fc + 2 / 63 * F2_3d_3d_fc + 2 / 63 * F4_3d_3d_fc
U_3p_3d_fc  = $U(3p,3d)_fc
F2_3p_3d_fc = $F2(3p,3d)_fc
G1_3p_3d_fc = $G1(3p,3d)_fc
G3_3p_3d_fc = $G3(3p,3d)_fc
F0_3p_3d_fc = U_3p_3d_fc + 1 / 15 * G1_3p_3d_fc + 3 / 70 * G3_3p_3d_fc

H_coulomb_sc = F0_3d_3d_sc * OppF0_3d_3d
             + F2_3d_3d_sc * OppF2_3d_3d
             + F4_3d_3d_sc * OppF4_3d_3d

H_coulomb_fc = F0_3d_3d_fc * OppF0_3d_3d
             + F2_3d_3d_fc * OppF2_3d_3d
             + F4_3d_3d_fc * OppF4_3d_3d
             + F0_3p_3d_fc * OppF0_3p_3d
             + F2_3p_3d_fc * OppF2_3p_3d
             + G1_3p_3d_fc * OppG1_3p_3d
             + G3_3p_3d_fc * OppG3_3p_3d

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling term.
--------------------------------------------------------------------------------
Oppldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

Oppldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

zeta_3d_sc = $zeta(3d)_sc

zeta_3d_fc = $zeta(3d)_fc
zeta_3p_fc = $zeta(3p)_fc

H_soc_sc = zeta_3d_sc * Oppldots_3d

H_soc_fc = zeta_3d_fc * Oppldots_3d
         + zeta_3p_fc * Oppldots_3p

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
OpptenDq = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, { 0.6,  0.6, -0.4, -0.4}))
OppDs    = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-2.0,  2.0,  2.0, -1.0}))
OppDt    = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-6.0, -1.0, -1.0,  4.0}))

tenDq_sc = $10Dq_sc
Ds_sc = $Ds_sc
Dt_sc = $Dt_sc

tenDq_fc = $10Dq_fc
Ds_fc = $Ds_fc
Dt_fc = $Dt_fc

H_cf_sc = tenDq_sc * OpptenDq
        + Ds_sc * OppDs
        + Dt_sc * OppDt

H_cf_fc = tenDq_fc * OpptenDq
        + Ds_fc * OppDs
        + Dt_fc * OppDt

--------------------------------------------------------------------------------
-- Define the magnetic field term.
--------------------------------------------------------------------------------
OppSx    = NewOperator('Sx'   , NFermions, IndexUp_3d, IndexDn_3d)
OppSy    = NewOperator('Sy'   , NFermions, IndexUp_3d, IndexDn_3d)
OppSz    = NewOperator('Sz'   , NFermions, IndexUp_3d, IndexDn_3d)
OppSsqr  = NewOperator('Ssqr' , NFermions, IndexUp_3d, IndexDn_3d)
OppSplus = NewOperator('Splus', NFermions, IndexUp_3d, IndexDn_3d)
OppSmin  = NewOperator('Smin' , NFermions, IndexUp_3d, IndexDn_3d)

OppLx    = NewOperator('Lx'   , NFermions, IndexUp_3d, IndexDn_3d)
OppLy    = NewOperator('Ly'   , NFermions, IndexUp_3d, IndexDn_3d)
OppLz    = NewOperator('Lz'   , NFermions, IndexUp_3d, IndexDn_3d)
OppLsqr  = NewOperator('Lsqr' , NFermions, IndexUp_3d, IndexDn_3d)
OppLplus = NewOperator('Lplus', NFermions, IndexUp_3d, IndexDn_3d)
OppLmin  = NewOperator('Lmin' , NFermions, IndexUp_3d, IndexDn_3d)

OppJx    = NewOperator('Jx'   , NFermions, IndexUp_3d, IndexDn_3d)
OppJy    = NewOperator('Jy'   , NFermions, IndexUp_3d, IndexDn_3d)
OppJz    = NewOperator('Jz'   , NFermions, IndexUp_3d, IndexDn_3d)
OppJsqr  = NewOperator('Jsqr' , NFermions, IndexUp_3d, IndexDn_3d)
OppJplus = NewOperator('Jplus', NFermions, IndexUp_3d, IndexDn_3d)
OppJmin  = NewOperator('Jmin' , NFermions, IndexUp_3d, IndexDn_3d)

Bx = $Bx * EnergyUnits.Tesla.value
By = $By * EnergyUnits.Tesla.value
Bz = $Bz * EnergyUnits.Tesla.value

B = Bx * (2 * OppSx + OppLx)
  + By * (2 * OppSy + OppLy)
  + Bz * (2 * OppSz + OppLz)

--------------------------------------------------------------------------------
-- Compose the total Hamiltonian.
--------------------------------------------------------------------------------
H_sc = $H_coulomb_flag * H_coulomb_sc + $H_soc_flag * H_soc_sc + $H_cf_flag * H_cf_sc + B
H_fc = $H_coulomb_flag * H_coulomb_fc + $H_soc_flag * H_soc_fc + $H_cf_flag * H_cf_fc + B

--------------------------------------------------------------------------------
-- Determine the maximum number of states and define the starting restrictions.
--------------------------------------------------------------------------------
NPsis = math.fact(10) / (math.fact(NElectrons_3d) * math.fact(10 - NElectrons_3d))

StartingRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p, NElectrons_3p},
                                            {'000000 1111111111', NElectrons_3d, NElectrons_3d}}

Psis = Eigensystem(H_sc, StartingRestrictions, NPsis)
if not (type(Psis) == 'table') then
    Psis = {Psis}
end

-- Print some useful information about the calculated states.
OppList = {H_sc, OppSsqr, OppLsqr, OppJsqr, OppSz, OppLz}

print('     <E>    <S^2>    <L^2>    <J^2>    <Sz>     <Lz>');
for key, Psi in pairs(Psis) do
	expectationValues = Psi * OppList * Psi
	for key, expectationValue in pairs(expectationValues) do
		io.write(string.format('%9.4f', Complex.Re(expectationValue)))
	end
	io.write('\n')
end

--------------------------------------------------------------------------------
-- Define the transition operator.
--------------------------------------------------------------------------------
t = math.sqrt(1/2);

OppTx_3p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_3p, IndexDn_3p, {{1, -1, t    }, {1, 1, -t    }})
OppTy_3p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_3p, IndexDn_3p, {{1, -1, t * I}, {1, 1,  t * I}})
OppTz_3p_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_3p, IndexDn_3p, {{1,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

-- Initialize the partition function and the spectrum.
Z = 0
G = 0

Emin = $Emin1
Emax = $Emax1
Gamma = $Gamma1
NE = $NE1

-- Calculate the ground state energy.
E_gs = Psis[1] * H_sc * Psis[1]

for j = 1, NPsis do
    E_j = Psis[j] * H_sc * Psis[j]

    if math.abs(E_j - E_gs) < 1e-12 then
        dZ = 1
    else
        dZ = math.exp(-(E_j - E_gs) / T)
    end

    if (dZ < 1e-8) then
        break
    end

    Z = Z + dZ
    G = G + CreateSpectra(H_fc, {OppTx_3p_3d, OppTy_3p_3d, OppTz_3p_3d}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
end

G = Spectra.Sum(G, {1, 1, 1}) / 3 / Z
G.Print({{'file', '$baseName' .. '.spec'}})
