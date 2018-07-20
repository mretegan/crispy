--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 5d
-- symmetry: C3v
-- experiment: RIXS
-- edge: M2,3-O4,5 (3p5d)
--------------------------------------------------------------------------------
Verbosity($Verbosity)

--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_m = 0
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
NBosons = 0
NFermions = 16

NElectrons_3p = 6
NElectrons_5d = $NElectrons_5d

IndexDn_3p = {0, 2, 4}
IndexUp_3p = {1, 3, 5}
IndexDn_5d = {6, 8, 10, 12, 14}
IndexUp_5d = {7, 9, 11, 13, 15}

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_3p = NewOperator('Number', NFermions, IndexUp_3p, IndexUp_3p, {1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3p, IndexDn_3p, {1, 1, 1})

N_5d = NewOperator('Number', NFermions, IndexUp_5d, IndexUp_5d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_5d, IndexDn_5d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {1, 0, 0})
    F2_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 1, 0})
    F4_5d_5d = NewOperator('U', NFermions, IndexUp_5d, IndexDn_5d, {0, 0, 1})

    F0_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {1, 0}, {0, 0})
    F2_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {0, 1}, {0, 0})
    G1_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {0, 0}, {1, 0})
    G3_3p_5d = NewOperator('U', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {0, 0}, {0, 1})

    F2_5d_5d_i = $F2(5d,5d)_i_value * $F2(5d,5d)_i_scaling
    F4_5d_5d_i = $F4(5d,5d)_i_value * $F4(5d,5d)_i_scaling
    F0_5d_5d_i = 2 / 63 * F2_5d_5d_i + 2 / 63 * F4_5d_5d_i

    F2_5d_5d_m = $F2(5d,5d)_m_value * $F2(5d,5d)_m_scaling
    F4_5d_5d_m = $F4(5d,5d)_m_value * $F4(5d,5d)_m_scaling
    F0_5d_5d_m = 2 / 63 * F2_5d_5d_m + 2 / 63 * F4_5d_5d_m
    F2_3p_5d_m = $F2(3p,5d)_m_value * $F2(3p,5d)_m_scaling
    G1_3p_5d_m = $G1(3p,5d)_m_value * $G1(3p,5d)_m_scaling
    G3_3p_5d_m = $G3(3p,5d)_m_value * $G3(3p,5d)_m_scaling
    F0_3p_5d_m = 1 / 15 * G1_3p_5d_m + 3 / 70 * G3_3p_5d_m

    F2_5d_5d_f = $F2(5d,5d)_f_value * $F2(5d,5d)_f_scaling
    F4_5d_5d_f = $F4(5d,5d)_f_value * $F4(5d,5d)_f_scaling
    F0_5d_5d_f = 2 / 63 * F2_5d_5d_f + 2 / 63 * F4_5d_5d_f

    H_i = H_i + Chop(
          F0_5d_5d_i * F0_5d_5d
        + F2_5d_5d_i * F2_5d_5d
        + F4_5d_5d_i * F4_5d_5d)

    H_m = H_m + Chop(
          F0_5d_5d_m * F0_5d_5d
        + F2_5d_5d_m * F2_5d_5d
        + F4_5d_5d_m * F4_5d_5d
        + F0_3p_5d_m * F0_3p_5d
        + F2_3p_5d_m * F2_3p_5d
        + G1_3p_5d_m * G1_3p_5d
        + G3_3p_5d_m * G3_3p_5d)

    H_f = H_f + Chop(
          F0_5d_5d_f * F0_5d_5d
        + F2_5d_5d_f * F2_5d_5d
        + F4_5d_5d_f * F4_5d_5d)

    ldots_5d = NewOperator('ldots', NFermions, IndexUp_5d, IndexDn_5d)

    ldots_3p = NewOperator('ldots', NFermions, IndexUp_3p, IndexDn_3p)

    zeta_5d_i = $zeta(5d)_i_value * $zeta(5d)_i_scaling

    zeta_5d_m = $zeta(5d)_m_value * $zeta(5d)_m_scaling
    zeta_3p_m = $zeta(3p)_m_value * $zeta(3p)_m_scaling

    zeta_5d_f = $zeta(5d)_f_value * $zeta(5d)_f_scaling

    H_i = H_i + Chop(
          zeta_5d_i * ldots_5d)

    H_m = H_m + Chop(
          zeta_5d_m * ldots_5d
        + zeta_3p_m * ldots_3p)

    H_f = H_f + Chop(
          zeta_5d_f * ldots_5d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_cf == 1 then
    Dq_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}})
    Dsigma_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, {{2, 0, -7}})
    Dtau_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, {{4, 0, -21}})

    Dq_5d_i = $Dq(5d)_i_value
    Dsigma_5d_i = $Dsigma(5d)_i_value
    Dtau_5d_i = $Dtau(5d)_i_value

    Dq_5d_m = $Dq(5d)_m_value
    Dsigma_5d_m = $Dsigma(5d)_m_value
    Dtau_5d_m = $Dtau(5d)_m_value

    Dq_5d_f = $Dq(5d)_f_value
    Dsigma_5d_f = $Dsigma(5d)_f_value
    Dtau_5d_f = $Dtau(5d)_f_value

    H_i = H_i + Chop(
          Dq_5d_i * Dq_5d
        + Dsigma_5d_i * Dsigma_5d
        + Dtau_5d_i * Dtau_5d)

    H_m = H_m + Chop(
          Dq_5d_m * Dq_5d
        + Dsigma_5d_m * Dsigma_5d
        + Dtau_5d_m * Dtau_5d)

    H_f = H_f + Chop(
          Dq_5d_f * Dq_5d
        + Dsigma_5d_f * Dsigma_5d
        + Dtau_5d_f * Dtau_5d)
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
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_m = $Bx_m_value
    By_m = $By_m_value
    Bz_m = $Bz_m_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_m = H_m + Chop(
          Bx_m * (2 * Sx + Lx)
        + By_m * (2 * Sy + Ly)
        + Bz_m * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if H_exchange_field == 1 then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_m = $Hx_m_value
    Hy_m = $Hy_m_value
    Hz_m = $Hz_m_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_m = H_m + Chop(
          Hx_m * Sx
        + Hy_m * Sy
        + Hz_m * Sz)

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
InitialRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p, NElectrons_3p},
                                           {'000000 1111111111', NElectrons_5d, NElectrons_5d}}

