--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 3d
-- symmetry: Td
-- experiment: XAS
-- edge: K (1s)
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
H_crystal_field = $H_crystal_field
H_3d_4p_hybridization = $H_3d_4p_hybridization
H_magnetic_field = $H_magnetic_field
H_exchange_field = $H_exchange_field

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = 0
NFermions = 12

NElectrons_1s = 2
NElectrons_3d = $NElectrons_3d

IndexDn_1s = {0}
IndexUp_1s = {1}
IndexDn_3d = {2, 4, 6, 8, 10}
IndexUp_3d = {3, 5, 7, 9, 11}

if H_3d_4p_hybridization == 1 then
    NFermions = 18

    NElectrons_4p = 0

    IndexDn_4p = {12, 14, 16}
    IndexUp_4p = {13, 15, 17}
end

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_1s = NewOperator('Number', NFermions, IndexUp_1s, IndexUp_1s, {1})
     + NewOperator('Number', NFermions, IndexDn_1s, IndexDn_1s, {1})

N_3d = NewOperator('Number', NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator('Number', NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

if H_atomic == 1 then
    F0_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
    F2_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
    F4_3d_3d = NewOperator('U', NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

    F0_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {1}, {0})
    G2_1s_3d = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_3d, IndexDn_3d, {0}, {1})

    U_3d_3d_i = $U(3d,3d)_i_value
    F2_3d_3d_i = $F2(3d,3d)_i_value * $F2(3d,3d)_i_scale
    F4_3d_3d_i = $F4(3d,3d)_i_value * $F4(3d,3d)_i_scale
    F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

    U_3d_3d_f = $U(3d,3d)_f_value
    F2_3d_3d_f = $F2(3d,3d)_f_value * $F2(3d,3d)_f_scale
    F4_3d_3d_f = $F4(3d,3d)_f_value * $F4(3d,3d)_f_scale
    F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
    U_1s_3d_f = $U(1s,3d)_f_value
    G2_1s_3d_f = $G2(1s,3d)_f_value * $G2(1s,3d)_f_scale
    F0_1s_3d_f = U_1s_3d_f + 1 / 10 * G2_1s_3d_f

    H_i = H_i + Chop(
          F0_3d_3d_i * F0_3d_3d
        + F2_3d_3d_i * F2_3d_3d
        + F4_3d_3d_i * F4_3d_3d)

    H_f = H_f + Chop(
          F0_3d_3d_f * F0_3d_3d
        + F2_3d_3d_f * F2_3d_3d
        + F4_3d_3d_f * F4_3d_3d
        + F0_1s_3d_f * F0_1s_3d
        + G2_1s_3d_f * G2_1s_3d)

    ldots_3d = NewOperator('ldots', NFermions, IndexUp_3d, IndexDn_3d)

    zeta_3d_i = $zeta(3d)_i_value * $zeta(3d)_i_scale

    zeta_3d_f = $zeta(3d)_f_value * $zeta(3d)_f_scale

    H_i = H_i + Chop(
          zeta_3d_i * ldots_3d)

    H_f = H_f + Chop(
          zeta_3d_f * ldots_3d)
end

--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if H_crystal_field == 1 then
    -- PotentialExpandedOnClm('Td', 2, {Ee, Et2})
    -- tenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm('Td', 2, {-0.6, 0.4}))

    Akm = {{4, 0, -2.1}, {4, -4, -1.5 * sqrt(0.7)}, {4, 4, -1.5 * sqrt(0.7)}}
    tenDq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, Akm)

    tenDq_3d_i = $10Dq(3d)_i_value

    io.write('Energies of the 3d orbitals in the initial Hamiltonian (crystal field term only):\n')
    io.write('================\n')
    io.write('Irrep.         E\n')
    io.write('================\n')
    io.write(string.format('e       %8.3f\n', -0.6 * tenDq_3d_i))
    io.write(string.format('t2      %8.3f\n',  0.4 * tenDq_3d_i))
    io.write('================\n')
    io.write('\n')

    tenDq_3d_f = $10Dq(3d)_f_value

    H_i = H_i + Chop(
          tenDq_3d_i * tenDq_3d)

    H_f = H_f + Chop(
          tenDq_3d_f * tenDq_3d)
end

