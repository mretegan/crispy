--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3h crystal field for f electrons, Quanty "zx" setting: the three-fold C3 axis
    -- is along z, the horizontal mirror sigma_h is the xy-plane, and a C2' axis lies
    -- along x. The seven #m orbitals split into a1' + a2' + a2'' + e' + e'';
    -- energies are referenced to their (degeneracy-weighted) average so the k = 0
    -- monopole vanishes. The Akm expansion is taken from the Quanty point-group
    -- tables (https://www.quanty.org/physics_chemistry/point_groups).
    Eav_#m_i = ($Ea1p(#m)_i_value + $Ea2p(#m)_i_value + $Ea2pp(#m)_i_value + 2 * $Eep(#m)_i_value + 2 * $Eepp(#m)_i_value) / 7
    Ea1p_#m_i = $Ea1p(#m)_i_value - Eav_#m_i
    Ea2p_#m_i = $Ea2p(#m)_i_value - Eav_#m_i
    Ea2pp_#m_i = $Ea2pp(#m)_i_value - Eav_#m_i
    Eep_#m_i = $Eep(#m)_i_value - Eav_#m_i
    Eepp_#m_i = $Eepp(#m)_i_value - Eav_#m_i

    Akm_#m_i = {
        {0, 0, (1 / 7) * (Ea1p_#m_i + Ea2p_#m_i + Ea2pp_#m_i + 2 * Eep_#m_i + 2 * Eepp_#m_i)},
        {2, 0, (-5 / 28) * (5 * Ea1p_#m_i + 5 * Ea2p_#m_i - 4 * Ea2pp_#m_i - 6 * Eep_#m_i)},
        {4, 0, (3 / 14) * (3 * Ea1p_#m_i + 3 * Ea2p_#m_i + 2 * (3 * Ea2pp_#m_i + Eep_#m_i - 7 * Eepp_#m_i))},
        {6, 0, (-13 / 140) * (Ea1p_#m_i + Ea2p_#m_i - 20 * Ea2pp_#m_i + 30 * Eep_#m_i - 12 * Eepp_#m_i)},
        {6, -6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#m_i - Ea2p_#m_i))},
        {6, 6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#m_i - Ea2p_#m_i))}
    }

    io.write("Initial-state D3h crystal field Hamiltonian (a1', a2', a2'', e', e'') diagonal energies:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("%-7s %8.3f\n", "a1'", Ea1p_#m_i))
    io.write(string.format("%-7s %8.3f\n", "a2'", Ea2p_#m_i))
    io.write(string.format("%-7s %8.3f\n", "a2''", Ea2pp_#m_i))
    io.write(string.format("%-7s %8.3f\n", "e'", Eep_#m_i))
    io.write(string.format("%-7s %8.3f\n", "e''", Eepp_#m_i))
    io.write("================\n")
    io.write("\n")

    Eav_#m_m = ($Ea1p(#m)_m_value + $Ea2p(#m)_m_value + $Ea2pp(#m)_m_value + 2 * $Eep(#m)_m_value + 2 * $Eepp(#m)_m_value) / 7
    Ea1p_#m_m = $Ea1p(#m)_m_value - Eav_#m_m
    Ea2p_#m_m = $Ea2p(#m)_m_value - Eav_#m_m
    Ea2pp_#m_m = $Ea2pp(#m)_m_value - Eav_#m_m
    Eep_#m_m = $Eep(#m)_m_value - Eav_#m_m
    Eepp_#m_m = $Eepp(#m)_m_value - Eav_#m_m

    Akm_#m_m = {
        {0, 0, (1 / 7) * (Ea1p_#m_m + Ea2p_#m_m + Ea2pp_#m_m + 2 * Eep_#m_m + 2 * Eepp_#m_m)},
        {2, 0, (-5 / 28) * (5 * Ea1p_#m_m + 5 * Ea2p_#m_m - 4 * Ea2pp_#m_m - 6 * Eep_#m_m)},
        {4, 0, (3 / 14) * (3 * Ea1p_#m_m + 3 * Ea2p_#m_m + 2 * (3 * Ea2pp_#m_m + Eep_#m_m - 7 * Eepp_#m_m))},
        {6, 0, (-13 / 140) * (Ea1p_#m_m + Ea2p_#m_m - 20 * Ea2pp_#m_m + 30 * Eep_#m_m - 12 * Eepp_#m_m)},
        {6, -6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#m_m - Ea2p_#m_m))},
        {6, 6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#m_m - Ea2p_#m_m))}
    }

    Eav_#m_f = ($Ea1p(#m)_f_value + $Ea2p(#m)_f_value + $Ea2pp(#m)_f_value + 2 * $Eep(#m)_f_value + 2 * $Eepp(#m)_f_value) / 7
    Ea1p_#m_f = $Ea1p(#m)_f_value - Eav_#m_f
    Ea2p_#m_f = $Ea2p(#m)_f_value - Eav_#m_f
    Ea2pp_#m_f = $Ea2pp(#m)_f_value - Eav_#m_f
    Eep_#m_f = $Eep(#m)_f_value - Eav_#m_f
    Eepp_#m_f = $Eepp(#m)_f_value - Eav_#m_f

    Akm_#m_f = {
        {0, 0, (1 / 7) * (Ea1p_#m_f + Ea2p_#m_f + Ea2pp_#m_f + 2 * Eep_#m_f + 2 * Eepp_#m_f)},
        {2, 0, (-5 / 28) * (5 * Ea1p_#m_f + 5 * Ea2p_#m_f - 4 * Ea2pp_#m_f - 6 * Eep_#m_f)},
        {4, 0, (3 / 14) * (3 * Ea1p_#m_f + 3 * Ea2p_#m_f + 2 * (3 * Ea2pp_#m_f + Eep_#m_f - 7 * Eepp_#m_f))},
        {6, 0, (-13 / 140) * (Ea1p_#m_f + Ea2p_#m_f - 20 * Ea2pp_#m_f + 30 * Eep_#m_f - 12 * Eepp_#m_f)},
        {6, -6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#m_f - Ea2p_#m_f))},
        {6, 6, (13 / 20) * (sqrt(33 / 7) * (Ea1p_#m_f - Ea2p_#m_f))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_f))
end
