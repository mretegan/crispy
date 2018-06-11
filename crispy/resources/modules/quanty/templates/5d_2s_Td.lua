--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: 10.5281/zenodo.1008184.
--
-- elements: 5d
-- symmetry: Td
-- experiment: XAS, XPS
-- edge: L1 (2s)
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
H_5d_Ld_hybridization = $H_5d_Ld_hybridization
H_magnetic_field = $H_magnetic_field
H_exchange_field = $H_exchange_field

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 12

NElectrons_2s = 2
NElectrons_5d = $NElectrons_5d

IndexDn_2s = {0}
IndexUp_2s = {1}
IndexDn_5d = {2, 4, 6, 8, 10}
IndexUp_5d = {3, 5, 7, 9, 11}

if H_5d_Ld_hybridization == 1 then
    NFermions = 22

    NElectrons_Ld = 10

    IndexDn_Ld = {12, 14, 16, 18, 20}
    IndexUp_Ld = {13, 15, 17, 19, 21}
end

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2s = NewOperator('Number', NFermions, IndexUp_2s, IndexUp_2s, {1})
     + NewOperator('Number', NFermions, IndexDn_2s, IndexDn_2s, {1})

N_5d = NewOperator('Number', NFermions, IndexUp_5d, IndexUp_5d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_5d, IndexDn_5d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {1, 0, 0})
    F2_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 1, 0})
    F4_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 0, 1})

    F0_2s_5d = NewOperator('U', NFermions, IndexUp_2s, IndexDn_2s, IndexUp_5d, IndexDn_5d, {1}, {0})
    G2_2s_5d = NewOperator('U', NFermions, IndexUp_2s, IndexDn_2s, IndexUp_5d, IndexDn_5d, {0}, {1})

    F2_5d_5d_i = $F2(5d,5d)_i_value * $F2(5d,5d)_i_scaling
    F4_5d_5d_i = $F4(5d,5d)_i_value * $F4(5d,5d)_i_scaling
    F0_5d_5d_i = 2 / 63 * F2_5d_5d_i + 2 / 63 * F4_5d_5d_i

    F2_5d_5d_f = $F2(5d,5d)_f_value * $F2(5d,5d)_f_scaling
    F4_5d_5d_f = $F4(5d,5d)_f_value * $F4(5d,5d)_f_scaling
    F0_5d_5d_f = 2 / 63 * F2_5d_5d_f + 2 / 63 * F4_5d_5d_f
    G2_2s_5d_f = $G2(2s,5d)_f_value * $G2(2s,5d)_f_scaling
    F0_2s_5d_f = 1 / 10 * G2_2s_5d_f

    H_i = H_i + Chop(
          F0_5d_5d_i * F0_5d_5d
        + F2_5d_5d_i * F2_5d_5d
        + F4_5d_5d_i * F4_5d_5d)

    H_f = H_f + Chop(
          F0_5d_5d_f * F0_5d_5d
        + F2_5d_5d_f * F2_5d_5d
        + F4_5d_5d_f * F4_5d_5d
        + F0_2s_5d_f * F0_2s_5d
        + G2_2s_5d_f * G2_2s_5d)

    ldots_5d = NewOperator('ldots', NFermions, IndexUp_5d, IndexDn_5d)

    zeta_5d_i = $zeta(5d)_i_value * $zeta(5d)_i_scaling

    zeta_5d_f = $zeta(5d)_f_value * $zeta(5d)_f_scaling

    H_i = H_i + Chop(
          zeta_5d_i * ldots_5d)

    H_f = H_f + Chop(
          zeta_5d_f * ldots_5d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    -- PotentialExpandedOnClm('Td', 2, {Ee, Et2})
    tenDq_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    tenDq_5d_i = $10Dq(5d)_i_value

    tenDq_5d_f = $10Dq(5d)_f_value

    H_i = H_i + Chop(
          tenDq_5d_i * tenDq_5d)

    H_f = H_f + Chop(
          tenDq_5d_f * tenDq_5d)
end

--------------------------------------------------------------------------------
-- Define the 5d-Ld hybridization term.
--------------------------------------------------------------------------------
if H_5d_Ld_hybridization == 1 then
    N_Ld = NewOperator('Number', NFermions, IndexUp_Ld, IndexUp_Ld, {1, 1, 1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_Ld, IndexDn_Ld, {1, 1, 1, 1, 1})

    Delta_5d_Ld_i = $Delta(5d,Ld)_i_value
    U_5d_5d_i = $U(5d,5d)_i_value
    e_5d_i = (10 * Delta_5d_Ld_i - NElectrons_5d * (19 + NElectrons_5d) * U_5d_5d_i / 2) / (10 + NElectrons_5d)
    e_Ld_i = NElectrons_5d * ((1 + NElectrons_5d) * U_5d_5d_i / 2 - Delta_5d_Ld_i) / (10 + NElectrons_5d)

    Delta_5d_Ld_f = $Delta(5d,Ld)_f_value
    U_5d_5d_f = $U(5d,5d)_f_value
    U_2s_5d_f = $U(2s,5d)_f_value
    e_5d_f = (10 * Delta_5d_Ld_f - NElectrons_5d * (23 + NElectrons_5d) * U_5d_5d_f / 2 - 22 * U_2s_5d_f) / (12 + NElectrons_5d)
    e_2s_f = (10 * Delta_5d_Ld_f + (1 + NElectrons_5d) * (NElectrons_5d * U_5d_5d_f / 2 - (10 + NElectrons_5d) * U_2s_5d_f)) / (12 + NElectrons_5d)
    e_Ld_f = ((1 + NElectrons_5d) * (NElectrons_5d * U_5d_5d_f / 2 + 2 * U_2s_5d_f) - (2 + NElectrons_5d) * Delta_5d_Ld_f) / (12 + NElectrons_5d)

    H_i = H_i + Chop(
          U_5d_5d_i * F0_5d_5d
        + e_5d_i * N_5d
        + e_Ld_i * N_Ld)

    H_f = H_f + Chop(
          U_5d_5d_f * F0_5d_5d
        + U_2s_5d_f * F0_2s_5d
        + e_5d_f * N_5d
        + e_2s_f * N_2s
        + e_Ld_f * N_Ld)

    tenDq_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Ve_5d_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {1, 0}))
             + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Td', 2, {1, 0}))

    Vt2_5d_Ld = NewOperator('CF', NFermions, IndexUp_Ld, IndexDn_Ld, IndexUp_5d, IndexDn_5d, PotentialExpandedOnClm('Td', 2, {0, 1}))
              + NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_Ld, IndexDn_Ld, PotentialExpandedOnClm('Td', 2, {0, 1}))

    tenDq_Ld_i = $10Dq(Ld)_i_value
    Ve_5d_Ld_i = $Ve(5d,Ld)_i_value
    Vt2_5d_Ld_i = $Vt2(5d,Ld)_i_value

    tenDq_Ld_f = $10Dq(Ld)_f_value
    Ve_5d_Ld_f = $Ve(5d,Ld)_f_value
    Vt2_5d_Ld_f = $Vt2(5d,Ld)_f_value

    H_i = H_i + Chop(
          tenDq_Ld_i * tenDq_Ld
        + Ve_5d_Ld_i * Ve_5d_Ld
        + Vt2_5d_Ld_i * Vt2_5d_Ld)

    H_f = H_f + Chop(
          tenDq_Ld_f * tenDq_Ld
        + Ve_5d_Ld_f * Ve_5d_Ld
        + Vt2_5d_Ld_f * Vt2_5d_Ld)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_5d = NewOperator('Sx', NFermions, IndexUp_5d, IndexDn_5d)