--------------------------------------------------------------------------------
-- Define the 3d-4p hybridization term.
--------------------------------------------------------------------------------
if H_3d_4p_hybridization == 1 then
    F0_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
    F2_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
    G1_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
    G3_3d_4p = NewOperator('U', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})
    G1_1s_4p = NewOperator('U', NFermions, IndexUp_1s, IndexDn_1s, IndexUp_4p, IndexDn_4p, {0}, {1})

    F2_3d_4p_i = $F2(3d,4p)_i_value * $F2(3d,4p)_i_scale
    G1_3d_4p_i = $G1(3d,4p)_i_value * $G1(3d,4p)_i_scale
    G3_3d_4p_i = $G3(3d,4p)_i_value * $G3(3d,4p)_i_scale

    F2_3d_4p_f = $F2(3d,4p)_i_value * $F2(3d,4p)_i_scale
    G1_3d_4p_f = $G1(3d,4p)_i_value * $G1(3d,4p)_i_scale
    G3_3d_4p_f = $G3(3d,4p)_i_value * $G3(3d,4p)_i_scale
    G1_1s_4p_f = $G1(1s,4p)_f_value * $G1(1s,4p)_f_scale

    H_i = H_i + Chop(
          F2_3d_4p_i * F2_3d_4p
        + G1_3d_4p_i * G1_3d_4p
        + G3_3d_4p_i * G3_3d_4p)

    H_f = H_f + Chop(
          F2_3d_4p_f * F2_3d_4p
        + G1_3d_4p_f * G1_3d_4p
        + G3_3d_4p_f * G3_3d_4p
        + G1_1s_4p_f * G1_1s_4p)

    ldots_4p = NewOperator('ldots', NFermions, IndexUp_4p, IndexDn_4p)

    zeta_4p_i = $zeta(4p)_i_value

    zeta_4p_f = $zeta(4p)_f_value

    H_i = H_i + Chop(
          zeta_4p_i * ldots_4p)

    H_f = H_f + Chop(
          zeta_4p_f * ldots_4p)

    N_4p = NewOperator('Number', NFermions, IndexUp_4p, IndexUp_4p, {1, 1, 1})
         + NewOperator('Number', NFermions, IndexDn_4p, IndexDn_4p, {1, 1, 1})

    Delta_3d_4p_i = $Delta(3d,4p)_i_value
    e_3d_i = -(NElectrons_3d - 1) * U_3d_3d_i / 2
    e_4p_i =  (NElectrons_3d - 1) * U_3d_3d_i / 2 + Delta_3d_4p_i

    Delta_3d_4p_f = $Delta(3d,4p)_f_value
    e_3d_f= -(NElectrons_3d - 1) * U_3d_3d_f / 2
    e_4p_f=  (NElectrons_3d - 1) * U_3d_3d_f / 2 + Delta_3d_4p_f

    H_i = H_i + Chop(
          e_3d_i * N_3d
        + e_4p_i * N_4p)

    H_f = H_f + Chop(
          e_3d_f * N_3d
        + e_4p_f * N_4p)

    Akm = {{3, 2, (-7 * I) / math.sqrt(6)}, {3, -2, (7 * I) / math.sqrt(6)}}
    Vt2_3d_4p = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_4p, IndexDn_4p, Akm)
              + NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_3d, IndexDn_3d, Akm)

	Vt2_3d_4p_i = $Vt2(3d,4p)_i_value

	Vt2_3d_4p_f = $Vt2(3d,4p)_f_value

    H_i = H_i + Chop(
          Vt2_3d_4p_i * Vt2_3d_4p)

    H_f = H_f + Chop(
          Vt2_3d_4p_f * Vt2_3d_4p)
end

--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_3d = NewOperator('Sx', NFermions, IndexUp_3d, IndexDn_3d)
Sy_3d = NewOperator('Sy', NFermions, IndexUp_3d, IndexDn_3d)
Sz_3d = NewOperator('Sz', NFermions, IndexUp_3d, IndexDn_3d)
Ssqr_3d = NewOperator('Ssqr', NFermions, IndexUp_3d, IndexDn_3d)
Splus_3d = NewOperator('Splus', NFermions, IndexUp_3d, IndexDn_3d)
Smin_3d = NewOperator('Smin', NFermions, IndexUp_3d, IndexDn_3d)

