--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: 10.5281/zenodo.1008184.
--
-- elements: 5f
-- symmetry: Oh
-- experiment: XAS
-- edge: L2,3 (2p)
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
H_cf     = $H_cf

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NFermions = 20
NBosons = 0

NElectrons_2p = 6
NElectrons_5f = $NElectrons_5f

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_5f = {6, 8, 10, 12, 14, 16, 18}
IndexUp_5f = {7, 9, 11, 13, 15, 17, 19}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2p = NewOperator('Number', NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_5f = NewOperator('Number', NFermions, IndexUp_5f, IndexUp_5f, {1, 1, 1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_5f, IndexDn_5f, {1, 1, 1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_5f_5f = NewOperator('U', NFermions, IndexUp_5f, IndexDn_5f, {1, 0, 0, 0})
    F2_5f_5f = NewOperator('U', NFermions, IndexUp_5f, IndexDn_5f, {0, 1, 0, 0})
    F4_5f_5f = NewOperator('U', NFermions, IndexUp_5f, IndexDn_5f, {0, 0, 1, 0})
    F6_5f_5f = NewOperator('U', NFermions, IndexUp_5f, IndexDn_5f, {0, 0, 0, 1})

    F0_2p_5f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5f, IndexDn_5f, {1, 0}, {0, 0})
    F2_2p_5f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5f, IndexDn_5f, {0, 1}, {0, 0})
    G2_2p_5f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5f, IndexDn_5f, {0, 0}, {1, 0})
    G4_2p_5f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_5f, IndexDn_5f, {0, 0}, {0, 1})

    F2_5f_5f_i = $F2(5f,5f)_i_value * $F2(5f,5f)_i_scaling
    F4_5f_5f_i = $F4(5f,5f)_i_value * $F4(5f,5f)_i_scaling
    F6_5f_5f_i = $F6(5f,5f)_i_value * $F6(5f,5f)_i_scaling
    F0_5f_5f_i = 4 / 195 * F2_5f_5f_i + 2 / 143 * F4_5f_5f_i + 100 / 5577 * F6_5f_5f_i

    F2_5f_5f_f = $F2(5f,5f)_f_value * $F2(5f,5f)_f_scaling
    F4_5f_5f_f = $F4(5f,5f)_f_value * $F4(5f,5f)_f_scaling
    F6_5f_5f_f = $F6(5f,5f)_f_value * $F6(5f,5f)_f_scaling
    F0_5f_5f_f = 4 / 195 * F2_5f_5f_f + 2 / 143 * F4_5f_5f_f + 100 / 5577 * F6_5f_5f_f
    F2_2p_5f_f = $F2(2p,5f)_f_value * $F2(2p,5f)_f_scaling
    G2_2p_5f_f = $G2(2p,5f)_f_value * $G2(2p,5f)_f_scaling
    G4_2p_5f_f = $G4(2p,5f)_f_value * $G4(2p,5f)_f_scaling
    F0_2p_5f_f = 3 / 70 * G2_2p_5f_f + 2 / 63 * G4_2p_5f_f

    H_i = H_i
        + F0_5f_5f_i * F0_5f_5f
        + F2_5f_5f_i * F2_5f_5f
        + F4_5f_5f_i * F4_5f_5f
        + F6_5f_5f_i * F6_5f_5f

    H_f = H_f
        + F0_5f_5f_f * F0_5f_5f
        + F2_5f_5f_f * F2_5f_5f
        + F4_5f_5f_f * F4_5f_5f
        + F6_5f_5f_f * F6_5f_5f
        + F0_2p_5f_f * F0_2p_5f
        + F2_2p_5f_f * F2_2p_5f
        + G2_2p_5f_f * G2_2p_5f
        + G4_2p_5f_f * G4_2p_5f

    ldots_5f = NewOperator('ldots', NFermions, IndexUp_5f, IndexDn_5f)

    ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

    zeta_5f_i = $zeta(5f)_i_value * $zeta(5f)_i_scaling

    zeta_5f_f = $zeta(5f)_f_value * $zeta(5f)_f_scaling
    zeta_2p_f = $zeta(2p)_f_value * $zeta(2p)_f_scaling

    H_i = H_i
        + zeta_5f_i * ldots_5f

    H_f = H_f
        + zeta_5f_f * ldots_5f
        + zeta_2p_f * ldots_2p
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('Oh', 3, {Ea2u, Et1u, Et2u})
    Ea2u_5f = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, PotentialExpandedOnClm('Oh', 3, {1, 0, 0}))
    Et2u_5f = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, PotentialExpandedOnClm('Oh', 3, {0, 1, 0}))
    Et1u_5f = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, PotentialExpandedOnClm('Oh', 3, {0, 0, 1}))

    Ea2u_5f_i = $Ea2u(5f)_i_value
    Et2u_5f_i = $Et2u(5f)_i_value
    Et1u_5f_i = $Et1u(5f)_i_value

    Ea2u_5f_f = $Ea2u(5f)_f_value
    Et2u_5f_f = $Et2u(5f)_f_value
    Et1u_5f_f = $Et1u(5f)_f_value

    -- Set to zero the barycenter of the orbital energies.
    E_5f_i = (Ea2u_5f_i + 3 * Et2u_5f_i + 3 * Et1u_5f_i) / 7
    Ea2u_5f_i = Ea2u_5f_i - E_5f_i
    Et2u_5f_i = Et2u_5f_i - E_5f_i
    Et1u_5f_i = Et1u_5f_i - E_5f_i

    E_5f_f = (Ea2u_5f_f + 3 * Et2u_5f_f + 3 * Et1u_5f_f) / 7
    Ea2u_5f_f = Ea2u_5f_f - E_5f_f
    Et2u_5f_f = Et2u_5f_f - E_5f_f
    Et1u_5f_f = Et1u_5f_f - E_5f_f

    H_i = H_i
        + Ea2u_5f_i * Ea2u_5f
        + Et2u_5f_i * Et2u_5f
        + Et1u_5f_i * Et1u_5f

    H_f = H_f
        + Ea2u_5f_f * Ea2u_5f
        + Et2u_5f_f * Et2u_5f
        + Et1u_5f_f * Et1u_5f
