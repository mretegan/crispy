--------------------------------------------------------------------------------
-- Quanty input file generated using the CRiSPy user-interface.
--
-- experiment: XAS
-- edge: K
-- elements: 3d transition metals
-- symmetry: Oh
-- Hamiltonian: Coulomb, spin-orbit coupling, crystal field
-- transition operators: dipole
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 16

NElectrons_2p = $NElectrons_2p
NElectrons_3d = $NElectrons_3d

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_3d = {6, 8, 10, 12, 14}
IndexUp_3d = {7, 9, 11, 13, 15}

--------------------------------------------------------------------------------
-- Define the Coulomb term.
--------------------------------------------------------------------------------
OppF0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
OppF2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
OppF4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

OppF0_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
OppF2_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
OppG1_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
OppG3_2p_3d = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

scaling_gs  = $scaling_gs
F2_3d_3d_gs = $F2(3d,3d)_gs * scaling_gs
F4_3d_3d_gs = $F4(3d,3d)_gs * scaling_gs
F0_3d_3d_gs = 2.0 / 63.0 * (F2_3d_3d_gs + F4_3d_3d_gs)

scaling_fs  = $scaling_fs
F2_3d_3d_fs = $F2(3d,3d)_fs * scaling_fs
F4_3d_3d_fs = $F4(3d,3d)_fs * scaling_fs
F0_3d_3d_fs = 2.0 / 63.0 * (F2_3d_3d_fs + F4_3d_3d_fs) 
F2_2p_3d_fs = $F2(2p,3d)_fs * scaling_fs
G1_2p_3d_fs = $G1(2p,3d)_fs * scaling_fs
G3_2p_3d_fs = $G3(2p,3d)_fs * scaling_fs
F0_2p_3d_fs = 1.0 / 15.0 * G1_2p_3d_fs + 3.0 / 70.0 * G3_2p_3d_fs

H_coulomb_gs = F0_3d_3d_gs * OppF0_3d_3d +
               F2_3d_3d_gs * OppF2_3d_3d +
               F4_3d_3d_gs * OppF4_3d_3d

H_coulomb_fs = F0_3d_3d_fs * OppF0_3d_3d +
               F2_3d_3d_fs * OppF2_3d_3d +
               F4_3d_3d_fs * OppF4_3d_3d +
               F0_2p_3d_fs * OppF0_2p_3d +
               F2_2p_3d_fs * OppF2_2p_3d +
               G1_2p_3d_fs * OppG1_2p_3d +
               G3_2p_3d_fs * OppG3_2p_3d

--------------------------------------------------------------------------------
-- Define the spin-orbit coupling.
--------------------------------------------------------------------------------
Oppldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)
Oppldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

zeta_3d_gs = $zeta(3d)_gs

zeta_3d_fs = $zeta(3d)_fs
zeta_2p_fs = $zeta(2p)_fs

H_soc_gs = zeta_3d_gs * Oppldots_3d

H_soc_fs = zeta_3d_fs * Oppldots_3d + 
           zeta_2p_fs * Oppldots_2p

--------------------------------------------------------------------------------
-- Define the crystal field.
--------------------------------------------------------------------------------
tenDq_gs = $10Dq_gs
Ds_gs = $Ds_gs
Dt_gs = $Dt_gs

tenDq_fs = $10Dq_fs
Ds_fs = $Ds_fs
Dt_fs = $Dt_fs

OpptenDq = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, { 0.6,  0.6, -0.4, -0.4}))
OppDs    = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-2.0,  2.0,  2.0, -1.0}))
OppDt    = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('D4h', 2, {-6.0, -1.0, -1.0,  4.0}))

H_cf_gs = tenDq_gs * OpptenDq +
             Ds_gs * OppDs +
             Dt_gs * OppDt

H_cf_fs = tenDq_fs * OpptenDq +
             Ds_fs * OppDs +
             Dt_fs * OppDt

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

GoundStateRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_2p, NElectrons_2p},
                                              {'000000 1111111111', NElectrons_3d, NElectrons_3d}}

-- Calculate the wave functions.
Psis = Eigensystem(H_gs, GoundStateRestrictions, NPsis)
if not (type(Psis) == 'table') then
    Psis = {Psis}
end

-- Calculate the energy of the ground state.
E_gs = Psis[1] * H_gs * Psis[1]

--------------------------------------------------------------------------------
-- Define the transition operator. 
--------------------------------------------------------------------------------
t = math.sqrt(1/2);

OppTx = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, {{1, -1, t    }, {1, 1, -t    }})
OppTy = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, {{1, -1, t * I}, {1, 1,  t * I}})
OppTz = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, {{1,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

-- Initialize the partition function and the spectrum.
Z = 0

Spectrum_x = 0
Spectrum_y = 0
Spectrum_z = 0

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

    Spectrum_x = Spectrum_x + CreateSpectra(H_fs, {OppTx}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    Spectrum_y = Spectrum_y + CreateSpectra(H_fs, {OppTy}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
    Spectrum_z = Spectrum_z + CreateSpectra(H_fs, {OppTz}, Psis[j], {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ

end

Spectrum = (Spectrum_x + Spectrum_y + Spectrum_z) / 3.0

-- Broaden the spectrum.
BroadeningLorentzian = $BroadeningLorentzian
BroadeningGaussian = $BroadeningGaussian
Spectrum.Broaden(BroadeningGaussian, BroadeningLorentzian - Gamma)

Spectrum.Print({{'file', 'quanty.spec'}})