Lx_3d = NewOperator('Lx', NFermions, IndexUp_3d, IndexDn_3d)
Ly_3d = NewOperator('Ly', NFermions, IndexUp_3d, IndexDn_3d)
Lz_3d = NewOperator('Lz', NFermions, IndexUp_3d, IndexDn_3d)
Lsqr_3d = NewOperator('Lsqr', NFermions, IndexUp_3d, IndexDn_3d)
Lplus_3d = NewOperator('Lplus', NFermions, IndexUp_3d, IndexDn_3d)
Lmin_3d = NewOperator('Lmin', NFermions, IndexUp_3d, IndexDn_3d)

Jx_3d = NewOperator('Jx', NFermions, IndexUp_3d, IndexDn_3d)
Jy_3d = NewOperator('Jy', NFermions, IndexUp_3d, IndexDn_3d)
Jz_3d = NewOperator('Jz', NFermions, IndexUp_3d, IndexDn_3d)
Jsqr_3d = NewOperator('Jsqr', NFermions, IndexUp_3d, IndexDn_3d)
Jplus_3d = NewOperator('Jplus', NFermions, IndexUp_3d, IndexDn_3d)
Jmin_3d = NewOperator('Jmin', NFermions, IndexUp_3d, IndexDn_3d)

Tx_3d = NewOperator('Tx', NFermions, IndexUp_3d, IndexDn_3d)
Ty_3d = NewOperator('Ty', NFermions, IndexUp_3d, IndexDn_3d)
Tz_3d = NewOperator('Tz', NFermions, IndexUp_3d, IndexDn_3d)

Sx = Sx_3d
Sy = Sy_3d
Sz = Sz_3d

Lx = Lx_3d
Ly = Ly_3d
Lz = Lz_3d

Jx = Jx_3d
Jy = Jy_3d
Jz = Jz_3d

Tx = Tx_3d
Ty = Ty_3d
Tz = Tz_3d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if H_magnetic_field == 1 then
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

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

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_1s, NElectrons_1s},
                                           {'00 1111111111', NElectrons_3d, NElectrons_3d}}

FinalRestrictions = {NFermions, NBosons, {'11 0000000000', NElectrons_1s - 1, NElectrons_1s - 1},
                                         {'00 1111111111', NElectrons_3d + 1, NElectrons_3d + 1}}

if H_3d_4p_hybridization == 1 then
    InitialRestrictions = {NFermions, NBosons, {'11 0000000000 000000', NElectrons_1s, NElectrons_1s},
                                               {'00 1111111111 000000', NElectrons_3d, NElectrons_3d},
                                               {'00 0000000000 111111', NElectrons_4p, NElectrons_4p}}

    FinalRestrictions = {NFermions, NBosons, {'11 0000000000 000000', NElectrons_1s - 1, NElectrons_1s - 1},
                                             {'00 1111111111 000000', NElectrons_3d + 1, NElectrons_3d + 1},
                                             {'00 0000000000 111111', NElectrons_4p, NElectrons_4p}}

    CalculationRestrictions = {NFermions, NBosons, {'00 0000000000 111111', NElectrons_4p, NElectrons_4p + 1}}
end

T = $T * EnergyUnits.Kelvin.value

-- Approximate machine epsilon for single precision arithmetics.
epsilon = 1.19e-07

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

--------------------------------------------------------------------------------
-- Define some helper function for the spectra calculation.
--------------------------------------------------------------------------------
function ValueInTable(value, table)
    -- Check if a value is in a table.
    for k, v in ipairs(table) do
        if value == v then
            return true
        end
    end
    return false
end

function GetSpectrum(G, T, Psis, indices, dZSpectra)
    -- Extract the spectra corresponding to the operators identified
    -- using the indices argument. The returned spectrum is a weighted
    -- sum, where the weights are the Boltzmann probabilities.
    if not (type(indices) == 'table') then
        indices = {indices}
    end

    c = 1
    dZSpectrum = {}

    for i in ipairs(T) do
        for k in ipairs(Psis) do
            if ValueInTable(i, indices) then
                table.insert(dZSpectrum, dZSpectra[c])
            else
                table.insert(dZSpectrum, 0)
            end
            c = c + 1
        end
    end

    return Spectra.Sum(G, dZSpectrum)
end

function SaveSpectrum(G, suffix)
    -- Scale, broaden, and save the spectrum to disk.
    G = -1 / math.pi * G

    Gmin1 = $Gmin1 - Gamma
    Gmax1 = $Gmax1 - Gamma
    Egamma1 = ($Egamma1 - Eedge1) + DeltaE
    G.Broaden(0, {{Emin, Gmin1}, {Egamma1, Gmin1}, {Egamma1, Gmax1}, {Emax, Gmax1}})

    G.Print({{'file', '$BaseName_' .. suffix .. '.spec'}})
