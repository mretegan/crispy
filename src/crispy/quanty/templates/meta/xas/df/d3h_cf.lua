--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3h crystal field for f electrons, Quanty "zx" setting: the three-fold C3 axis
    -- is along z, the horizontal mirror sigma_h is the xy-plane, and a C2' axis lies
    -- along x. The seven #f orbitals split into a1' + a2' + a2'' + e' + e'';
    -- energies are referenced to their (degeneracy-weighted) average so the k = 0
    -- monopole vanishes. The Akm expansion is taken from the Quanty point-group
    -- tables (https://www.quanty.org/physics_chemistry/point_groups).
    Eav_#f_i = ($Ea1p(#f)_i_value + $Ea2p(#f)_i_value + $Ea2pp(#f)_i_value + 2 * $Eep(#f)_i_value + 2 * $Eepp(#f)_i_value) / 7
    Ea1p_#f_i = $Ea1p(#f)_i_value - Eav_#f_i
    Ea2p_#f_i = $Ea2p(#f)_i_value - Eav_#f_i
    Ea2pp_#f_i = $Ea2pp(#f)_i_value - Eav_#f_i
    Eep_#f_i = $Eep(#f)_i_value - Eav_#f_i
    Eepp_#f_i = $Eepp(#f)_i_value - Eav_#f_i

    Akm_#f_i = {
        {0, 0, (1 / 7) * (Ea1p_#f_i + Ea2p_#f_i + Ea2pp_#f_i + 2 * Eep_#f_i + 2 * Eepp_#f_i)},
        {2, 0, (-5 / 28) * (5 * Ea1p_#f_i + 5 * Ea2p_#f_i - 4 * Ea2pp_#f_i - 6 * Eep_#f_i)},
        {4, 0, (3 / 14) * (3 * Ea1p_#f_i + 3 * Ea2p_#f_i + 2 * (3 * Ea2pp_#f_i + Eep_#f_i - 7 * Eepp_#f_i))},
        {6, 0, (-13 / 140) * (Ea1p_#f_i + Ea2p_#f_i - 20 * Ea2pp_#f_i + 30 * Eep_#f_i - 12 * Eepp_#f_i)},
        {6, -6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#f_i - Ea2p_#f_i))},
        {6, 6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#f_i - Ea2p_#f_i))}
    }

    io.write("Initial-state D3h crystal field Hamiltonian (a1', a2', a2'', e', e'') diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("%-7s %8.3f\n", "a1'", Ea1p_#f_i))
    io.write(string.format("%-7s %8.3f\n", "a2'", Ea2p_#f_i))
    io.write(string.format("%-7s %8.3f\n", "a2''", Ea2pp_#f_i))
    io.write(string.format("%-7s %8.3f\n", "e'", Eep_#f_i))
    io.write(string.format("%-7s %8.3f\n", "e''", Eepp_#f_i))
    io.write("================\n")
    io.write("\n")

    Eav_#f_f = ($Ea1p(#f)_f_value + $Ea2p(#f)_f_value + $Ea2pp(#f)_f_value + 2 * $Eep(#f)_f_value + 2 * $Eepp(#f)_f_value) / 7
    Ea1p_#f_f = $Ea1p(#f)_f_value - Eav_#f_f
    Ea2p_#f_f = $Ea2p(#f)_f_value - Eav_#f_f
    Ea2pp_#f_f = $Ea2pp(#f)_f_value - Eav_#f_f
    Eep_#f_f = $Eep(#f)_f_value - Eav_#f_f
    Eepp_#f_f = $Eepp(#f)_f_value - Eav_#f_f

    Akm_#f_f = {
        {0, 0, (1 / 7) * (Ea1p_#f_f + Ea2p_#f_f + Ea2pp_#f_f + 2 * Eep_#f_f + 2 * Eepp_#f_f)},
        {2, 0, (-5 / 28) * (5 * Ea1p_#f_f + 5 * Ea2p_#f_f - 4 * Ea2pp_#f_f - 6 * Eep_#f_f)},
        {4, 0, (3 / 14) * (3 * Ea1p_#f_f + 3 * Ea2p_#f_f + 2 * (3 * Ea2pp_#f_f + Eep_#f_f - 7 * Eepp_#f_f))},
        {6, 0, (-13 / 140) * (Ea1p_#f_f + Ea2p_#f_f - 20 * Ea2pp_#f_f + 30 * Eep_#f_f - 12 * Eepp_#f_f)},
        {6, -6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#f_f - Ea2p_#f_f))},
        {6, 6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#f_f - Ea2p_#f_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_i))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_f))
end
