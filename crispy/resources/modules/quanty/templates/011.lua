--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy.
--
-- experiment: XAS
-- edge: K (2s)
-- elements: 3d transition metals
-- symmetry: Oh
-- Hamiltonian: Coulomb, spin-orbit coupling, ligand field
-- transition operators: dipole
--------------------------------------------------------------------------------

Verbosity(0x00FF)

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 22

NElectrons_2s = $NElectrons_2s
NElectrons_3d = $NElectrons_3d
NElectrons_Ld = 10

IndexDn_2s = {0}
IndexUp_2s = {1}
IndexDn_3d = {2, 4, 6, 8, 10}
IndexUp_3d = {3, 5, 7, 9, 11}
IndexDn_Ld = {12, 14, 16, 18, 20}
IndexUp_Ld = {13, 15, 17, 19, 21}

--------------------------------------------------------------------------------
-- Define the Coulomb term.
--------------------------------------------------------------------------------
OppF0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
OppF2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
OppF4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

OppF0_2s_3d = NewOperator('U', NFermions, IndexUp_2s, IndexDn_2s, IndexUp_3d, IndexDn_3d, {1}, {0})
OppG2_2s_3d = NewOperator('U', NFermions, IndexUp_2s, IndexDn_2s, IndexUp_3d, IndexDn_3d, {0}, {1})

OppNUp_2s = NewOperator('Number', NFermions, IndexUp_2s, IndexUp_2s, {1})
OppNDn_2s = NewOperator('Number', NFermions, IndexDn_2s, IndexDn_2s, {1})
OppN_2s   = OppNUp_2s + OppNDn_2s

OppNUp_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
OppNDn_3d = NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})
OppN_3d   = OppNUp_3d + OppNDn_3d

OppNUp_Ld = NewOperator('Number', NFermions, IndexUp_Ld, IndexUp_Ld, {1, 1, 1, 1, 1})
OppNDn_Ld = NewOperator('Number', NFermions, IndexDn_Ld, IndexDn_Ld, {1, 1, 1, 1, 1})
OppN_Ld   = OppNUp_Ld + OppNDn_Ld

Delta_gs    = $Delta_gs
U_3d_3d_gs  = $U(3d,3d)_gs
F2_3d_3d_gs = $F2(3d,3d)_gs
F4_3d_3d_gs = $F4(3d,3d)_gs
F0_3d_3d_gs = U_3d_3d_gs + 2 / 63 * F2_3d_3d_gs + 2 / 63 * F4_3d_3d_gs
e_3d_gs     = (10 * Delta_gs - NElectrons_3d * (19 + NElectrons_3d) * U_3d_3d_gs / 2) / (10 + NElectrons_3d)
e_Ld_gs     = NElectrons_3d * ((1 + NElectrons_3d) * U_3d_3d_gs / 2 - Delta_gs) / (10 + NElectrons_3d)

Delta_fs    = $Delta_fs
U_3d_3d_fs  = $U(3d,3d)_fs
F2_3d_3d_fs = $F2(3d,3d)_fs
F4_3d_3d_fs = $F4(3d,3d)_fs
F0_3d_3d_fs = U_3d_3d_fs + 2 / 63 * F2_3d_3d_fs + 2 / 63 * F4_3d_3d_fs
U_2s_3d_fs  = $U(2s,3d)_fs
G2_2s_3d_fs = $G2(2s,3d)_fs
F0_2s_3d_fs = U_2s_3d_fs + 1 / 10 * G2_2s_3d_fs
e_2s_fs = (10 * Delta_fs + (1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_fs / 2 - (10 + NElectrons_3d) * U_2s_3d_fs)) / (12 + NElectrons_3d)
e_3d_fs = (10 * Delta_fs - NElectrons_3d * (23 + NElectrons_3d) * U_3d_3d_fs / 2 - 22 * U_2s_3d_fs) / (12 + NElectrons_3d)
e_Ld_fs = ((1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_fs / 2 + 2 * U_2s_3d_fs) - (2 + NElectrons_3d) * Delta_fs) / (12 + NElectrons_3d)

H_coulomb_gs = F0_3d_3d_gs * OppF0_3d_3d
             + F2_3d_3d_gs * OppF2_3d_3d
             + F4_3d_3d_gs * OppF4_3d_3d
             + e_3d_gs     * OppN_3d
             + e_Ld_gs     * OppN_Ld


H_coulomb_fs = F0_3d_3d_fs * OppF0_3d_3d
             + F2_3d_3d_fs * OppF2_3d_3d
             + F4_3d_3d_fs * OppF4_3d_3d
             + F0_2s_3d_fs * OppF0_2s_3d
             + G2_2s_3d_fs * OppG2_2s_3d
             + e_2s_fs     * OppN_2s
             + e_3d_fs     * OppN_3d
             + e_Ld_fs     * OppN_Ld

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling.
--------------------------------------------------------------------------------
Oppldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