end

--------------------------------------------------------------------------------
-- Define the transition operators.
--------------------------------------------------------------------------------
t = math.sqrt(1/2)

Txy_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t * I}, {2, 2, -t * I}})
Txz_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t    }, {2, 1, -t    }})
Tyz_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -1, t * I}, {2, 1,  t * I}})
Tx2y2_1s_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2, -2, t    }, {2, 2,  t    }})
Tz2_1s_3d   = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, IndexUp_1s, IndexDn_1s, {{2,  0, 1    }                })

if H_3d_4p_hybridization == 1 then
    Tx_1s_4p = NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1, -1, t    }, {1, 1, -t    }})
    Ty_1s_4p = NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1, -1, t * I}, {1, 1,  t * I}})
    Tz_1s_4p = NewOperator('CF', NFermions, IndexUp_4p, IndexDn_4p, IndexUp_1s, IndexDn_1s, {{1,  0, 1    }                })
end

k = $k1
ev = $eps11
eh = $eps12

-- Calculate the right and left polarization vectors.
er = {t * (eh[1] - I * ev[1]),
      t * (eh[2] - I * ev[2]),
      t * (eh[3] - I * ev[3])}

el = {-t * (eh[1] + I * ev[1]),
      -t * (eh[2] + I * ev[2]),
      -t * (eh[3] + I * ev[3])}

function CalculateT(e, k)
    -- Calculate the transition operator for arbitrary
    -- polarization and wave vectors.
    if k == nil then
        T = e[1] * Tx_1s_4p + e[2] * Ty_1s_4p + e[3] * Tz_1s_4p
    else
        T = (e[1] * k[2] + e[2] * k[1]) * Txy_1s_3d
          + (e[1] * k[3] + e[3] * k[1]) * Txz_1s_3d
          + (e[2] * k[3] + e[3] * k[2]) * Tyz_1s_3d
          + (e[1] * k[1] + e[2] * k[2]) * Tx2y2_1s_3d
          + e[3] * k[3] * Tz2_1s_3d
    end
    return Chop(T)
end

Tv_1s_3d = CalculateT(ev, k)
Th_1s_3d = CalculateT(eh, k)
Tr_1s_3d = CalculateT(er, k)
Tl_1s_3d = CalculateT(el, k)
Tk_1s_3d = CalculateT(k, k)

if H_3d_4p_hybridization == 1 then
    Tv_1s_4p = CalculateT(ev)
    Th_1s_4p = CalculateT(eh)
    Tr_1s_4p = CalculateT(er)
    Tl_1s_4p = CalculateT(el)
    Tk_1s_4p = CalculateT(k)
end


-- List with the user selected spectra.
spectra = {$spectra}

-- Create two lists, one with the operators and the second with
-- the indices of the operators required to calculate a given
-- spectrum.
T_1s_3d = {}
indices_1s_3d = {}
c = 1

spectrum = 'Isotropic'
if ValueInTable(spectrum, spectra) then
    indices_1s_3d[spectrum] = {}
    for j, operator in ipairs({Txy_1s_3d, Txz_1s_3d, Tyz_1s_3d, Tx2y2_1s_3d, Tz2_1s_3d}) do
        table.insert(T_1s_3d, operator)
        table.insert(indices_1s_3d[spectrum], c)
        c = c + 1
    end
end

spectrum = 'Circular Dichroism'
if ValueInTable(spectrum, spectra) then
    indices_1s_3d[spectrum] = {}
    for j, operator in ipairs({Tr_1s_3d, Tl_1s_3d}) do
        table.insert(T_1s_3d, operator)
        table.insert(indices_1s_3d[spectrum], c)
        c = c + 1
    end
end

spectrum = 'Linear Dichroism'
if ValueInTable(spectrum, spectra) then
    indices_1s_3d[spectrum] = {}
    for j, operator in ipairs({Tv_1s_3d, Th_1s_3d}) do
        table.insert(T_1s_3d, operator)
        table.insert(indices_1s_3d[spectrum], c)
        c = c + 1
    end
end

