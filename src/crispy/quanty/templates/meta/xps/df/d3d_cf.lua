--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3d crystal field for f electrons in the Zy orientation (C3 axis along z, a
    -- basal C2 axis along y), taken from the Quanty point-group tables:
    -- https://www.quanty.org/physics_chemistry/point_groups/d3d/orientation_zy
    --
    -- The seven #f orbitals (l = 3, ungerade) split into a1u + 2 a2u + 2 eu. The
    -- two a2u orbitals share an irrep and mix through Ma2u; likewise the two eu
    -- doublets mix through Meu. The independent parameters are therefore the five
    -- diagonal energies (Ea1u, Ea2uA, Ea2uB, Eeu1, Eeu2) and the two off-diagonal
    -- mixing elements (Ma2u, Meu). The diagonal energies are referenced to their
    -- (degeneracy-weighted) average so the k = 0 monopole vanishes.
    Eav_#f_i = ($Ea1u(#f)_i_value + $Ea2uA(#f)_i_value + $Ea2uB(#f)_i_value + 2 * $Eeu1(#f)_i_value + 2 * $Eeu2(#f)_i_value) / 7
    Ea1u_#f_i = $Ea1u(#f)_i_value - Eav_#f_i
    Ea2uA_#f_i = $Ea2uA(#f)_i_value - Eav_#f_i
    Ea2uB_#f_i = $Ea2uB(#f)_i_value - Eav_#f_i
    Eeu1_#f_i = $Eeu1(#f)_i_value - Eav_#f_i
    Eeu2_#f_i = $Eeu2(#f)_i_value - Eav_#f_i
    Ma2u_#f_i = $Ma2u(#f)_i_value
    Meu_#f_i = $Meu(#f)_i_value

    Akm_#f_i = {
        {0, 0, (1 / 7) * (Ea1u_#f_i + Ea2uA_#f_i + Ea2uB_#f_i + 2 * Eeu1_#f_i + 2 * Eeu2_#f_i)},
        {2, 0, (-5 / 28) * (5 * Ea1u_#f_i + 5 * Ea2uA_#f_i - 4 * Ea2uB_#f_i - 6 * Eeu1_#f_i)},
        {4, 0, (3 / 14) * (3 * Ea1u_#f_i + 3 * Ea2uA_#f_i + 2 * (3 * Ea2uB_#f_i + Eeu1_#f_i - 7 * Eeu2_#f_i))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma2u_#f_i + 6 * Meu_#f_i)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma2u_#f_i + 2 * Meu_#f_i)},
        {6, 0, (-13 / 140) * (Ea1u_#f_i + Ea2uA_#f_i - 20 * Ea2uB_#f_i + 30 * Eeu1_#f_i - 12 * Eeu2_#f_i)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma2u_#f_i - 3 * Meu_#f_i))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma2u_#f_i - 3 * Meu_#f_i))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#f_i - Ea2uA_#f_i))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#f_i - Ea2uA_#f_i))}
    }

    io.write("Initial-state D3d crystal field Hamiltonian (a1u, a2u, eu) diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1u     %8.3f\n", Ea1u_#f_i))
    io.write(string.format("a2u(A)  %8.3f\n", Ea2uA_#f_i))
    io.write(string.format("a2u(B)  %8.3f\n", Ea2uB_#f_i))
    io.write(string.format("eu(1)   %8.3f\n", Eeu1_#f_i))
    io.write(string.format("eu(2)   %8.3f\n", Eeu2_#f_i))
    io.write("================\n")
    io.write(string.format("Off-diagonal elements: <a2u(A)|H|a2u(B)> = %.3f, <eu(1)|H|eu(2)> = %.3f.\n", Ma2u_#f_i, Meu_#f_i))
    io.write("\n")

    Eav_#f_f = ($Ea1u(#f)_f_value + $Ea2uA(#f)_f_value + $Ea2uB(#f)_f_value + 2 * $Eeu1(#f)_f_value + 2 * $Eeu2(#f)_f_value) / 7
    Ea1u_#f_f = $Ea1u(#f)_f_value - Eav_#f_f
    Ea2uA_#f_f = $Ea2uA(#f)_f_value - Eav_#f_f
    Ea2uB_#f_f = $Ea2uB(#f)_f_value - Eav_#f_f
    Eeu1_#f_f = $Eeu1(#f)_f_value - Eav_#f_f
    Eeu2_#f_f = $Eeu2(#f)_f_value - Eav_#f_f
    Ma2u_#f_f = $Ma2u(#f)_f_value
    Meu_#f_f = $Meu(#f)_f_value

    Akm_#f_f = {
        {0, 0, (1 / 7) * (Ea1u_#f_f + Ea2uA_#f_f + Ea2uB_#f_f + 2 * Eeu1_#f_f + 2 * Eeu2_#f_f)},
        {2, 0, (-5 / 28) * (5 * Ea1u_#f_f + 5 * Ea2uA_#f_f - 4 * Ea2uB_#f_f - 6 * Eeu1_#f_f)},
        {4, 0, (3 / 14) * (3 * Ea1u_#f_f + 3 * Ea2uA_#f_f + 2 * (3 * Ea2uB_#f_f + Eeu1_#f_f - 7 * Eeu2_#f_f))},
        {4, 3, (1 / sqrt(14)) * (9 * Ma2u_#f_f + 6 * Meu_#f_f)},
        {4, -3, -3 * (1 / sqrt(14)) * (3 * Ma2u_#f_f + 2 * Meu_#f_f)},
        {6, 0, (-13 / 140) * (Ea1u_#f_f + Ea2uA_#f_f - 20 * Ea2uB_#f_f + 30 * Eeu1_#f_f - 12 * Eeu2_#f_f)},
        {6, 3, (-13 / 5) * (sqrt(3 / 14) * (Ma2u_#f_f - 3 * Meu_#f_f))},
        {6, -3, (13 / 5) * (sqrt(3 / 14) * (Ma2u_#f_f - 3 * Meu_#f_f))},
        {6, -6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#f_f - Ea2uA_#f_f))},
        {6, 6, (-13 / 20) * (sqrt(33 / 7) * (Ea1u_#f_f - Ea2uA_#f_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_i))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_f))
end