zeta_3d_gs = $zeta(3d)_gs

zeta_3d_fs = $zeta(3d)_fs

H_soc_gs = zeta_3d_gs * Oppldots_3d

H_soc_fs = zeta_3d_fs * Oppldots_3d

--------------------------------------------------------------------------------
-- Define the ligand field.
--------------------------------------------------------------------------------
OpptenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))
OpptenDq_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

OppVeg_3d = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {1, 0}))
OppVeg_Ld = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {1, 0}))
OppVeg = OppVeg_3d + OppVeg_Ld

OppVt2g_3d = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {0, 1}))
OppVt2g_Ld = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Oh', 2, {0, 1}))
OppVt2g = OppVt2g_3d + OppVt2g_Ld

tenDq_3d_gs = $10Dq(3d)_gs
tenDq_Ld_gs = $10Dq(Ld)_gs
Veg_gs      = $V(eg)_gs
Vt2g_gs     = $V(t2g)_gs

tenDq_3d_fs = $10Dq(3d)_fs
tenDq_Ld_fs = $10Dq(Ld)_fs
Veg_fs      = $V(eg)_fs
Vt2g_fs     = $V(t2g)_fs

H_lf_gs = tenDq_3d_gs * OpptenDq_3d
        + tenDq_Ld_gs * OpptenDq_Ld
        + Veg_gs      * OppVeg
        + Vt2g_gs     * OppVt2g

H_lf_fs = tenDq_3d_fs * OpptenDq_3d
        + tenDq_Ld_fs * OpptenDq_Ld
        + Veg_fs      * OppVeg
        + Vt2g_fs     * OppVt2g

--------------------------------------------------------------------------------
-- Define the magnetic field.
--------------------------------------------------------------------------------
OppSx_3d    = NewOperator('Sx'   , NFermions, IndexUp_3d, IndexDn_3d)
OppSy_3d    = NewOperator('Sy'   , NFermions, IndexUp_3d, IndexDn_3d)
OppSz_3d    = NewOperator('Sz'   , NFermions, IndexUp_3d, IndexDn_3d)
OppSsqr_3d  = NewOperator('Ssqr' , NFermions, IndexUp_3d, IndexDn_3d)
OppSplus_3d = NewOperator('Splus', NFermions, IndexUp_3d, IndexDn_3d)
OppSmin_3d  = NewOperator('Smin' , NFermions, IndexUp_3d, IndexDn_3d)

OppLx_3d    = NewOperator('Lx'   , NFermions, IndexUp_3d, IndexDn_3d)
OppLy_3d    = NewOperator('Ly'   , NFermions, IndexUp_3d, IndexDn_3d)
OppLz_3d    = NewOperator('Lz'   , NFermions, IndexUp_3d, IndexDn_3d)
OppLsqr_3d  = NewOperator('Lsqr' , NFermions, IndexUp_3d, IndexDn_3d)
OppLplus_3d = NewOperator('Lplus', NFermions, IndexUp_3d, IndexDn_3d)
OppLmin_3d  = NewOperator('Lmin' , NFermions, IndexUp_3d, IndexDn_3d)

OppJx_3d    = NewOperator('Jx'   , NFermions, IndexUp_3d, IndexDn_3d)
OppJy_3d    = NewOperator('Jy'   , NFermions, IndexUp_3d, IndexDn_3d)
OppJz_3d    = NewOperator('Jz'   , NFermions, IndexUp_3d, IndexDn_3d)
OppJsqr_3d  = NewOperator('Jsqr' , NFermions, IndexUp_3d, IndexDn_3d)
OppJplus_3d = NewOperator('Jplus', NFermions, IndexUp_3d, IndexDn_3d)
OppJmin_3d  = NewOperator('Jmin' , NFermions, IndexUp_3d, IndexDn_3d)

