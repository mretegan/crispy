--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- PotentialExpandedOnClm("Oh", 2, {Eeg, Et2g})
    -- tenDq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 2, {0.6, -0.4}))

    Akm = {{4, 0, 2.1}, {4, -4, 1.5 * sqrt(0.7)}, {4, 4, 1.5 * sqrt(0.7)}}
    tenDq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    tenDq_#f_i = $10Dq(#f)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("eg      %8.3f\n",  0.6 * tenDq_#f_i))
    io.write(string.format("t2g     %8.3f\n", -0.4 * tenDq_#f_i))
    io.write("================\n")
    io.write("\n")

    tenDq_#f_f = $10Dq(#f)_f_value

    H_i = H_i + Chop(
          tenDq_#f_i * tenDq_#f)

    H_f = H_f + Chop(
          tenDq_#f_f * tenDq_#f)
end

--------------------------------------------------------------------------------
-- Define the #f-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_#f_L1_i = $Delta(#f,L1)_i_value
    E_#f_i = (10 * Delta_#f_L1_i - NElectrons_#f * (19 + NElectrons_#f) * U_#f_#f_i / 2) / (10 + NElectrons_#f)
    E_L1_i = NElectrons_#f * ((1 + NElectrons_#f) * U_#f_#f_i / 2 - Delta_#f_L1_i) / (10 + NElectrons_#f)

    Delta_#f_L1_f = $Delta(#f,L1)_f_value
    E_#f_f = (10 * Delta_#f_L1_f - NElectrons_#f * (31 + NElectrons_#f) * U_#f_#f_f / 2 - 90 * U_#i_#f_f) / (16 + NElectrons_#f)
    E_#i_f = (10 * Delta_#f_L1_f + (1 + NElectrons_#f) * (NElectrons_#f * U_#f_#f_f / 2 - (10 + NElectrons_#f) * U_#i_#f_f)) / (16 + NElectrons_#f)
    E_L1_f = ((1 + NElectrons_#f) * (NElectrons_#f * U_#f_#f_f / 2 + 6 * U_#i_#f_f) - (6 + NElectrons_#f) * Delta_#f_L1_f) / (16 + NElectrons_#f)

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L1_i * N_L1)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
        + E_L1_f * N_L1)

    tenDq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 2, {0.6, -0.4}))

    Veg_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 2, {1, 0}))
              + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 2, {1, 0}))

    Vt2g_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 2, {0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 2, {0, 1}))

    tenDq_L1_i = $10Dq(L1)_i_value
    Veg_#f_L1_i = $Veg(#f,L1)_i_value
    Vt2g_#f_L1_i = $Vt2g(#f,L1)_i_value

    tenDq_L1_f = $10Dq(L1)_f_value
    Veg_#f_L1_f = $Veg(#f,L1)_f_value
    Vt2g_#f_L1_f = $Vt2g(#f,L1)_f_value

    H_i = H_i + Chop(
          tenDq_L1_i * tenDq_L1
        + Veg_#f_L1_i * Veg_#f_L1
        + Vt2g_#f_L1_i * Vt2g_#f_L1)

    H_f = H_f + Chop(
          tenDq_L1_f * tenDq_L1
        + Veg_#f_L1_f * Veg_#f_L1
        + Vt2g_#f_L1_f * Vt2g_#f_L1)
end

--------------------------------------------------------------------------------
-- Define the #f-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if MlctLigandsHybridizationTerm then
    N_L2 = NewOperator("Number", NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_#f_L2_i = $Delta(#f,L2)_i_value
    E_#f_i = U_#f_#f_i * (-NElectrons_#f + 1) / 2
    E_L2_i = Delta_#f_L2_i + U_#f_#f_i * NElectrons_#f / 2 - U_#f_#f_i / 2

    Delta_#f_L2_f = $Delta(#f,L2)_f_value
    E_#f_f = -(U_#f_#f_f * NElectrons_#f^2 + 11 * U_#f_#f_f * NElectrons_#f + 60 * U_#i_#f_f) / (2 * NElectrons_#f + 12)
    E_#i_f = NElectrons_#f * (U_#f_#f_f * NElectrons_#f + U_#f_#f_f - 2 * U_#i_#f_f * NElectrons_#f - 2 * U_#i_#f_f) / (2 * (NElectrons_#f + 6))
    E_L2_f = (2 * Delta_#f_L2_f * NElectrons_#f + 12 * Delta_#f_L2_f + U_#f_#f_f * NElectrons_#f^2 - U_#f_#f_f * NElectrons_#f - 12 * U_#f_#f_f + 12 * U_#i_#f_f * NElectrons_#f + 12 * U_#i_#f_f) / (2 * (NElectrons_#f + 6))

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L2_i * N_L2)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
        + E_L2_f * N_L2)

    tenDq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("Oh", 2, {0.6, -0.4}))

    Veg_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 2, {1, 0}))
              + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("Oh", 2, {1, 0}))

    Vt2g_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 2, {0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("Oh", 2, {0, 1}))

    tenDq_L2_i = $10Dq(L2)_i_value
    Veg_#f_L2_i = $Veg(#f,L2)_i_value
    Vt2g_#f_L2_i = $Vt2g(#f,L2)_i_value

    tenDq_L2_f = $10Dq(L2)_f_value
    Veg_#f_L2_f = $Veg(#f,L2)_f_value
    Vt2g_#f_L2_f = $Vt2g(#f,L2)_f_value

    H_i = H_i + Chop(
          tenDq_L2_i * tenDq_L2
        + Veg_#f_L2_i * Veg_#f_L2
        + Vt2g_#f_L2_i * Vt2g_#f_L2)

    H_f = H_f + Chop(
          tenDq_L2_f * tenDq_L2
        + Veg_#f_L2_f * Veg_#f_L2
        + Vt2g_#f_L2_f * Vt2g_#f_L2)
end
