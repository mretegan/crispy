--------------------------------------------------------------------------------
-- Quanty input file generated using the CRiSPy user-interface.
--
-- experiment: XAS
-- edge: K (1s)
-- elements: 3d transition metals
-- symmetry: Oh
-- Hamiltonian: Coulomb, spin-orbit coupling, crystal field
-- transition operators: quadrupole
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 12

NElectrons_1s = $NElectrons_1s
NElectrons_3d = $NElectrons_3d

IndexDn_1s = {0}
IndexUp_1s = {1}
IndexDn_3d = {2, 4, 6, 8, 10}
IndexUp_3d = {3, 5, 7, 9, 11}

--------------------------------------------------------------------------------
-- Define the Coulomb term.
--------------------------------------------------------------------------------
OppF0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
OppF2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
OppF4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

OppF0_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {1}, {0})
OppG2_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {0}, {1})

scaling_gs  = $scaling_gs
F2_3d_3d_gs = $F2(3d,3d)_gs * scaling_gs
F4_3d_3d_gs = $F4(3d,3d)_gs * scaling_gs
F0_3d_3d_gs = 2.0 / 63.0 * (F2_3d_3d_gs + F4_3d_3d_gs)

scaling_fs  = $scaling_fs
F2_3d_3d_fs = $F2(3d,3d)_fs * scaling_fs
F4_3d_3d_fs = $F4(3d,3d)_fs * scaling_fs
F0_3d_3d_fs = 2.0 / 63.0 * (F2_3d_3d_fs + F4_3d_3d_fs) 
G2_1s_3d_fs = $G2(1s,3d)_fs * scaling_fs

H_coulomb_gs = F0_3d_3d_gs * OppF0_3d_3d +
               F2_3d_3d_gs * OppF2_3d_3d +
               F4_3d_3d_gs * OppF4_3d_3d

H_coulomb_fs = F0_3d_3d_fs * OppF0_3d_3d +
               F2_3d_3d_fs * OppF2_3d_3d +
               F4_3d_3d_fs * OppF4_3d_3d +
               G2_1s_3d_fs * OppG2_1s_3d 

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling.
--------------------------------------------------------------------------------
Oppldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

zeta_3d_gs = $zeta(3d)_gs
zeta_3d_fs = $zeta(3d)_fs

H_soc_gs = zeta_3d_gs * Oppldots_3d
H_soc_fs = zeta_3d_fs * Oppldots_3d

--------------------------------------------------------------------------------
-- Define the crystal field.
--------------------------------------------------------------------------------
tenDq_gs = $10Dq_gs
tenDq_fs = $10Dq_fs

OpptenDq = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Oh', 2, {0.6, -0.4}))

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

B = Bx * (2 * OppSx + OppLx) +
    By * (2 * OppSy + OppLy) +
    Bz * (2 * OppSz + OppLz)

--------------------------------------------------------------------------------
-- Compose the final Hamiltonian.
--------------------------------------------------------------------------------
H_gs = $H_coulomb * H_coulomb_gs + $H_soc * H_soc_gs + $H_cf * H_cf_gs + B
H_fs = $H_coulomb * H_coulomb_fs + $H_soc * H_soc_fs + $H_cf * H_cf_fs + B

--------------------------------------------------------------------------------
--  Define initial restrictions and calculate the ground state energy.
--------------------------------------------------------------------------------
-- Determine the number of possible states in the initial configuration.
NPsis = math.fact(10) / (math.fact(NElectrons_3d) * math.fact(10 - NElectrons_3d))

GroundStateRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_1s, NElectrons_1s},
                                               {'00 1111111111', NElectrons_3d, NElectrons_3d}}

-- Calculate the wave functions.
Psis = Eigensystem(H_gs, GroundStateRestrictions, NPsis)
if not (type(Psis) == 'table') then
    Psis = {Psis}
end

-- Calculate the energy of the ground state.
E_gs = Psis[1] * H_gs * Psis[1]

--------------------------------------------------------------------------------
-- Define the transition operator. 
--------------------------------------------------------------------------------
t = math.sqrt(1/2);

OppTxy   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t * I}, {2, 2, -t * I}})
OppTxz   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t    }, {2, 1, -t    }})
OppTyz   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t * I}, {2, 1,  t * I}})
OppTx2y2 = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t    }, {2, 2,  t    }})
OppTz2   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

-- Initialize the partition function and the spectrum.
Z = 0

Spectrum = 0

Emin = -20.0
Emax = 20.0
Gamma = 0.20
NE = math.floor(10 * (Emax - Emin) / Gamma)

for j = 1, NPsis do

    dZ = math.exp(-(Psis[j] * H_gs * Psis[j] - E_gs) / T)

    if (dZ < 1e-8) then
        break
    end

    Z = Z + dZ

    Spectrum = Spectrum + CreateSpectra(H_fs, {OppTxy, OppTxz, OppTyz, OppTx2y2, OppTz2}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'Tensor', true}}) * dZ

end

Spectrum = Spectra.Sum(Spectrum, {1.0, 0.0, 0.0, 0.0, 0.0, 
                                  0.0, 1.0, 0.0, 0.0, 0.0,
                                  0.0, 0.0, 1.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0, 1.0, 0.0,
                                  0.0, 0.0, 0.0, 0.0, 1.0}) / 15.0

-- Broaden the spectrum.
BroadeningLorentzian = $BroadeningLorentzian
BroadeningGaussian = $BroadeningGaussian
Spectrum.Broaden(BroadeningGaussian, BroadeningLorentzian - Gamma)

Spectrum.Print({{'file', 'quanty.spec'}})
