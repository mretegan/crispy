--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3d crystal field in the Zy orientation (C3 axis along z, a basal C2 axis
    -- along y), taken from the Quanty point-group tables:
    -- https://www.quanty.org/physics_chemistry/point_groups/d3d/orientation_zy
    --
    -- The five #m orbitals split into a1g + 2 eg. The two eg pairs descend from
    -- the cubic eg (egσ) and t2g (egπ); they share the same irrep and so
    -- mix through a single off-diagonal element Meg. The on-site Hamiltonian in
    -- the (a1g, egσ, egπ) symmetry-adapted basis is
    --
    --     [ Ea1g    0      0    ]
    --     [   0    Eegσ   Meg   ]
    --     [   0    Meg    Eegπ  ]
    --
    -- The crystal-field potential expanded on the renormalized spherical
    -- harmonics is (Quanty Zy page, k = 0 monopole shift dropped):
    --
    --   {2,  0,   Ea1g + Eegsigma - 2*Eegpi}
    --   {4,  0,   (3/5)*(3*Ea1g - 4*Eegsigma + Eegpi)}
    --   {4, +-3, +-3*sqrt(7/5)*Meg}
    --
    -- Building one operator per parameter (the Akm coefficients are linear in
    -- the parameters) keeps each irrep energy independently tunable.
    Akm = {{2, 0, 1}, {4, 0, 9 / 5}}
    Ea1g_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{2, 0, 1}, {4, 0, -12 / 5}}
    Eegsigma_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{2, 0, -2}, {4, 0, 3 / 5}}
    Eegpi_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{4, -3, -3 * sqrt(7 / 5)}, {4, 3, 3 * sqrt(7 / 5)}}
    Meg_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Ea1g_#m_i = $Ea1g(#m)_i_value
    Eegsigma_#m_i = $Eegsigma(#m)_i_value
    Eegpi_#m_i = $Eegpi(#m)_i_value
    Meg_#m_i = $Meg(#m)_i_value

    io.write("Initial-state D3d crystal field Hamiltonian in the (a1g, egσ, egπ) basis:\n")
    io.write("=========================================\n")
    io.write("Irrep.            E\n")
    io.write("=========================================\n")
    io.write(string.format("a1g           %8.3f\n", Ea1g_#m_i))
    io.write(string.format("egσ           %8.3f\n", Eegsigma_#m_i))
    io.write(string.format("egπ           %8.3f\n", Eegpi_#m_i))
    io.write("=========================================\n")
    io.write(string.format("The eg-eg off-diagonal element <egσ|H|egπ> is %.3f.\n", Meg_#m_i))
    io.write("\n")

    Ea1g_#m_m = $Ea1g(#m)_m_value
    Eegsigma_#m_m = $Eegsigma(#m)_m_value
    Eegpi_#m_m = $Eegpi(#m)_m_value
    Meg_#m_m = $Meg(#m)_m_value

    Ea1g_#m_f = $Ea1g(#m)_f_value
    Eegsigma_#m_f = $Eegsigma(#m)_f_value
    Eegpi_#m_f = $Eegpi(#m)_f_value
    Meg_#m_f = $Meg(#m)_f_value

    H_i = H_i + Chop(
          Ea1g_#m_i * Ea1g_#m
        + Eegsigma_#m_i * Eegsigma_#m
        + Eegpi_#m_i * Eegpi_#m
        + Meg_#m_i * Meg_#m)

    H_m = H_m + Chop(
          Ea1g_#m_m * Ea1g_#m
        + Eegsigma_#m_m * Eegsigma_#m
        + Eegpi_#m_m * Eegpi_#m
        + Meg_#m_m * Meg_#m)

    H_f = H_f + Chop(
          Ea1g_#m_f * Ea1g_#m
        + Eegsigma_#m_f * Eegsigma_#m
        + Eegpi_#m_f * Eegpi_#m
        + Meg_#m_f * Meg_#m)
end
