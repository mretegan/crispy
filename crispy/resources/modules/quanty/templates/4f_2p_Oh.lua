--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: 10.5281/zenodo.1008184.
--
-- elements: 4f
-- symmetry: Oh
-- experiment: XAS, XPS
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
H_cf = $H_cf
H_magnetic_field = $H_magnetic_field
H_exchange_field = $H_exchange_field

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NFermions = 20
NBosons = 0

NElectrons_2p = 6
NElectrons_4f = $NElectrons_4f

IndexDn_2p = {0, 2, 4}
IndexUp_2p = {1, 3, 5}
IndexDn_4f = {6, 8, 10, 12, 14, 16, 18}
IndexUp_4f = {7, 9, 11, 13, 15, 17, 19}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2p = NewOperator('Number', NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_4f = NewOperator('Number', NFermions, IndexUp_4f, IndexUp_4f, {1, 1, 1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_4f, IndexDn_4f, {1, 1, 1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {1, 0, 0, 0})
    F2_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 1, 0, 0})
    F4_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 1, 0})
    F6_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 0, 1})

    F0_2p_4f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {1, 0}, {0, 0})
    F2_2p_4f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {0, 1}, {0, 0})
    G2_2p_4f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {0, 0}, {1, 0})
    G4_2p_4f = NewOperator('U', NFermions, IndexUp_2p, IndexDn_2p, IndexUp_4f, IndexDn_4f, {0, 0}, {0, 1})

    F2_4f_4f_i = $F2(4f,4f)_i_value * $F2(4f,4f)_i_scaling
    F4_4f_4f_i = $F4(4f,4f)_i_value * $F4(4f,4f)_i_scaling
    F6_4f_4f_i = $F6(4f,4f)_i_value * $F6(4f,4f)_i_scaling
    F0_4f_4f_i = 4 / 195 * F2_4f_4f_i + 2 / 143 * F4_4f_4f_i + 100 / 5577 * F6_4f_4f_i

    F2_4f_4f_f = $F2(4f,4f)_f_value * $F2(4f,4f)_f_scaling
    F4_4f_4f_f = $F4(4f,4f)_f_value * $F4(4f,4f)_f_scaling
    F6_4f_4f_f = $F6(4f,4f)_f_value * $F6(4f,4f)_f_scaling
    F0_4f_4f_f = 4 / 195 * F2_4f_4f_f + 2 / 143 * F4_4f_4f_f + 100 / 5577 * F6_4f_4f_f
    F2_2p_4f_f = $F2(2p,4f)_f_value * $F2(2p,4f)_f_scaling
    G2_2p_4f_f = $G2(2p,4f)_f_value * $G2(2p,4f)_f_scaling
    G4_2p_4f_f = $G4(2p,4f)_f_value * $G4(2p,4f)_f_scaling
    F0_2p_4f_f = 3 / 70 * G2_2p_4f_f + 2 / 63 * G4_2p_4f_f

    H_i = H_i + Chop(
          F0_4f_4f_i * F0_4f_4f
        + F2_4f_4f_i * F2_4f_4f
        + F4_4f_4f_i * F4_4f_4f
        + F6_4f_4f_i * F6_4f_4f)

    H_f = H_f + Chop(
          F0_4f_4f_f * F0_4f_4f
        + F2_4f_4f_f * F2_4f_4f
        + F4_4f_4f_f * F4_4f_4f
        + F6_4f_4f_f * F6_4f_4f
        + F0_2p_4f_f * F0_2p_4f
        + F2_2p_4f_f * F2_2p_4f
        + G2_2p_4f_f * G2_2p_4f
        + G4_2p_4f_f * G4_2p_4f)

    ldots_4f = NewOperator('ldots', NFermions, IndexUp_4f, IndexDn_4f)

    ldots_2p = NewOperator('ldots', NFermions, IndexUp_2p, IndexDn_2p)

    zeta_4f_i = $zeta(4f)_i_value * $zeta(4f)_i_scaling

    zeta_4f_f = $zeta(4f)_f_value * $zeta(4f)_f_scaling
    zeta_2p_f = $zeta(2p)_f_value * $zeta(2p)_f_scaling

    H_i = H_i + Chop(
          zeta_4f_i * ldots_4f)

    H_f = H_f + Chop(
          zeta_4f_f * ldots_4f
        + zeta_2p_f * ldots_2p)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('Oh', 3, {Ea2u, Et1u, Et2u})
    Ea2u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {1, 0, 0}))
    Et2u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 1, 0}))
    Et1u_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, PotentialExpandedOnClm('Oh', 3, {0, 0, 1}))

    Ea2u_4f_i = $Ea2u(4f)_i_value
    Et2u_4f_i = $Et2u(4f)_i_value
    Et1u_4f_i = $Et1u(4f)_i_value

    Ea2u_4f_f = $Ea2u(4f)_f_value
    Et2u_4f_f = $Et2u(4f)_f_value
    Et1u_4f_f = $Et1u(4f)_f_value

    -- Set to zero the barycenter of the orbital energies.
    E_4f_i = (Ea2u_4f_i + 3 * Et2u_4f_i + 3 * Et1u_4f_i) / 7
    Ea2u_4f_i = Ea2u_4f_i - E_4f_i
    Et2u_4f_i = Et2u_4f_i - E_4f_i
    Et1u_4f_i = Et1u_4f_i - E_4f_i

    E_4f_f = (Ea2u_4f_f + 3 * Et2u_4f_f + 3 * Et1u_4f_f) / 7
    Ea2u_4f_f = Ea2u_4f_f - E_4f_f
    Et2u_4f_f = Et2u_4f_f - E_4f_f
    Et1u_4f_f = Et1u_4f_f - E_4f_f

    H_i = H_i + Chop(
          Ea2u_4f_i * Ea2u_4f
        + Et2u_4f_i * Et2u_4f
        + Et1u_4f_i * Et1u_4f)

    H_f = H_f + Chop(
          Ea2u_4f_f * Ea2u_4f
        + Et2u_4f_f * Et2u_4f
        + Et1u_4f_f * Et1u_4f)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_4f = NewOperator('Sx', NFermions, IndexUp_4f, IndexDn_4f)
