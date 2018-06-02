--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: 10.5281/zenodo.1008184.
--
-- elements: 4f
-- symmetry: Oh
-- experiment: XAS, XPS, XMCD, X(M)LD
-- edge: N4,5 (4d)
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
NFermions = 24
NBosons = 0

NElectrons_4d = 10
NElectrons_4f = $NElectrons_4f

IndexDn_4d = {0, 2, 4, 6, 8}
IndexUp_4d = {1, 3, 5, 7, 9}
IndexDn_4f = {10, 12, 14, 16, 18, 20, 22}
IndexUp_4f = {11, 13, 15, 17, 19, 21, 23}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_4d = NewOperator('Number', NFermions, IndexUp_4d, IndexUp_4d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_4d, IndexDn_4d, {1, 1, 1, 1, 1})

N_4f = NewOperator('Number', NFermions, IndexUp_4f, IndexUp_4f, {1, 1, 1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_4f, IndexDn_4f, {1, 1, 1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {1, 0, 0, 0})
    F2_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 1, 0, 0})
    F4_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 1, 0})
    F6_4f_4f = NewOperator('U', NFermions, IndexUp_4f, IndexDn_4f, {0, 0, 0, 1})

    F0_4d_4f = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {1, 0, 0}, {0, 0, 0});
    F2_4d_4f = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 1, 0}, {0, 0, 0});
    F4_4d_4f = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 1}, {0, 0, 0});
    G1_4d_4f = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {1, 0, 0});
    G3_4d_4f = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 1, 0});
    G5_4d_4f = NewOperator('U', NFermions, IndexUp_4d, IndexDn_4d, IndexUp_4f, IndexDn_4f, {0, 0, 0}, {0, 0, 1});

    F2_4f_4f_i = $F2(4f,4f)_i_value * $F2(4f,4f)_i_scaling
    F4_4f_4f_i = $F4(4f,4f)_i_value * $F4(4f,4f)_i_scaling
    F6_4f_4f_i = $F6(4f,4f)_i_value * $F6(4f,4f)_i_scaling
    F0_4f_4f_i = 4 / 195 * F2_4f_4f_i + 2 / 143 * F4_4f_4f_i + 100 / 5577 * F6_4f_4f_i

    F2_4f_4f_f = $F2(4f,4f)_f_value * $F2(4f,4f)_f_scaling
    F4_4f_4f_f = $F4(4f,4f)_f_value * $F4(4f,4f)_f_scaling
    F6_4f_4f_f = $F6(4f,4f)_f_value * $F6(4f,4f)_f_scaling
    F0_4f_4f_f = 4 / 195 * F2_4f_4f_f + 2 / 143 * F4_4f_4f_f + 100 / 5577 * F6_4f_4f_f
    F2_4d_4f_f = $F2(4d,4f)_f_value * $F2(4d,4f)_f_scaling
    F4_4d_4f_f = $F4(4d,4f)_f_value * $F4(4d,4f)_f_scaling
    G1_4d_4f_f = $G1(4d,4f)_f_value * $G1(4d,4f)_f_scaling
    G3_4d_4f_f = $G3(4d,4f)_f_value * $G3(4d,4f)_f_scaling
    G5_4d_4f_f = $G5(4d,4f)_f_value * $G5(4d,4f)_f_scaling
    F0_4d_4f_f = 3 / 70 * G1_4d_4f_f + 2 / 105 * G3_4d_4f_f + 5 / 231 * G5_4d_4f_f

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
        + F0_4d_4f_f * F0_4d_4f
        + F2_4d_4f_f * F2_4d_4f
        + F4_4d_4f_f * F4_4d_4f
        + G1_4d_4f_f * G1_4d_4f
        + G3_4d_4f_f * G3_4d_4f
        + G5_4d_4f_f * G5_4d_4f)

    ldots_4f = NewOperator('ldots', NFermions, IndexUp_4f, IndexDn_4f)

    ldots_4d = NewOperator('ldots', NFermions, IndexUp_4d, IndexDn_4d)

    zeta_4f_i = $zeta(4f)_i_value * $zeta(4f)_i_scaling

    zeta_4f_f = $zeta(4f)_f_value * $zeta(4f)_f_scaling
    zeta_4d_f = $zeta(4d)_f_value * $zeta(4d)_f_scaling

    H_i = H_i + Chop(
          zeta_4f_i * ldots_4f)

    H_f = H_f + Chop(
          zeta_4f_f * ldots_4f
        + zeta_4d_f * ldots_4d)
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
InitialRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_4d, NElectrons_4d},
                                           {'0000000000 11111111111111', NElectrons_4f, NElectrons_4f}}

FinalRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_4d - 1, NElectrons_4d - 1},
                                         {'0000000000 11111111111111', NElectrons_4f + 1, NElectrons_4f + 1}}

if Experiment == 'XPS' then
    FinalRestrictions = {NFermions, NBosons, {'1111111111 00000000000000', NElectrons_4d - 1, NElectrons_4d - 1},
                                             {'0000000000 11111111111111', NElectrons_4f, NElectrons_4f}}
end

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_4d, N_4f, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=============================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_4d>    <N_4f>          dZ\n'
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

Tx_4d_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_4d, IndexDn_4d, {{1, -1, t    }, {1, 1, -t    }})
Ty_4d_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_4d, IndexDn_4d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_4d_4f = NewOperator('CF', NFermions, IndexUp_4f, IndexDn_4f, IndexUp_4d, IndexDn_4d, {{1,  0, 1    }                })

k1 = $k1
eps11 = $eps11
eps12 = $eps12

Tk1_4d_4f = Chop(k1[1] * Tx_4d_4f + k1[2] * Ty_4d_4f + k1[3] * Tz_4d_4f)
Teps11_4d_4f = Chop(eps11[1] * Tx_4d_4f + eps11[2] * Ty_4d_4f + eps11[3] * Tz_4d_4f)
Teps12_4d_4f = Chop(eps12[1] * Tx_4d_4f + eps12[2] * Ty_4d_4f + eps12[3] * Tz_4d_4f)

Tr_4d_4f = Chop(t * (Teps11_4d_4f - I * Teps12_4d_4f))
Tl_4d_4f = Chop(-t * (Teps11_4d_4f + I * Teps12_4d_4f))

Ta_4d = {}
for i = 1, NElectrons_4d / 2 do
    Ta_4d[2*i - 1] = NewOperator('An', NFermions, IndexDn_4d[i])
    Ta_4d[2*i]     = NewOperator('An', NFermions, IndexUp_4d[i])
end

T = {}
if Experiment == 'XAS' then
    T = {Tx_4d_4f, Ty_4d_4f, Tz_4d_4f}
elseif Experiment == 'XPS' then
    T = Ta_4d
elseif Experiment == 'X(M)LD' then
    T = {Teps11_4d_4f, Teps12_4d_4f}
elseif Experiment == 'XMCD' then
    T = {Tr_4d_4f, Tl_4d_4f}
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
            table.insert(IndicesToSum, dZ[j] / #T)
        elseif Experiment == 'XPS' then
            table.insert(IndicesToSum, dZ[j] / #T)
        elseif Experiment == 'XMCD' or Experiment == 'X(M)LD' then
            if i == 1 then
                table.insert(IndicesToSum, dZ[j])
            else
                table.insert(IndicesToSum, -dZ[j])
            end
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

