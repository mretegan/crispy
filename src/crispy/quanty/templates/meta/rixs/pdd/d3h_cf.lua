--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3h crystal field for d electrons, Quanty "zx" setting: the three-fold C3 axis
    -- is along z, the horizontal mirror sigma_h is the xy-plane, and a C2' axis lies
    -- along x. The five #m orbitals split into a1' + e' + e'', parametrized by Dmu
    -- and Dnu (a1' = -2Dmu - 6Dnu, e' = 2Dmu - Dnu, e'' = -Dmu + 4Dnu). The Akm
    -- expansion (k = 2 and 4, m = 0) is taken from the Quanty point-group tables
    -- (https://www.quanty.org/physics_chemistry/point_groups).
    Akm = {{2, 0, -7}}
    Dmu_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{4, 0, -21}}
    Dnu_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Dmu_#m_i = $Dmu(#m)_i_value
    Dnu_#m_i = $Dnu(#m)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a\'1     %8.3f\n", -2 * Dmu_#m_i - 6 * Dnu_#m_i))
    io.write(string.format("e\'      %8.3f\n", 2 * Dmu_#m_i - Dnu_#m_i))
    io.write(string.format("e\'\'     %8.3f\n", -Dmu_#m_i + 4 * Dnu_#m_i))
    io.write("================\n")
    io.write("\n")

    Dmu_#m_m = $Dmu(#m)_m_value
    Dnu_#m_m = $Dnu(#m)_m_value

    Dmu_#m_f = $Dmu(#m)_f_value
    Dnu_#m_f = $Dnu(#m)_f_value

    H_i = H_i + Chop(
          Dmu_#m_i * Dmu_#m
        + Dnu_#m_i * Dnu_#m)

    H_m = H_m + Chop(
          Dmu_#m_m * Dmu_#m
        + Dnu_#m_m * Dnu_#m)

    H_f = H_f + Chop(
          Dmu_#m_f * Dmu_#m
        + Dnu_#m_f * Dnu_#m)
end