if H_3d_4p_hybridization == 1 then
    T_1s_4p = {}
    indices_1s_4p = {}
    c = 1

    spectrum = 'Isotropic'
    if ValueInTable(spectrum, spectra) then
        indices_1s_4p[spectrum] = {}
        for j, operator in ipairs({Tx_1s_4p, Ty_1s_4p, Tz_1s_4p}) do
            table.insert(T_1s_4p, operator)
            table.insert(indices_1s_4p[spectrum], c)
            c = c + 1
        end
    end

    spectrum = 'Circular Dichroism'
    if ValueInTable(spectrum, spectra) then
        indices_1s_4p[spectrum] = {}
        for j, operator in ipairs({Tr_1s_4p, Tl_1s_4p}) do
            table.insert(T_1s_4p, operator)
            table.insert(indices_1s_4p[spectrum], c)
            c = c + 1
        end
    end

    spectrum = 'Linear Dichroism'
    if ValueInTable(spectrum, spectra) then
        indices_1s_4p[spectrum] = {}
        for j, operator in ipairs({Tv_1s_4p, Th_1s_4p}) do
            table.insert(T_1s_4p, operator)
            table.insert(indices_1s_4p[spectrum], c)
            c = c + 1
        end
    end
end

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
Sk = Chop(k[1] * Sx + k[2] * Sy + k[3] * Sz)
Lk = Chop(k[1] * Lx + k[2] * Ly + k[3] * Lz)
Jk = Chop(k[1] * Jx + k[2] * Jy + k[3] * Jz)
Tk = Chop(k[1] * Tx + k[2] * Ty + k[3] * Tz)

Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_1s, N_3d, 'dZ'}
header = 'Analysis of the initial Hamiltonian:\n'
header = header .. '=================================================================================================================================\n'
header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_1s>    <N_3d>          dZ\n'
header = header .. '=================================================================================================================================\n'
footer = '=================================================================================================================================\n'

if H_3d_4p_hybridization == 1 then
    Operators = {H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_1s, N_3d, N_4p, 'dZ'}
    header = 'Analysis of the initial Hamiltonian:\n'
    header = header .. '===========================================================================================================================================\n'
    header = header .. 'State         <E>     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_1s>    <N_3d>    <N_4p>          dZ\n'
    header = header .. '===========================================================================================================================================\n'
    footer = '===========================================================================================================================================\n'
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


if next(spectra) == nil then
    return
end

E_gs_i = Psis_i[1] * H_i * Psis_i[1]

if CalculationRestrictions == nil then
    Psis_f = Eigensystem(H_f, FinalRestrictions, 1)
else
    Psis_f = Eigensystem(H_f, FinalRestrictions, 1, {{'restrictions', CalculationRestrictions}})
end

Psis_f = {Psis_f}
E_gs_f = Psis_f[1] * H_f * Psis_f[1]

Eedge1 = $Eedge1
DeltaE = E_gs_f - E_gs_i

Emin = ($Emin1 - Eedge1) + DeltaE
Emax = ($Emax1 - Eedge1) + DeltaE
NE = $NE1
Gamma = $Gamma1
DenseBorder = $DenseBorder

if H_3d_4p_hybridization == 1 then
    -- Calculate the spectra. Note that the CalculationRestrictions are always active in this case.
    G_1s_3d = CreateSpectra(H_f, T_1s_3d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}, {'DenseBorder', DenseBorder}})
    G_1s_4p = CreateSpectra(H_f, T_1s_4p, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}, {'DenseBorder', DenseBorder}})

    -- Calculate the prefactors for the two spectra (see http://dx.doi.org/10.1103/PhysRevB.94.245115)
    -- Note that in the publication Iedge1 doesn't appear in equations 9 and 10. Iedge1 is just
    -- a scale factor for the intensity of the edge, and in the publication is set to the experimental
    -- edge jump. Here it is set to make the quadrupolar prefactor 1. In this way the spectra with and without
    -- pd-hybridization can be more easily compared.
    alpha = 7.2973525664E-3
    a0 = 5.2917721067E-1
    hbar = 6.582119514E-16
    c = 2.99792458E+18

    P1_1s_4p = $P1(1s,4p)
    P2_1s_3d = $P2(1s,3d)

    prefactor_1s_3d = 4 * math.pi^2 * alpha * a0^4 / (2 * hbar * c)^2 * P2_1s_3d^2 * Eedge1^3
    prefactor_1s_4p = 4 * math.pi^2 * alpha * a0^2                    * P1_1s_4p^2 * Eedge1

    Iedge1 = prefactor_1s_3d

    prefactor_1s_3d = prefactor_1s_3d / Iedge1
    prefactor_1s_4p = prefactor_1s_4p / Iedge1

    G_1s_3d = prefactor_1s_3d * G_1s_3d
    G_1s_4p = prefactor_1s_4p * G_1s_4p
else
    if CalculationRestrictions == nil then
        G_1s_3d = CreateSpectra(H_f, T_1s_3d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'DenseBorder', DenseBorder}})
    else
        G_1s_3d = CreateSpectra(H_f, T_1s_3d, Psis_i, {{'Emin', Emin}, {'Emax', Emax}, {'NE', NE}, {'Gamma', Gamma}, {'restrictions', CalculationRestrictions}, {'DenseBorder', DenseBorder}})
    end