IntermediateRestrictions = {NFermions, NBosons, {'111111 0000000000', NElectrons_3p - 1, NElectrons_3p - 1},
                                                {'000000 1111111111', NElectrons_5d + 1, NElectrons_5d + 1}}

FinalRestrictions = InitialRestrictions

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sz, Lz, Jz, N_3p, N_5d, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=============================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sz>      <Lz>      <Jz>    <N_3p>    <N_5d>          dZ\n'
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

Tx_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1, -1, t    }, {1, 1, -t    }})
Ty_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_3p_5d = NewOperator('CF', NFermions, IndexUp_5d, IndexDn_5d, IndexUp_3p, IndexDn_3p, {{1,  0, 1    }                })

Tx_5d_3p = NewOperator('CF', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {{1, -1, t    }, {1, 1, -t    }})
Ty_5d_3p = NewOperator('CF', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {{1, -1, t * I}, {1, 1,  t * I}})
Tz_5d_3p = NewOperator('CF', NFermions, IndexUp_3p, IndexDn_3p, IndexUp_5d, IndexDn_5d, {{1,  0, 1    }                })

--------------------------------------------------------------------------------
-- Calculate and save the spectrum.
--------------------------------------------------------------------------------
E_gs_i = Psis_i[1] * H_i * Psis_i[1]

if CalculationRestrictions == nil then
    Psis_m = Eigensystem(H_m, IntermediateRestrictions, 1)
else
    Psis_m = Eigensystem(H_m, IntermediateRestrictions, 1, {{'restrictions', CalculationRestrictions}})
end
Psis_m = {Psis_m}
E_gs_m = Psis_m[1] * H_m * Psis_m[1]

Eedge1 = $Eedge1
DeltaE1 = Eedge1 + E_gs_i - E_gs_m

Eedge2 = $Eedge2
DeltaE2 = Eedge2

Emin1 = $Emin1 - DeltaE1
Emax1 = $Emax1 - DeltaE1
NE1 = $NE1
Gamma1 = $Gamma1

Emin2 = $Emin2 - DeltaE2
Emax2 = $Emax2 - DeltaE2
NE2 = $NE2
Gamma2 = $Gamma2

DenseBorder = $DenseBorder

G = 0

if CalculationRestrictions == nil then
    G = G + CreateResonantSpectra(H_m, H_f, {Tx_3p_5d, Ty_3p_5d, Tz_3p_5d}, {Tx_5d_3p, Ty_5d_3p, Tz_5d_3p}, Psis_i, {{'Emin1', Emin1}, {'Emax1', Emax1}, {'NE1', NE1}, {'Gamma1', Gamma1}, {'Emin2', Emin2}, {'Emax2', Emax2}, {'NE2', NE2}, {'Gamma2', Gamma2}, {'DenseBorder', DenseBorder}})
else
    G = G + CreateResonantSpectra(H_m, H_f, {Tx_3p_5d, Ty_3p_5d, Tz_3p_5d}, {Tx_5d_3p, Ty_5d_3p, Tz_5d_3p}, Psis_i, {{'Emin1', Emin1}, {'Emax1', Emax1}, {'NE1', NE1}, {'Gamma1', Gamma1}, {'Emin2', Emin2}, {'Emax2', Emax2}, {'NE2', NE2}, {'Gamma2', Gamma2}, {'restrictions1', CalculationRestrictions}, {'restrictions2', CalculationRestrictions}, {'DenseBorder', DenseBorder}})
end

Gtot = 0
shift = 0

for i = 1, #Psis_i do
    for j = 1, 3 * 3 do
        Indexes = {}
        for k = 1, NE1 + 1 do
            table.insert(Indexes, k + shift)
        end
        Gtot = Gtot + Spectra.Element(G, Indexes) * dZ[i]
        shift = shift + NE1 + 1
    end
end

Gtot = -1 * Gtot

Gtot.Print({{'file', '$BaseName.spec'}})