Sy_5d = NewOperator('Sy', NFermions, IndexUp_5d, IndexDn_5d)
Sz_5d = NewOperator('Sz', NFermions, IndexUp_5d, IndexDn_5d)
Ssqr_5d = NewOperator('Ssqr', NFermions, IndexUp_5d, IndexDn_5d)
Splus_5d = NewOperator('Splus', NFermions, IndexUp_5d, IndexDn_5d)
Smin_5d = NewOperator('Smin', NFermions, IndexUp_5d, IndexDn_5d)

Lx_5d = NewOperator('Lx', NFermions, IndexUp_5d, IndexDn_5d)
Ly_5d = NewOperator('Ly', NFermions, IndexUp_5d, IndexDn_5d)
Lz_5d = NewOperator('Lz', NFermions, IndexUp_5d, IndexDn_5d)
Lsqr_5d = NewOperator('Lsqr', NFermions, IndexUp_5d, IndexDn_5d)
Lplus_5d = NewOperator('Lplus', NFermions, IndexUp_5d, IndexDn_5d)
Lmin_5d = NewOperator('Lmin', NFermions, IndexUp_5d, IndexDn_5d)

Jx_5d = NewOperator('Jx', NFermions, IndexUp_5d, IndexDn_5d)
Jy_5d = NewOperator('Jy', NFermions, IndexUp_5d, IndexDn_5d)
Jz_5d = NewOperator('Jz', NFermions, IndexUp_5d, IndexDn_5d)
Jsqr_5d = NewOperator('Jsqr', NFermions, IndexUp_5d, IndexDn_5d)
Jplus_5d = NewOperator('Jplus', NFermions, IndexUp_5d, IndexDn_5d)
Jmin_5d = NewOperator('Jmin', NFermions, IndexUp_5d, IndexDn_5d)

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
InitialRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_2s, NElectrons_2s},
                                           {'00 1111111111', NElectrons_5d, NElectrons_5d}}

FinalRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_2s - 1, NElectrons_2s - 1},
                                         {'00 1111111111', NElectrons_5d + 1, NElectrons_5d + 1}}

if Experiment == 'XPS' then
    FinalRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_2s - 1, NElectrons_2s - 1},
                                             {'00 1111111111', NElectrons_5d, NElectrons_5d}}
end

if H_5d_Ld_hybridization == 1 then
    InitialRestrictions = {NFermions, NBosons, {'11 0000000000 0000000000', NElectrons_2s, NElectrons_2s},
                                               {'00 1111111111 0000000000', NElectrons_5d, NElectrons_5d},
                                               {'00 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}

    FinalRestrictions = {NFermions, NBosons, {'11 0000000000 0000000000', NElectrons_2s - 1, NElectrons_2s - 1},
                                             {'00 1111111111 0000000000', NElectrons_5d + 1, NElectrons_5d + 1},
                                             {'00 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}

    if Experiment == 'XPS' then
        FinalRestrictions = {NFermions, NBosons, {'11 0000000000 0000000000', NElectrons_2s - 1, NElectrons_2s - 1},
                                                 {'00 1111111111 0000000000', NElectrons_5d, NElectrons_5d},
                                                 {'00 0000000000 1111111111', NElectrons_Ld, NElectrons_Ld}}
    end

    CalculationRestrictions = {NFermions, NBosons, {'00 0000000000 1111111111', NElectrons_Ld - (NConfigurations - 1), NElectrons_Ld}}
end

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2s, N_5d, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=============================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2s>    <N_5d>          dZ\n'
header = header .. '=============================================================================================================\n'
footer = '=============================================================================================================\n'

if H_5d_Ld_hybridization == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_2s, N_5d, N_Ld, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '=======================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_2s>    <N_5d>    <N_Ld>          dZ\n'
    header = header .. '=======================================================================================================================\n'
    footer = '=======================================================================================================================\n'
end

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

Txy_2s_5d   = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2s, IndexDn_2s, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_2s_5d   = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2s, IndexDn_2s, {{2, -1, t    }, {2, 1, -t    }})
Tyz_2s_5d   = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2s, IndexDn_2s, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_2s_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2s, IndexDn_2s, {{2, -2, t    }, {2, 2,  t    }})
Tz2_2s_5d   = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_2s, IndexDn_2s, {{2,  0, 1    }                })

Ta_2s = {}
for i = 1, NElectrons_2s / 2 do
    Ta_2s[2*i - 1] = NewOperator('An', NFermions, IndexDn_2s[i])
    Ta_2s[2*i]     = NewOperator('An', NFermions, IndexUp_2s[i])
end

T = {}
if Experiment == 'XAS' then
    T = {Txy_2s_5d, Txz_2s_5d, Tyz_2s_5d, Tx2y2_2s_5d, Tz2_2s_5d}
elseif Experiment == 'XPS' then
    T = Ta_2s
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

