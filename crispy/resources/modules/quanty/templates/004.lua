--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- experiment: XAS
-- edge: M2,3 (3p)
-- elements: 3d transition metals
-- symmetry: Oh
-- Hamiltonian: Coulomb, spin-orbit coupling, crystal field
-- transition operators: dipole
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

Delta_gs    = $Delta_gs
U_3d_3d_gs  = $U(3d,3d)_gs
F2_3d_3d_gs = $F2(3d,3d)_gs
F4_3d_3d_gs = $F4(3d,3d)_gs
F0_3d_3d_gs = U_3d_3d_gs + 2 / 63 * F2_3d_3d_gs + 2 / 63 * F4_3d_3d_gs

Delta_fs    = $Delta_fs
U_3d_3d_fs  = $U(3d,3d)_fs
F2_3d_3d_fs = $F2(3d,3d)_fs
F4_3d_3d_fs = $F4(3d,3d)_fs
F0_3d_3d_fs = U_3d_3d_fs + 2 / 63 * F2_3d_3d_fs + 2 / 63 * F4_3d_3d_fs
U_3p_3d_fs  = $U(3p,3d)_fs
F2_3p_3d_fs = $F2(3p,3d)_fs
G1_3p_3d_fs = $G1(3p,3d)_fs
G3_3p_3d_fs = $G3(3p,3d)_fs
F0_3p_3d_fs = U_3p_3d_fs + 1 / 15 * G1_3p_3d_fs + 3 / 70 * G3_3p_3d_fs

H_coulomb_gs = F0_3d_3d_gs * OppF0_3d_3d
             + F2_3d_3d_gs * OppF2_3d_3d
             + F4_3d_3d_gs * OppF4_3d_3d

H_coulomb_fs = F0_3d_3d_fs * OppF0_3d_3d
             + F2_3d_3d_fs * OppF2_3d_3d
             + F4_3d_3d_fs * OppF4_3d_3d
             + F0_3p_3d_fs * OppF0_3p_3d
             + F2_3p_3d_fs * OppF2_3p_3d
             + G1_3p_3d_fs * OppG1_3p_3d
             + G3_3p_3d_fs * OppG3_3p_3d

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling.
--------------------------------------------------------------------------------
Oppldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

Oppldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

zeta_3d_gs = $zeta(3d)_gs

zeta_3d_fs = $zeta(3d)_fs
zeta_3p_fs = $zeta(3p)_fs

H_soc_gs = zeta_3d_gs * Oppldots_3d

H_soc_fs = zeta_3d_fs * Oppldots_3d
         + zeta_3p_fs * Oppldots_3p

--------------------------------------------------------------------------------
-- Define the crystal field.
--------------------------------------------------------------------------------
OpptenDq = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

tenDq_gs = $10Dq_gs

tenDq_fs = $10Dq_fs

H_cf_gs = tenDq_gs * OpptenDq

H_cf_fs = tenDq_fs * OpptenDq

--------------------------------------------------------------------------------
-- Define the magnetic field.
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

Bx =  $Bx * EnergyUnits.Tesla.value
By =  $By * EnergyUnits.Tesla.value
Bz =  $Bz * EnergyUnits.Tesla.value

B = Bx * (2 * OppSx + OppLx)
  + By * (2 * OppSy + OppLy)
  + Bz * (2 * OppSz + OppLz)

--------------------------------------------------------------------------------
-- Compose the final Hamiltonian.
--------------------------------------------------------------------------------
H_gs = $H_coulomb_flag * H_coulomb_gs + $H_soc_flag * H_soc_gs + $H_cf_flag * H_cf_gs + B
H_fs = $H_coulomb_flag * H_coulomb_fs + $H_soc_flag * H_soc_fs + $H_cf_flag * H_cf_fs + B

--------------------------------------------------------------------------------
--  Define initial restrictions and calculate the ground state energy.
--------------------------------------------------------------------------------
-- Determine the number of possible states in the initial configuration.
NPsis = math.fact(10) / (math.fact(NElectrons_3d) * math.fact(10 - NElectrons_3d))

GroundStateRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p, NElectrons_3p},
                                               {'000000 1111111111', NElectrons_3d, NElectrons_3d}}

-- Calculate the wave functions.
Psis = Eigensystem(H_gs, GroundStateRestrictions, NPsis)
if not (type(Psis) == 'table') then
    Psis = {Psis}
end

-- Calculate the energy of the ground state.
E_gs = Psis[1] * H_gs * Psis[1]

-- Print some useful information about the lowest eigenstates.
OppList = {H_gs, OppSsqr, OppLsqr, OppJsqr, OppSz, OppLz}

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

Spectrum = 0

Emin = -20
Emax = 20
Gamma = 0.2
NE = math.floor(10 * (Emax - Emin) / Gamma)

for j = 1, NPsis do
    E_j = Psis[j] * H_gs * Psis[j]
    if math.abs(E_j - E_gs) < 1e-12 then
        dZ = 1
    else
        dZ = math.exp(-(E_j - E_gs) / T)
    end
    if (dZ < 1e-8) then
        break
    end
    Z = Z + dZ
    Spectrum = Spectrum + CreateSpectra(H_fs, {OppTx_3p_3d, OppTy_3p_3d, OppTz_3p_3d}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
end

Spectrum = Spectrum / Z

-- Broaden the spectrum.
BroadeningLorentzian = $BroadeningLorentzian
BroadeningGaussian = $BroadeningGaussian
Spectrum.Broaden(BroadeningGaussian, BroadeningLorentzian - Gamma)

Spectrum.Print({{'file', '$baseName' .. '.spec'}})
