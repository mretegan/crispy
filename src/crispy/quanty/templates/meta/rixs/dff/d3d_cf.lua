--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3d crystal field for f electrons in the Zy orientation (C3 axis along z, a
    -- basal C2 axis along y), taken from the Quanty point-group tables:
    -- https://www.quanty.org/physics_chemistry/point_groups/d3d/orientation_zy
    --
    -- The seven #m orbitals (l = 3, ungerade) split into a1u + 2 a2u + 2 eu. The
    -- two a2u orbitals share an irrep and mix through Ma2u; likewise the two eu
    -- doublets mix through Meu. The independent parameters are therefore the five
    -- diagonal energies (Ea1u, Ea2uA, Ea2uB, Eeu1, Eeu2) and the two off-diagonal
    -- mixing elements (Ma2u, Meu). The diagonal energies are referenced to their
    -- (degeneracy-weighted) average so the k = 0 monopole vanishes.
    Eav_#m_i = ($Ea1u(#m)_i_value + $Ea2uA(#m)_i_value + $Ea2uB(#m)_i_value + 2 * $Eeu1(#m)_i_value + 2 * $Eeu2(#m)_i_value) / 7
    Ea1u_#m_i = $Ea1u(#m)_i_value - Eav_#m_i
    Ea2uA_#m_i = $Ea2uA(#m)_i_value - Eav_#m_i
    Ea2uB_#m_i = $Ea2uB(#m)_i_value - Eav_#m_i
    Eeu1_#m_i = $Eeu1(#m)_i_value - Eav_#m_i
    Eeu2_#m_i = $Eeu2(#m)_i_value - Eav_#m_i
    Ma2u_#m_i = $Ma2u(#m)_i_value
    Meu_#m_i = $Meu(#m)_i_value

    Akm_#m_i = {
        {0, 0, (1 / 7) * (Ea1u_#m_i + Ea2uA_#m_i + Ea2uB_#m_i + 2 * Eeu1_#m_i + 2 * Eeu2_#m_i)},
        {2, 0, (-5 / 28) * (5 * Ea1u_#m_i + 5 * Ea2uA_#m_i - 4 * Ea2uB_#m_i - 6 * Eeu1_#m_i)},
        {4, 0, (3 / 14) * (3 * Ea1u_#m_i + 3 * Ea2uA_#m_i + 2 * (3 * Ea2uB_#m_i + Eeu1_#m_i - 7 * Eeu2_#m_i))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma2u_#m_i + 6 * Meu_#m_i)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma2u_#m_i + 2 * Meu_#m_i)},
        {6, 0, (-13 / 140) * (Ea1u_#m_i + Ea2uA_#m_i - 20 * Ea2uB_#m_i + 30 * Eeu1_#m_i - 12 * Eeu2_#m_i)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma2u_#m_i - 3 * Meu_#m_i))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma2u_#m_i - 3 * Meu_#m_i))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#m_i - Ea2uA_#m_i))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#m_i - Ea2uA_#m_i))}
    }

    io.write("Initial-state D3d crystal field Hamiltonian (a1u, a2u, eu) diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1u     %8.3f\n", Ea1u_#m_i))
    io.write(string.format("a2u(A)  %8.3f\n", Ea2uA_#m_i))
    io.write(string.format("a2u(B)  %8.3f\n", Ea2uB_#m_i))
    io.write(string.format("eu(1)   %8.3f\n", Eeu1_#m_i))
    io.write(string.format("eu(2)   %8.3f\n", Eeu2_#m_i))
    io.write("================\n")
    io.write(string.format("Off-diagonal elements: <a2u(A)|H|a2u(B)> = %.3f, <eu(1)|H|eu(2)> = %.3f.\n", Ma2u_#m_i, Meu_#m_i))
    io.write("\n")

    Eav_#m_m = ($Ea1u(#m)_m_value + $Ea2uA(#m)_m_value + $Ea2uB(#m)_m_value + 2 * $Eeu1(#m)_m_value + 2 * $Eeu2(#m)_m_value) / 7
    Ea1u_#m_m = $Ea1u(#m)_m_value - Eav_#m_m
    Ea2uA_#m_m = $Ea2uA(#m)_m_value - Eav_#m_m
    Ea2uB_#m_m = $Ea2uB(#m)_m_value - Eav_#m_m
    Eeu1_#m_m = $Eeu1(#m)_m_value - Eav_#m_m
    Eeu2_#m_m = $Eeu2(#m)_m_value - Eav_#m_m
    Ma2u_#m_m = $Ma2u(#m)_m_value
    Meu_#m_m = $Meu(#m)_m_value

    Akm_#m_m = {
        {0, 0, (1 / 7) * (Ea1u_#m_m + Ea2uA_#m_m + Ea2uB_#m_m + 2 * Eeu1_#m_m + 2 * Eeu2_#m_m)},
        {2, 0, (-5 / 28) * (5 * Ea1u_#m_m + 5 * Ea2uA_#m_m - 4 * Ea2uB_#m_m - 6 * Eeu1_#m_m)},
        {4, 0, (3 / 14) * (3 * Ea1u_#m_m + 3 * Ea2uA_#m_m + 2 * (3 * Ea2uB_#m_m + Eeu1_#m_m - 7 * Eeu2_#m_m))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma2u_#m_m + 6 * Meu_#m_m)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma2u_#m_m + 2 * Meu_#m_m)},
        {6, 0, (-13 / 140) * (Ea1u_#m_m + Ea2uA_#m_m - 20 * Ea2uB_#m_m + 30 * Eeu1_#m_m - 12 * Eeu2_#m_m)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma2u_#m_m - 3 * Meu_#m_m))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma2u_#m_m - 3 * Meu_#m_m))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#m_m - Ea2uA_#m_m))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#m_m - Ea2uA_#m_m))}
    }

    Eav_#m_f = ($Ea1u(#m)_f_value + $Ea2uA(#m)_f_value + $Ea2uB(#m)_f_value + 2 * $Eeu1(#m)_f_value + 2 * $Eeu2(#m)_f_value) / 7
    Ea1u_#m_f = $Ea1u(#m)_f_value - Eav_#m_f
    Ea2uA_#m_f = $Ea2uA(#m)_f_value - Eav_#m_f
    Ea2uB_#m_f = $Ea2uB(#m)_f_value - Eav_#m_f
    Eeu1_#m_f = $Eeu1(#m)_f_value - Eav_#m_f
    Eeu2_#m_f = $Eeu2(#m)_f_value - Eav_#m_f
    Ma2u_#m_f = $Ma2u(#m)_f_value
    Meu_#m_f = $Meu(#m)_f_value

    Akm_#m_f = {
        {0, 0, (1 / 7) * (Ea1u_#m_f + Ea2uA_#m_f + Ea2uB_#m_f + 2 * Eeu1_#m_f + 2 * Eeu2_#m_f)},
        {2, 0, (-5 / 28) * (5 * Ea1u_#m_f + 5 * Ea2uA_#m_f - 4 * Ea2uB_#m_f - 6 * Eeu1_#m_f)},
        {4, 0, (3 / 14) * (3 * Ea1u_#m_f + 3 * Ea2uA_#m_f + 2 * (3 * Ea2uB_#m_f + Eeu1_#m_f - 7 * Eeu2_#m_f))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma2u_#m_f + 6 * Meu_#m_f)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma2u_#m_f + 2 * Meu_#m_f)},
        {6, 0, (-13 / 140) * (Ea1u_#m_f + Ea2uA_#m_f - 20 * Ea2uB_#m_f + 30 * Eeu1_#m_f - 12 * Eeu2_#m_f)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma2u_#m_f - 3 * Meu_#m_f))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma2u_#m_f - 3 * Meu_#m_f))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#m_f - Ea2uA_#m_f))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#m_f - Ea2uA_#m_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_f))
end
