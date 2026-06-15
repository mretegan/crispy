--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D4h crystal field for f electrons, Quanty "zxy" setting: the four-fold C4 axis
    -- is along z and the C2' axes / vertical mirror planes lie along x and y. The
    -- seven #m orbitals split into a2u + b1u + b2u + 2 eu (the two eu sets mix
    -- through Meu); energies are referenced to their (degeneracy-weighted) average so
    -- the k = 0 monopole vanishes. The Akm expansion is taken from the Quanty
    -- point-group tables (https://www.quanty.org/physics_chemistry/point_groups).
    Eav_#m_i = ($Ea2u(#m)_i_value + $Eb1u(#m)_i_value + $Eb2u(#m)_i_value + 2 * $Eeu1(#m)_i_value + 2 * $Eeu2(#m)_i_value) / 7
    Ea2u_#m_i = $Ea2u(#m)_i_value - Eav_#m_i
    Eb1u_#m_i = $Eb1u(#m)_i_value - Eav_#m_i
    Eb2u_#m_i = $Eb2u(#m)_i_value - Eav_#m_i
    Eeu1_#m_i = $Eeu1(#m)_i_value - Eav_#m_i
    Eeu2_#m_i = $Eeu2(#m)_i_value - Eav_#m_i
    Meu_#m_i = $Meu(#m)_i_value

    Akm_#m_i = {
        {0, 0, (1 / 7) * (Ea2u_#m_i + Eb1u_#m_i + Eb2u_#m_i + 2 * Eeu1_#m_i + 2 * Eeu2_#m_i)},
        {2, 0, (5 / 7) * (Ea2u_#m_i - Eeu1_#m_i + sqrt(15) * Meu_#m_i)},
        {4, 0, (3 / 28) * (12 * Ea2u_#m_i - 14 * Eb1u_#m_i - 14 * Eb2u_#m_i + 9 * Eeu1_#m_i + 7 * Eeu2_#m_i - 2 * sqrt(15) * Meu_#m_i)},
        {4, -4, (-3 / 56) * (2 * sqrt(70) * Eb1u_#m_i - 2 * sqrt(70) * Eb2u_#m_i - 3 * sqrt(70) * Eeu1_#m_i + 3 * sqrt(70) * Eeu2_#m_i - 2 * sqrt(42) * Meu_#m_i)},
        {4, 4, (-3 / 56) * (2 * sqrt(70) * Eb1u_#m_i - 2 * sqrt(70) * Eb2u_#m_i - 3 * sqrt(70) * Eeu1_#m_i + 3 * sqrt(70) * Eeu2_#m_i - 2 * sqrt(42) * Meu_#m_i)},
        {6, 0, (13 / 280) * (40 * Ea2u_#m_i + 12 * Eb1u_#m_i + 12 * Eb2u_#m_i - 25 * Eeu1_#m_i - 39 * Eeu2_#m_i - 14 * sqrt(15) * Meu_#m_i)},
        {6, -4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_#m_i - 4 * sqrt(42) * Eb2u_#m_i + 5 * sqrt(42) * Eeu1_#m_i - 5 * sqrt(42) * Eeu2_#m_i + 2 * sqrt(70) * Meu_#m_i))},
        {6, 4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_#m_i - 4 * sqrt(42) * Eb2u_#m_i + 5 * sqrt(42) * Eeu1_#m_i - 5 * sqrt(42) * Eeu2_#m_i + 2 * sqrt(70) * Meu_#m_i))}
    }

    io.write("Initial-state D4h crystal field Hamiltonian (a2u, b1u, b2u, eu) diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("%-7s %8.3f\n", "a2u", Ea2u_#m_i))
    io.write(string.format("%-7s %8.3f\n", "b1u", Eb1u_#m_i))
    io.write(string.format("%-7s %8.3f\n", "b2u", Eb2u_#m_i))
    io.write(string.format("%-7s %8.3f\n", "eu(1)", Eeu1_#m_i))
    io.write(string.format("%-7s %8.3f\n", "eu(2)", Eeu2_#m_i))
    io.write("================\n")
    io.write(string.format("Off-diagonal elements: <eu(1)|H|eu(2)> = %.3f.\n", Meu_#m_i))
    io.write("\n")

    Eav_#m_m = ($Ea2u(#m)_m_value + $Eb1u(#m)_m_value + $Eb2u(#m)_m_value + 2 * $Eeu1(#m)_m_value + 2 * $Eeu2(#m)_m_value) / 7
    Ea2u_#m_m = $Ea2u(#m)_m_value - Eav_#m_m
    Eb1u_#m_m = $Eb1u(#m)_m_value - Eav_#m_m
    Eb2u_#m_m = $Eb2u(#m)_m_value - Eav_#m_m
    Eeu1_#m_m = $Eeu1(#m)_m_value - Eav_#m_m
    Eeu2_#m_m = $Eeu2(#m)_m_value - Eav_#m_m
    Meu_#m_m = $Meu(#m)_m_value

    Akm_#m_m = {
        {0, 0, (1 / 7) * (Ea2u_#m_m + Eb1u_#m_m + Eb2u_#m_m + 2 * Eeu1_#m_m + 2 * Eeu2_#m_m)},
        {2, 0, (5 / 7) * (Ea2u_#m_m - Eeu1_#m_m + sqrt(15) * Meu_#m_m)},
        {4, 0, (3 / 28) * (12 * Ea2u_#m_m - 14 * Eb1u_#m_m - 14 * Eb2u_#m_m + 9 * Eeu1_#m_m + 7 * Eeu2_#m_m - 2 * sqrt(15) * Meu_#m_m)},
        {4, -4, (-3 / 56) * (2 * sqrt(70) * Eb1u_#m_m - 2 * sqrt(70) * Eb2u_#m_m - 3 * sqrt(70) * Eeu1_#m_m + 3 * sqrt(70) * Eeu2_#m_m - 2 * sqrt(42) * Meu_#m_m)},
        {4, 4, (-3 / 56) * (2 * sqrt(70) * Eb1u_#m_m - 2 * sqrt(70) * Eb2u_#m_m - 3 * sqrt(70) * Eeu1_#m_m + 3 * sqrt(70) * Eeu2_#m_m - 2 * sqrt(42) * Meu_#m_m)},
        {6, 0, (13 / 280) * (40 * Ea2u_#m_m + 12 * Eb1u_#m_m + 12 * Eb2u_#m_m - 25 * Eeu1_#m_m - 39 * Eeu2_#m_m - 14 * sqrt(15) * Meu_#m_m)},
        {6, -4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_#m_m - 4 * sqrt(42) * Eb2u_#m_m + 5 * sqrt(42) * Eeu1_#m_m - 5 * sqrt(42) * Eeu2_#m_m + 2 * sqrt(70) * Meu_#m_m))},
        {6, 4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_#m_m - 4 * sqrt(42) * Eb2u_#m_m + 5 * sqrt(42) * Eeu1_#m_m - 5 * sqrt(42) * Eeu2_#m_m + 2 * sqrt(70) * Meu_#m_m))}
    }

    Eav_#m_f = ($Ea2u(#m)_f_value + $Eb1u(#m)_f_value + $Eb2u(#m)_f_value + 2 * $Eeu1(#m)_f_value + 2 * $Eeu2(#m)_f_value) / 7
    Ea2u_#m_f = $Ea2u(#m)_f_value - Eav_#m_f
    Eb1u_#m_f = $Eb1u(#m)_f_value - Eav_#m_f
    Eb2u_#m_f = $Eb2u(#m)_f_value - Eav_#m_f
    Eeu1_#m_f = $Eeu1(#m)_f_value - Eav_#m_f
    Eeu2_#m_f = $Eeu2(#m)_f_value - Eav_#m_f
    Meu_#m_f = $Meu(#m)_f_value

    Akm_#m_f = {
        {0, 0, (1 / 7) * (Ea2u_#m_f + Eb1u_#m_f + Eb2u_#m_f + 2 * Eeu1_#m_f + 2 * Eeu2_#m_f)},
        {2, 0, (5 / 7) * (Ea2u_#m_f - Eeu1_#m_f + sqrt(15) * Meu_#m_f)},
        {4, 0, (3 / 28) * (12 * Ea2u_#m_f - 14 * Eb1u_#m_f - 14 * Eb2u_#m_f + 9 * Eeu1_#m_f + 7 * Eeu2_#m_f - 2 * sqrt(15) * Meu_#m_f)},
        {4, -4, (-3 / 56) * (2 * sqrt(70) * Eb1u_#m_f - 2 * sqrt(70) * Eb2u_#m_f - 3 * sqrt(70) * Eeu1_#m_f + 3 * sqrt(70) * Eeu2_#m_f - 2 * sqrt(42) * Meu_#m_f)},
        {4, 4, (-3 / 56) * (2 * sqrt(70) * Eb1u_#m_f - 2 * sqrt(70) * Eb2u_#m_f - 3 * sqrt(70) * Eeu1_#m_f + 3 * sqrt(70) * Eeu2_#m_f - 2 * sqrt(42) * Meu_#m_f)},
        {6, 0, (13 / 280) * (40 * Ea2u_#m_f + 12 * Eb1u_#m_f + 12 * Eb2u_#m_f - 25 * Eeu1_#m_f - 39 * Eeu2_#m_f - 14 * sqrt(15) * Meu_#m_f)},
        {6, -4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_#m_f - 4 * sqrt(42) * Eb2u_#m_f + 5 * sqrt(42) * Eeu1_#m_f - 5 * sqrt(42) * Eeu2_#m_f + 2 * sqrt(70) * Meu_#m_f))},
        {6, 4, (-13 / 560) * (sqrt(3) * (4 * sqrt(42) * Eb1u_#m_f - 4 * sqrt(42) * Eb2u_#m_f + 5 * sqrt(42) * Eeu1_#m_f - 5 * sqrt(42) * Eeu2_#m_f + 2 * sqrt(70) * Meu_#m_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_f))
end