Sy_4f = NewOperator('Sy', NFermions, IndexUp_4f, IndexDn_4f)
Sz_4f = NewOperator('Sz', NFermions, IndexUp_4f, IndexDn_4f)
Ssqr_4f = NewOperator('Ssqr', NFermions, IndexUp_4f, IndexDn_4f)
Splus_4f = NewOperator('Splus', NFermions, IndexUp_4f, IndexDn_4f)
Smin_4f = NewOperator('Smin', NFermions, IndexUp_4f, IndexDn_4f)

Lx_4f = NewOperator('Lx', NFermions, IndexUp_4f, IndexDn_4f)
Ly_4f = NewOperator('Ly', NFermions, IndexUp_4f, IndexDn_4f)
Lz_4f = NewOperator('Lz', NFermions, IndexUp_4f, IndexDn_4f)
Lsqr_4f = NewOperator('Lsqr', NFermions, IndexUp_4f, IndexDn_4f)
Lplus_4f = NewOperator('Lplus', NFermions, IndexUp_4f, IndexDn_4f)
Lmin_4f = NewOperator('Lmin', NFermions, IndexUp_4f, IndexDn_4f)

Jx_4f = NewOperator('Jx', NFermions, IndexUp_4f, IndexDn_4f)
Jy_4f = NewOperator('Jy', NFermions, IndexUp_4f, IndexDn_4f)
Jz_4f = NewOperator('Jz', NFermions, IndexUp_4f, IndexDn_4f)
Jsqr_4f = NewOperator('Jsqr', NFermions, IndexUp_4f, IndexDn_4f)
Jplus_4f = NewOperator('Jplus', NFermions, IndexUp_4f, IndexDn_4f)
Jmin_4f = NewOperator('Jmin', NFermions, IndexUp_4f, IndexDn_4f)

Sx = Sx_4f
Sy = Sy_4f
Sz = Sz_4f

Lx = Lx_4f
Ly = Ly_4f
Lz = Lz_4f