end

--------------------------------------------------------------------------------
-- Define the spin and orbital operators.
--------------------------------------------------------------------------------
Sx_5f    = NewOperator('Sx'   , NFermions, IndexUp_5f, IndexDn_5f)
Sy_5f    = NewOperator('Sy'   , NFermions, IndexUp_5f, IndexDn_5f)
Sz_5f    = NewOperator('Sz'   , NFermions, IndexUp_5f, IndexDn_5f)
Ssqr_5f  = NewOperator('Ssqr' , NFermions, IndexUp_5f, IndexDn_5f)
Splus_5f = NewOperator('Splus', NFermions, IndexUp_5f, IndexDn_5f)
Smin_5f  = NewOperator('Smin' , NFermions, IndexUp_5f, IndexDn_5f)

Lx_5f    = NewOperator('Lx'   , NFermions, IndexUp_5f, IndexDn_5f)
Ly_5f    = NewOperator('Ly'   , NFermions, IndexUp_5f, IndexDn_5f)
Lz_5f    = NewOperator('Lz'   , NFermions, IndexUp_5f, IndexDn_5f)
Lsqr_5f  = NewOperator('Lsqr' , NFermions, IndexUp_5f, IndexDn_5f)
Lplus_5f = NewOperator('Lplus', NFermions, IndexUp_5f, IndexDn_5f)
Lmin_5f  = NewOperator('Lmin' , NFermions, IndexUp_5f, IndexDn_5f)

Jx_5f    = NewOperator('Jx'   , NFermions, IndexUp_5f, IndexDn_5f)
Jy_5f    = NewOperator('Jy'   , NFermions, IndexUp_5f, IndexDn_5f)
Jz_5f    = NewOperator('Jz'   , NFermions, IndexUp_5f, IndexDn_5f)
Jsqr_5f  = NewOperator('Jsqr' , NFermions, IndexUp_5f, IndexDn_5f)
Jplus_5f = NewOperator('Jplus', NFermions, IndexUp_5f, IndexDn_5f)
Jmin_5f  = NewOperator('Jmin' , NFermions, IndexUp_5f, IndexDn_5f)

Sx = Sx_5f
Sy = Sy_5f
Sz = Sz_5f

Lx = Lx_5f
Ly = Ly_5f
Lz = Lz_5f

Jx = Jx_5f
Jy = Jy_5f
Jz = Jz_5f

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'111111 00000000000000', NElectrons_2p, NElectrons_2p},
                                           {'000000 11111111111111', NElectrons_5f, NElectrons_5f}}

FinalRestrictions = {NFermions, NBosons, {'111111 00000000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                         {'000000 11111111111111', NElectrons_5f + 1, NElectrons_5f + 1}}

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2p, N_5f}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '==============================================================================================\n'
header = header .. '   i       <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2p>    <N_5f>\n'
header = header .. '==============================================================================================\n'
footer = '==============================================================================================\n'

-- Define the temperature.
T = $T * EnergyUnits.Kelvin.value

 -- Approximate machine epsilon.
epsilon = 2.22e-16
Z = 0

NPsis = $NPsis
NPsisAuto = $NPsisAuto

if NPsisAuto == 1 and NPsis ~= 1 then
    NPsis = 1
    NPsisIncrement = 8
    NPsisIsConverged = false
    dZ = {}

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
end

io.write(header)
for i, Psi in ipairs(Psis_i) do
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

Txy_2p_5f   = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, IndexUp_2p, IndexDn_2p, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_2p_5f   = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, IndexUp_2p, IndexDn_2p, {{2, -1, t    }, {2, 1, -t    }})
Tyz_2p_5f   = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, IndexUp_2p, IndexDn_2p, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_2p_5f = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, IndexUp_2p, IndexDn_2p, {{2, -2, t    }, {2, 2,  t    }})
Tz2_2p_5f   = NewOperator('CF', NFermions, IndexUp_5f, IndexDn_5f, IndexUp_2p, IndexDn_2p, {{2,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
CalculateIso = $calculateIso

if CalculateIso == 0 then
    return
end

E_gs_i = Psis_i[1] * H_i * Psis_i[1]

Psis_f = Eigensystem(H_f, FinalRestrictions, 1)
Psis_f = {Psis_f}
E_gs_f = Psis_f[1] * H_f * Psis_f[1]

Eedge1 = $Eedge1
DeltaE = Eedge1 + E_gs_i - E_gs_f

Emin = $Emin1 - DeltaE
Emax = $Emax1 - DeltaE
Gamma = $Gamma1
NE = $NE1

Z = 0

Giso = 0

for i, Psi in ipairs(Psis_i) do
    E = Psi * H_i * Psi

    if math.abs(E - E_gs_i) < epsilon then
        dZ = 1
    else
        dZ = math.exp(-(E - E_gs_i) / T)
    end

    Z = Z + dZ

    if CalculateIso == 1 then
        for j, Operator in ipairs({Txy_2p_5f, Txz_2p_5f, Tyz_2p_5f, Tx2y2_2p_5f, Tz2_2p_5f}) do
            Giso = Giso + CreateSpectra(H_f, Operator, Psi, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}}) * dZ
        end
    end
end


if CalculateIso == 1 then
    Giso = Giso / Z / 15
    Giso.Print({{'file', '$baseName' .. '_iso.spec'}})
end

