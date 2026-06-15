--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- C3v crystal field for f electrons: the three-fold C3 axis is along z and a
    -- vertical mirror plane sigma_v contains the y-axis (equivalent to the
    -- inversion-related Quanty D3d "Zy" setting). The seven #m orbitals split into
    -- 2 a1 + a2 + 2 e (the two a1 sets mix through Ma1, the two e sets through Me);
    -- energies are referenced to their (degeneracy-weighted) average so the k = 0
    -- monopole vanishes. The Akm expansion is taken from the Quanty point-group
    -- tables (https://www.quanty.org/physics_chemistry/point_groups).
    Eav_#m_i = ($Ea2(#m)_i_value + $Ea1A(#m)_i_value + $Ea1B(#m)_i_value + 2 * $Ee1(#m)_i_value + 2 * $Ee2(#m)_i_value) / 7
    Ea2_#m_i = $Ea2(#m)_i_value - Eav_#m_i
    Ea1A_#m_i = $Ea1A(#m)_i_value - Eav_#m_i
    Ea1B_#m_i = $Ea1B(#m)_i_value - Eav_#m_i
    Ee1_#m_i = $Ee1(#m)_i_value - Eav_#m_i
    Ee2_#m_i = $Ee2(#m)_i_value - Eav_#m_i
    Ma1_#m_i = $Ma1(#m)_i_value
    Me_#m_i = $Me(#m)_i_value

    Akm_#m_i = {
        {0, 0, (1 / 7) * (Ea2_#m_i + Ea1A_#m_i + Ea1B_#m_i + 2 * Ee1_#m_i + 2 * Ee2_#m_i)},
        {2, 0, (-5 / 28) * (5 * Ea2_#m_i + 5 * Ea1A_#m_i - 4 * Ea1B_#m_i - 6 * Ee1_#m_i)},
        {4, 0, (3 / 14) * (3 * Ea2_#m_i + 3 * Ea1A_#m_i + 2 * (3 * Ea1B_#m_i + Ee1_#m_i - 7 * Ee2_#m_i))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma1_#m_i + 6 * Me_#m_i)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma1_#m_i + 2 * Me_#m_i)},
        {6, 0, (-13 / 140) * (Ea2_#m_i + Ea1A_#m_i - 20 * Ea1B_#m_i + 30 * Ee1_#m_i - 12 * Ee2_#m_i)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma1_#m_i - 3 * Me_#m_i))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma1_#m_i - 3 * Me_#m_i))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea2_#m_i - Ea1A_#m_i))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea2_#m_i - Ea1A_#m_i))}
    }

    io.write("Initial-state C3v crystal field Hamiltonian (a1, a2, e) diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("%-7s %8.3f\n", "a2", Ea2_#m_i))
    io.write(string.format("%-7s %8.3f\n", "a1(A)", Ea1A_#m_i))
    io.write(string.format("%-7s %8.3f\n", "a1(B)", Ea1B_#m_i))
    io.write(string.format("%-7s %8.3f\n", "e(1)", Ee1_#m_i))
    io.write(string.format("%-7s %8.3f\n", "e(2)", Ee2_#m_i))
    io.write("================\n")
    io.write(string.format("Off-diagonal elements: <a1(A)|H|a1(B)> = %.3f, <e(1)|H|e(2)> = %.3f.\n", Ma1_#m_i, Me_#m_i))
    io.write("\n")

    Eav_#m_m = ($Ea2(#m)_m_value + $Ea1A(#m)_m_value + $Ea1B(#m)_m_value + 2 * $Ee1(#m)_m_value + 2 * $Ee2(#m)_m_value) / 7
    Ea2_#m_m = $Ea2(#m)_m_value - Eav_#m_m
    Ea1A_#m_m = $Ea1A(#m)_m_value - Eav_#m_m
    Ea1B_#m_m = $Ea1B(#m)_m_value - Eav_#m_m
    Ee1_#m_m = $Ee1(#m)_m_value - Eav_#m_m
    Ee2_#m_m = $Ee2(#m)_m_value - Eav_#m_m
    Ma1_#m_m = $Ma1(#m)_m_value
    Me_#m_m = $Me(#m)_m_value

    Akm_#m_m = {
        {0, 0, (1 / 7) * (Ea2_#m_m + Ea1A_#m_m + Ea1B_#m_m + 2 * Ee1_#m_m + 2 * Ee2_#m_m)},
        {2, 0, (-5 / 28) * (5 * Ea2_#m_m + 5 * Ea1A_#m_m - 4 * Ea1B_#m_m - 6 * Ee1_#m_m)},
        {4, 0, (3 / 14) * (3 * Ea2_#m_m + 3 * Ea1A_#m_m + 2 * (3 * Ea1B_#m_m + Ee1_#m_m - 7 * Ee2_#m_m))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma1_#m_m + 6 * Me_#m_m)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma1_#m_m + 2 * Me_#m_m)},
        {6, 0, (-13 / 140) * (Ea2_#m_m + Ea1A_#m_m - 20 * Ea1B_#m_m + 30 * Ee1_#m_m - 12 * Ee2_#m_m)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma1_#m_m - 3 * Me_#m_m))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma1_#m_m - 3 * Me_#m_m))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea2_#m_m - Ea1A_#m_m))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea2_#m_m - Ea1A_#m_m))}
    }

    Eav_#m_f = ($Ea2(#m)_f_value + $Ea1A(#m)_f_value + $Ea1B(#m)_f_value + 2 * $Ee1(#m)_f_value + 2 * $Ee2(#m)_f_value) / 7
    Ea2_#m_f = $Ea2(#m)_f_value - Eav_#m_f
    Ea1A_#m_f = $Ea1A(#m)_f_value - Eav_#m_f
    Ea1B_#m_f = $Ea1B(#m)_f_value - Eav_#m_f
    Ee1_#m_f = $Ee1(#m)_f_value - Eav_#m_f
    Ee2_#m_f = $Ee2(#m)_f_value - Eav_#m_f
    Ma1_#m_f = $Ma1(#m)_f_value
    Me_#m_f = $Me(#m)_f_value

    Akm_#m_f = {
        {0, 0, (1 / 7) * (Ea2_#m_f + Ea1A_#m_f + Ea1B_#m_f + 2 * Ee1_#m_f + 2 * Ee2_#m_f)},
        {2, 0, (-5 / 28) * (5 * Ea2_#m_f + 5 * Ea1A_#m_f - 4 * Ea1B_#m_f - 6 * Ee1_#m_f)},
        {4, 0, (3 / 14) * (3 * Ea2_#m_f + 3 * Ea1A_#m_f + 2 * (3 * Ea1B_#m_f + Ee1_#m_f - 7 * Ee2_#m_f))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma1_#m_f + 6 * Me_#m_f)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma1_#m_f + 2 * Me_#m_f)},
        {6, 0, (-13 / 140) * (Ea2_#m_f + Ea1A_#m_f - 20 * Ea1B_#m_f + 30 * Ee1_#m_f - 12 * Ee2_#m_f)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma1_#m_f - 3 * Me_#m_f))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma1_#m_f - 3 * Me_#m_f))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea2_#m_f - Ea1A_#m_f))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea2_#m_f - Ea1A_#m_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_f))
end
