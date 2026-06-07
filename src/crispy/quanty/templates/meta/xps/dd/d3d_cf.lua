--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- D3d crystal field in the Zy orientation (C3 axis along z, a basal C2 axis
    -- along y), taken from the Quanty point-group tables:
    -- https://www.quanty.org/physics_chemistry/point_groups/d3d/orientation_zy
    --
    -- The five #f orbitals split into a1g + 2 eg. The two eg pairs descend from
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
    Ea1g_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{2, 0, 1}, {4, 0, -12 / 5}}
    Eegsigma_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{2, 0, -2}, {4, 0, 3 / 5}}
    Eegpi_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{4, -3, -3 * sqrt(7 / 5)}, {4, 3, 3 * sqrt(7 / 5)}}
    Meg_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Ea1g_#f_i = $Ea1g(#f)_i_value
    Eegsigma_#f_i = $Eegsigma(#f)_i_value
    Eegpi_#f_i = $Eegpi(#f)_i_value
    Meg_#f_i = $Meg(#f)_i_value

    io.write("Initial-state D3d crystal field Hamiltonian in the (a1g, egσ, egπ) basis:\n")
    io.write("=========================================\n")
    io.write("Irrep.            E\n")
    io.write("=========================================\n")
    io.write(string.format("a1g           %8.3f\n", Ea1g_#f_i))
    io.write(string.format("egσ           %8.3f\n", Eegsigma_#f_i))
    io.write(string.format("egπ           %8.3f\n", Eegpi_#f_i))
    io.write("=========================================\n")
    io.write(string.format("The eg-eg off-diagonal element <egσ|H|egπ> is %.3f.\n", Meg_#f_i))
    io.write("\n")

    Ea1g_#f_f = $Ea1g(#f)_f_value
    Eegsigma_#f_f = $Eegsigma(#f)_f_value
    Eegpi_#f_f = $Eegpi(#f)_f_value
    Meg_#f_f = $Meg(#f)_f_value

    H_i = H_i + Chop(
          Ea1g_#f_i * Ea1g_#f
        + Eegsigma_#f_i * Eegsigma_#f
        + Eegpi_#f_i * Eegpi_#f
        + Meg_#f_i * Meg_#f)

    H_f = H_f + Chop(
          Ea1g_#f_f * Ea1g_#f
        + Eegsigma_#f_f * Eegsigma_#f
        + Eegpi_#f_f * Eegpi_#f
        + Meg_#f_f * Meg_#f)
end