OppSx_Ld    = NewOperator('Sx'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppSy_Ld    = NewOperator('Sy'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppSz_Ld    = NewOperator('Sz'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppSsqr_Ld  = NewOperator('Ssqr' , NFermions, IndexUp_Ld, IndexDn_Ld)
OppSplus_Ld = NewOperator('Splus', NFermions, IndexUp_Ld, IndexDn_Ld)
OppSmin_Ld  = NewOperator('Smin' , NFermions, IndexUp_Ld, IndexDn_Ld)

OppLx_Ld    = NewOperator('Lx'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppLy_Ld    = NewOperator('Ly'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppLz_Ld    = NewOperator('Lz'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppLsqr_Ld  = NewOperator('Lsqr' , NFermions, IndexUp_Ld, IndexDn_Ld)
OppLplus_Ld = NewOperator('Lplus', NFermions, IndexUp_Ld, IndexDn_Ld)
OppLmin_Ld  = NewOperator('Lmin' , NFermions, IndexUp_Ld, IndexDn_Ld)

OppJx_Ld    = NewOperator('Jx'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppJy_Ld    = NewOperator('Jy'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppJz_Ld    = NewOperator('Jz'   , NFermions, IndexUp_Ld, IndexDn_Ld)
OppJsqr_Ld  = NewOperator('Jsqr' , NFermions, IndexUp_Ld, IndexDn_Ld)
OppJplus_Ld = NewOperator('Jplus', NFermions, IndexUp_Ld, IndexDn_Ld)
OppJmin_Ld  = NewOperator('Jmin' , NFermions, IndexUp_Ld, IndexDn_Ld)

OppSx   = OppSx_3d + OppSx_Ld
OppSy   = OppSy_3d + OppSy_Ld
OppSz   = OppSz_3d + OppSz_Ld
OppSsqr = OppSx * OppSx + OppSy * OppSy + OppSz * OppSz

OppLx   = OppLx_3d + OppLx_Ld
OppLy   = OppLy_3d + OppLy_Ld
OppLz   = OppLz_3d + OppLz_Ld
OppLsqr = OppLx * OppLx + OppLy * OppLy + OppLz * OppLz

OppJx   = OppJx_3d + OppJx_Ld
OppJy   = OppJy_3d + OppJy_Ld
OppJz   = OppJz_3d + OppJz_Ld
OppJsqr = OppJx * OppJx + OppJy * OppJy + OppJz * OppJz

Bx =  $Bx * EnergyUnits.Tesla.value
By =  $By * EnergyUnits.Tesla.value
Bz =  $Bz * EnergyUnits.Tesla.value

B = Bx * (2 * OppSx + OppLx)
  + By * (2 * OppSy + OppLy)
  + Bz * (2 * OppSz + OppLz)

--------------------------------------------------------------------------------
-- Compose the final Hamiltonian.
--------------------------------------------------------------------------------
H_gs = $H_coulomb_flag * H_coulomb_gs + $H_soc_flag * H_soc_gs + $H_lf_flag * H_lf_gs + B
H_fs = $H_coulomb_flag * H_coulomb_fs + $H_soc_flag * H_soc_fs + $H_lf_flag * H_lf_fs + B

--------------------------------------------------------------------------------
--  Define initial restrictions and calculate the ground state energy.
--------------------------------------------------------------------------------
-- Determine the number of possible states in the initial configuration.
NPsis = 16

GroundStateRestrictions = {NFermions, NBosons, {'11 0000000000 0000000000', NElectrons_2s, NElectrons_2s},
                                               {'00 1111111111 0000000000', NElectrons_3d, NElectrons_3d},
                                               {'00 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}

-- Calculate the wave functions.
Psis = Eigensystem(H_gs, GroundStateRestrictions, NPsis)
if not (type(Psis) == 'table') then
    Psis = {Psis}
end

-- Calculate the energy of the ground state.
E_gs = Psis[1] * H_gs * Psis[1]

-- Print some useful information about the lowest eigenstates.
OppList = {H_gs, OppSsqr, OppLsqr, OppJsqr, OppSz, OppLz, OppN_2s, OppN_3d, OppN_Ld}

print('     <E>    <S^2>    <L^2>    <J^2>    <Sz>     <Lz>     <Np>      <Nd>     <NL>');
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

OppTxy_2s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2s, IndexDn_2s, {{2, -2, t * I}, {2, 2, -t * I}})
OppTxz_2s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2s, IndexDn_2s, {{2, -1, t    }, {2, 1, -t    }})
OppTyz_2s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2s, IndexDn_2s, {{2, -1, t * I}, {2, 1,  t * I}})
OppTx2y2_2s_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2s, IndexDn_2s, {{2, -2, t    }, {2, 2,  t    }})
OppTz2_2s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2s, IndexDn_2s, {{2,  0, 1    }                })

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
    Spectrum = Spectrum + CreateSpectra(H_fs, {OppTxy_2s_3d, OppTxz_2s_3d, OppTyz_2s_3d, OppTx2y2_2s_3d, OppTz2_2s_3d}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
end

Spectrum = Spectrum / Z

-- Broaden the spectrum.
BroadeningLorentzian = $BroadeningLorentzian
BroadeningGaussian = $BroadeningGaussian
Spectrum.Broaden(BroadeningGaussian, BroadeningLorentzian - Gamma)

Spectrum.Print({{'file', '$baseName' .. '.spec'}})
