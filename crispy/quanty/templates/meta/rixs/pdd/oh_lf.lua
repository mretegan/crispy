--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- PotentialExpandedOnClm("Oh", 2, {Eeg, Et2g})
    -- tenDq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 2, {0.6, -0.4}))

    Akm = {{4, 0, 2.1}, {4, -4, 1.5 * sqrt(0.7)}, {4, 4, 1.5 * sqrt(0.7)}}
    tenDq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    tenDq_#m_i = $10Dq(#m)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("eg      %8.3f\n",  0.6 * tenDq_#m_i))
    io.write(string.format("t2g     %8.3f\n", -0.4 * tenDq_#m_i))
    io.write("================\n")
    io.write("\n")

    tenDq_#m_m = $10Dq(#m)_m_value

    tenDq_#m_f = $10Dq(#m)_f_value

    H_i = H_i + Chop(
          tenDq_#m_i * tenDq_#m)

    H_m = H_m + Chop(
          tenDq_#m_m * tenDq_#m)

    H_f = H_f + Chop(
          tenDq_#m_f * tenDq_#m)
end

--------------------------------------------------------------------------------
-- Define the #m-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_#m_L1_i = $Delta(#m,L1)_i_value
    E_#m_i = (10 * Delta_#m_L1_i - NElectrons_#m * (19 + NElectrons_#m) * U_#m_#m_i / 2) / (10 + NElectrons_#m)
    E_L1_i = NElectrons_#m * ((1 + NElectrons_#m) * U_#m_#m_i / 2 - Delta_#m_L1_i) / (10 + NElectrons_#m)

    Delta_#m_L1_m = $Delta(#m,L1)_m_value
    E_#m_m = (10 * Delta_#m_L1_m - NElectrons_#m * (31 + NElectrons_#m) * U_#m_#m_m / 2 - 90 * U_#i_#m_m) / (16 + NElectrons_#m)
    E_#i_m = (10 * Delta_#m_L1_m + (1 + NElectrons_#m) * (NElectrons_#m * U_#m_#m_m / 2 - (10 + NElectrons_#m) * U_#i_#m_m)) / (16 + NElectrons_#m)
    E_L1_m = ((1 + NElectrons_#m) * (NElectrons_#m * U_#m_#m_m / 2 + 6 * U_#i_#m_m) - (6 + NElectrons_#m) * Delta_#m_L1_m) / (16 + NElectrons_#m)

    Delta_#m_L1_f = $Delta(#m,L1)_f_value
    E_#m_f = (10 * Delta_#m_L1_f - NElectrons_#m * (19 + NElectrons_#m) * U_#m_#m_f / 2) / (10 + NElectrons_#m)
    E_L1_f = NElectrons_#m * ((1 + NElectrons_#m) * U_#m_#m_f / 2 - Delta_#m_L1_f) / (10 + NElectrons_#m)

    H_i = H_i + Chop(
          E_#m_i * N_#m
        + E_L1_i * N_L1)

    H_m = H_m + Chop(
          E_#m_m * N_#m
        + E_#i_m * N_#i
        + E_L1_m * N_L1)

    H_f = H_f + Chop(
          E_#m_f * N_#m
        + E_L1_f * N_L1)

    tenDq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 2, {0.6, -0.4}))

    Veg_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 2, {1, 0}))
              + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 2, {1, 0}))

    Vt2g_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 2, {0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 2, {0, 1}))

    tenDq_L1_i = $10Dq(L1)_i_value
    Veg_#m_L1_i = $Veg(#m,L1)_i_value
    Vt2g_#m_L1_i = $Vt2g(#m,L1)_i_value

    tenDq_L1_m = $10Dq(L1)_m_value
    Veg_#m_L1_m = $Veg(#m,L1)_m_value
    Vt2g_#m_L1_m = $Vt2g(#m,L1)_m_value

    tenDq_L1_f = $10Dq(L1)_f_value
    Veg_#m_L1_f = $Veg(#m,L1)_f_value
    Vt2g_#m_L1_f = $Vt2g(#m,L1)_f_value

    H_i = H_i + Chop(
          tenDq_L1_i * tenDq_L1
        + Veg_#m_L1_i * Veg_#m_L1
        + Vt2g_#m_L1_i * Vt2g_#m_L1)

    H_m = H_m + Chop(
          tenDq_L1_m * tenDq_L1
        + Veg_#m_L1_m * Veg_#m_L1
        + Vt2g_#m_L1_m * Vt2g_#m_L1)

    H_f = H_f + Chop(
          tenDq_L1_f * tenDq_L1
        + Veg_#m_L1_f * Veg_#m_L1
        + Vt2g_#m_L1_f * Vt2g_#m_L1)
end

--------------------------------------------------------------------------------
-- Define the #m-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if MlctLigandsHybridizationTerm then
    N_L2 = NewOperator("Number", NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_#m_L2_i = $Delta(#m,L2)_i_value
    E_#m_i = U_#m_#m_i * (-NElectrons_#m + 1) / 2
    E_L2_i = Delta_#m_L2_i + U_#m_#m_i * NElectrons_#m / 2 - U_#m_#m_i / 2

    Delta_#m_L2_m = $Delta(#m,L2)_m_value
    E_#m_m = -(U_#m_#m_m * NElectrons_#m^2 + 11 * U_#m_#m_m * NElectrons_#m + 60 * U_#i_#m_m) / (2 * NElectrons_#m + 12)
    E_#i_m = NElectrons_#m * (U_#m_#m_m * NElectrons_#m + U_#m_#m_m - 2 * U_#i_#m_m * NElectrons_#m - 2 * U_#i_#m_m) / (2 * (NElectrons_#m + 6))
    E_L2_m = (2 * Delta_#f_L2_m * NElectrons_#f + 12 * Delta_#f_L2_m + U_#f_#f_m * NElectrons_#f^2 - U_#f_#f_m * NElectrons_#f - 12 * U_#f_#f_m + 12 * U_#i_#f_m * NElectrons_#f + 12 * U_#i_#f_m) / (2 * (NElectrons_#f + 6))

    Delta_#m_L2_f = $Delta(#m,L2)_f_value
    E_#m_f = U_#m_#m_f * (-NElectrons_#m + 1) / 2
    E_L2_f = Delta_#m_L2_f + U_#m_#m_f * NElectrons_#m / 2 - U_#m_#m_f / 2

    H_i = H_i + Chop(
          E_#m_i * N_#m
        + E_L2_i * N_L2)

    H_m = H_m + Chop(
          E_#m_m * N_#m
        + E_#i_m * N_#i
        + E_L2_m * N_L2)

    H_f = H_f + Chop(
          E_#m_f * N_#m
        + E_L2_f * N_L2)

    tenDq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("Oh", 2, {0.6, -0.4}))

    Veg_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 2, {1, 0}))
              + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("Oh", 2, {1, 0}))

    Vt2g_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 2, {0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("Oh", 2, {0, 1}))

    tenDq_L2_i = $10Dq(L2)_i_value
    Veg_#m_L2_i = $Veg(#m,L2)_i_value
    Vt2g_#m_L2_i = $Vt2g(#m,L2)_i_value

    tenDq_L2_m = $10Dq(L2)_m_value
    Veg_#m_L2_m = $Veg(#m,L2)_m_value
    Vt2g_#m_L2_m = $Vt2g(#m,L2)_m_value

    tenDq_L2_f = $10Dq(L2)_f_value
    Veg_#m_L2_f = $Veg(#m,L2)_f_value
    Vt2g_#m_L2_f = $Vt2g(#m,L2)_f_value

    H_i = H_i + Chop(
          tenDq_L2_i * tenDq_L2
        + Veg_#m_L2_i * Veg_#m_L2
        + Vt2g_#m_L2_i * Vt2g_#m_L2)

    H_m = H_m + Chop(
          tenDq_L2_m * tenDq_L2
        + Veg_#m_L2_m * Veg_#m_L2
        + Vt2g_#m_L2_m * Vt2g_#m_L2)

    H_f = H_f + Chop(
          tenDq_L2_f * tenDq_L2
        + Veg_#m_L2_f * Veg_#m_L2
        + Vt2g_#m_L2_f * Vt2g_#m_L2)
end
