--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- Td crystal field for f electrons, cube-axis (xyz) setting: the tetrahedron is
    -- inscribed in a cube with edges along x, y and z (S4/C2 axes along x, y, z;
    -- C3 axes along the cube diagonals [+-1, +-1, +-1]). The seven #m orbitals
    -- split into a2 + t1 + t2; energies are referenced to their (degeneracy-weighted)
    -- average so the k = 0 monopole vanishes. The Akm expansion is taken from the
    -- Quanty point-group tables (https://www.quanty.org/physics_chemistry/point_groups).
    Eav_#m_i = ($Ea2(#m)_i_value + 3 * $Et1(#m)_i_value + 3 * $Et2(#m)_i_value) / 7
    Ea2_#m_i = $Ea2(#m)_i_value - Eav_#m_i
    Et1_#m_i = $Et1(#m)_i_value - Eav_#m_i
    Et2_#m_i = $Et2(#m)_i_value - Eav_#m_i

    Akm_#m_i = {
        {0, 0, (1 / 7) * (Ea2_#m_i + 3 * (Et1_#m_i + Et2_#m_i))},
        {4, 0, (-3 / 4) * (2 * Ea2_#m_i + Et1_#m_i - 3 * Et2_#m_i)},
        {4, -4, (-3 / 4) * (sqrt(5 / 14) * (2 * Ea2_#m_i + Et1_#m_i - 3 * Et2_#m_i))},
        {4, 4, (-3 / 4) * (sqrt(5 / 14) * (2 * Ea2_#m_i + Et1_#m_i - 3 * Et2_#m_i))},
        {6, 0, (39 / 280) * (4 * Ea2_#m_i - 9 * Et1_#m_i + 5 * Et2_#m_i)},
        {6, -4, (-39 / 40) * ((1 / sqrt(14)) * (4 * Ea2_#m_i - 9 * Et1_#m_i + 5 * Et2_#m_i))},
        {6, 4, (-39 / 40) * ((1 / sqrt(14)) * (4 * Ea2_#m_i - 9 * Et1_#m_i + 5 * Et2_#m_i))}
    }

    io.write("Initial-state Td crystal field Hamiltonian (a2, t1, t2) diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("%-7s %8.3f\n", "a2", Ea2_#m_i))
    io.write(string.format("%-7s %8.3f\n", "t1", Et1_#m_i))
    io.write(string.format("%-7s %8.3f\n", "t2", Et2_#m_i))
    io.write("================\n")
    io.write("\n")

    Eav_#m_m = ($Ea2(#m)_m_value + 3 * $Et1(#m)_m_value + 3 * $Et2(#m)_m_value) / 7
    Ea2_#m_m = $Ea2(#m)_m_value - Eav_#m_m
    Et1_#m_m = $Et1(#m)_m_value - Eav_#m_m
    Et2_#m_m = $Et2(#m)_m_value - Eav_#m_m

    Akm_#m_m = {
        {0, 0, (1 / 7) * (Ea2_#m_m + 3 * (Et1_#m_m + Et2_#m_m))},
        {4, 0, (-3 / 4) * (2 * Ea2_#m_m + Et1_#m_m - 3 * Et2_#m_m)},
        {4, -4, (-3 / 4) * (sqrt(5 / 14) * (2 * Ea2_#m_m + Et1_#m_m - 3 * Et2_#m_m))},
        {4, 4, (-3 / 4) * (sqrt(5 / 14) * (2 * Ea2_#m_m + Et1_#m_m - 3 * Et2_#m_m))},
        {6, 0, (39 / 280) * (4 * Ea2_#m_m - 9 * Et1_#m_m + 5 * Et2_#m_m)},
        {6, -4, (-39 / 40) * ((1 / sqrt(14)) * (4 * Ea2_#m_m - 9 * Et1_#m_m + 5 * Et2_#m_m))},
        {6, 4, (-39 / 40) * ((1 / sqrt(14)) * (4 * Ea2_#m_m - 9 * Et1_#m_m + 5 * Et2_#m_m))}
    }

    Eav_#m_f = ($Ea2(#m)_f_value + 3 * $Et1(#m)_f_value + 3 * $Et2(#m)_f_value) / 7
    Ea2_#m_f = $Ea2(#m)_f_value - Eav_#m_f
    Et1_#m_f = $Et1(#m)_f_value - Eav_#m_f
    Et2_#m_f = $Et2(#m)_f_value - Eav_#m_f

    Akm_#m_f = {
        {0, 0, (1 / 7) * (Ea2_#m_f + 3 * (Et1_#m_f + Et2_#m_f))},
        {4, 0, (-3 / 4) * (2 * Ea2_#m_f + Et1_#m_f - 3 * Et2_#m_f)},
        {4, -4, (-3 / 4) * (sqrt(5 / 14) * (2 * Ea2_#m_f + Et1_#m_f - 3 * Et2_#m_f))},
        {4, 4, (-3 / 4) * (sqrt(5 / 14) * (2 * Ea2_#m_f + Et1_#m_f - 3 * Et2_#m_f))},
        {6, 0, (39 / 280) * (4 * Ea2_#m_f - 9 * Et1_#m_f + 5 * Et2_#m_f)},
        {6, -4, (-39 / 40) * ((1 / sqrt(14)) * (4 * Ea2_#m_f - 9 * Et1_#m_f + 5 * Et2_#m_f))},
        {6, 4, (-39 / 40) * ((1 / sqrt(14)) * (4 * Ea2_#m_f - 9 * Et1_#m_f + 5 * Et2_#m_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_f))
end