end

-- Create a list with the Boltzmann probabilities for a given operator
-- and state.
dZ_1s_3d = {}
for i in ipairs(T_1s_3d) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_1s_3d, dZ[j])
    end
end

if H_3d_4p_hybridization == 1 then
    dZ_1s_4p = {}
    for i in ipairs(T_1s_4p) do
        for j in ipairs(Psis_i) do
            table.insert(dZ_1s_4p, dZ[j])
        end
    end
end

if H_3d_4p_hybridization == 1 then
    spectrum = 'Isotropic'
    if ValueInTable(spectrum, spectra) then
        Giso_1s_3d = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum], dZ_1s_3d)
        Giso_1s_4p = GetSpectrum(G_1s_4p, T_1s_4p, Psis_i, indices_1s_4p[spectrum], dZ_1s_4p)
        Giso = Giso_1s_3d / 15 + Giso_1s_4p / 3
        SaveSpectrum(Giso, 'iso')
    end

    spectrum = 'Circular Dichroism'
    if ValueInTable(spectrum, spectra) then
        Gr_1s_3d = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][1], dZ_1s_3d)
        Gl_1s_3d = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][2], dZ_1s_3d)
        Gr_1s_4p = GetSpectrum(G_1s_4p, T_1s_4p, Psis_i, indices_1s_4p[spectrum][1], dZ_1s_4p)
        Gl_1s_4p = GetSpectrum(G_1s_4p, T_1s_4p, Psis_i, indices_1s_4p[spectrum][2], dZ_1s_4p)
        Gr = Gr_1s_3d + Gr_1s_4p
        Gl = Gl_1s_3d + Gl_1s_4p
        SaveSpectrum(Gr, 'r')
        SaveSpectrum(Gl, 'l')
        SaveSpectrum(Gr - Gl, 'cd')
    end

    spectrum = 'Linear Dichroism'
    if ValueInTable(spectrum, spectra) then
        Gv_1s_3d = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][1], dZ_1s_3d)
        Gh_1s_3d = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][2], dZ_1s_3d)
        Gv_1s_4p = GetSpectrum(G_1s_4p, T_1s_4p, Psis_i, indices_1s_4p[spectrum][1], dZ_1s_4p)
        Gh_1s_4p = GetSpectrum(G_1s_4p, T_1s_4p, Psis_i, indices_1s_4p[spectrum][2], dZ_1s_4p)
        Gv = Gv_1s_3d + Gv_1s_4p
        Gh = Gh_1s_3d + Gh_1s_4p
        SaveSpectrum(Gv, 'v')
        SaveSpectrum(Gh, 'h')
        SaveSpectrum(Gv - Gh, 'ld')
    end
else
    spectrum = 'Isotropic'
    if ValueInTable(spectrum, spectra) then
        Giso = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum], dZ_1s_3d)
        Giso = Giso / 15
        SaveSpectrum(Giso, 'iso')
    end

    spectrum = 'Circular Dichroism'
    if ValueInTable(spectrum, spectra) then
        Gr = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][1], dZ_1s_3d)
        Gl = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][2], dZ_1s_3d)
        SaveSpectrum(Gr, 'r')
        SaveSpectrum(Gl, 'l')
        SaveSpectrum(Gr - Gl, 'cd')
    end

    spectrum = 'Linear Dichroism'
    if ValueInTable(spectrum, spectra) then
        Gv = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][1], dZ_1s_3d)
        Gh = GetSpectrum(G_1s_3d, T_1s_3d, Psis_i, indices_1s_3d[spectrum][2], dZ_1s_3d)
        SaveSpectrum(Gv, 'v')
        SaveSpectrum(Gh, 'h')
        SaveSpectrum(Gv - Gh, 'ld')
    end
end