Jx = Jx_4f
Jy = Jy_4f
Jz = Jz_4f

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if H_magnetic_field == 1 then
    Bx_i = $Bx_i_value * EnergyUnits.Tesla.value
    By_i = $By_i_value * EnergyUnits.Tesla.value
    Bz_i = $Bz_i_value * EnergyUnits.Tesla.value

    Bx_f = $Bx_f_value * EnergyUnits.Tesla.value
    By_f = $By_f_value * EnergyUnits.Tesla.value
    Bz_f = $Bz_f_value * EnergyUnits.Tesla.value

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
Experiment = '$Experiment'

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'111111 00000000000000', NElectrons_2p, NElectrons_2p},
                                           {'000000 11111111111111', NElectrons_4f, NElectrons_4f}}

FinalRestrictions = {NFermions, NBosons, {'111111 00000000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                         {'000000 11111111111111', NElectrons_4f + 1, NElectrons_4f + 1}}

if Experiment == 'XPS' then
    FinalRestrictions = {NFermions, NBosons, {'111111 00000000000000', NElectrons_2p - 1, NElectrons_2p - 1},
                                             {'000000 11111111111111', NElectrons_4f, NElectrons_4f}}
end

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2p, N_4f, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=============================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2p>    <N_4f>          dZ\n'
header = header .. '=============================================================================================================\n'
footer = '=============================================================================================================\n'

T = $T * EnergyUnits.Kelvin.value

 -- Approximate machine epsilon.
epsilon = 2.22e-16

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

--------------------------------------------------------------------------------
-- Define the transition operators.
--------------------------------------------------------------------------------
t = math.sqrt(1/2);

Txy_2p_4f   = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_2p_4f   = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -1, t    }, {2, 1, -t    }})
Tyz_2p_4f   = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_2p_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2, -2, t    }, {2, 2,  t    }})
Tz2_2p_4f   = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_2p, IndexDn_2p, {{2,  0, 1    }                })

Ta_2p = {}
for i = 1, NElectrons_2p / 2 do
    Ta_2p[2*i - 1] = NewOperator('An', NFermions, IndexDn_2p[i])
    Ta_2p[2*i]     = NewOperator('An', NFermions, IndexUp_2p[i])
end

T = {}
if Experiment == 'XAS' then
    T = {Txy_2p_4f, Txz_2p_4f, Tyz_2p_4f, Tx2y2_2p_4f, Tz2_2p_4f}
elseif Experiment == 'XPS' then
    T = Ta_2p
else
    return
end

--------------------------------------------------------------------------------
-- Calculate and save the spectrum.
--------------------------------------------------------------------------------
E_gs_i = Psis_i[1] * H_i * Psis_i[1]

if CalculationRestrictions == nil then
    Psis_f = Eigensystem(H_f, FinalRestrictions, 1)
else
    Psis_f = Eigensystem(H_f, FinalRestrictions, 1, {{'restrictions', CalculationRestrictions}})
end

Psis_f = {Psis_f}
E_gs_f = Psis_f[1] * H_f * Psis_f[1]

Eedge1 = $Eedge1
DeltaE = Eedge1 + E_gs_i - E_gs_f

Emin = $Emin1 - DeltaE
Emax = $Emax1 - DeltaE
Gamma = $Gamma1
NE = $NE1

if CalculationRestrictions == nil then
    G = CreateSpectra(H_f, T, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}})
else
    G = CreateSpectra(H_f, T, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}})
end

IndicesToSum = {}
for i in ipairs(T) do
    for j in ipairs(Psis_i) do
        if Experiment == 'XAS' then
            table.insert(IndicesToSum, dZ[j] / #T / 3)
        elseif Experiment == 'XPS' then
            table.insert(IndicesToSum, dZ[j] / #T)
        end
    end
end

G = Spectra.Sum(G, IndicesToSum)
G = G / (2 * math.pi)

Gmin1 = $Gmin1 - Gamma
Gmax1 = $Gmax1 - Gamma
Egamma1 = $Egamma1 - DeltaE
G.Broaden(0, {{Emin, Gmin1}, {Egamma1, Gmin1}, {Egamma1, Gmax1}, {Emax, Gmax1}})

G.Print({{'file', '$BaseName.spec'}})

