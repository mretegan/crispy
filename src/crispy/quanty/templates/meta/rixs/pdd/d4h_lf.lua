--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- PotentialExpandedOnClm("D4h", 2, {Ea1g, Eb1g, Eb2g, Eeg})
    -- Dq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    -- Ds_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    -- Dt_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Akm = {{4, 0, 21}, {4, -4, 1.5 * sqrt(70)}, {4, 4, 1.5 * sqrt(70)}}
    Dq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{2, 0, -7}}
    Ds_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{4, 0, -21}}
    Dt_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Dq_#m_i = $10Dq(#m)_i_value / 10.0
    Ds_#m_i = $Ds(#m)_i_value
    Dt_#m_i = $Dt(#m)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1g     %8.3f\n", 6 * Dq_#m_i - 2 * Ds_#m_i - 6 * Dt_#m_i ))
    io.write(string.format("b1g     %8.3f\n", 6 * Dq_#m_i + 2 * Ds_#m_i - Dt_#m_i ))
    io.write(string.format("b2g     %8.3f\n", -4 * Dq_#m_i + 2 * Ds_#m_i - Dt_#m_i ))
    io.write(string.format("eg      %8.3f\n", -4 * Dq_#m_i - Ds_#m_i + 4 * Dt_#m_i))
    io.write("================\n")
    io.write("\n")

    Dq_#m_m = $10Dq(#m)_m_value / 10.0
    Ds_#m_m = $Ds(#m)_m_value
    Dt_#m_m = $Dt(#m)_m_value

    Dq_#m_f = $10Dq(#m)_f_value / 10.0
    Ds_#m_f = $Ds(#m)_f_value
    Dt_#m_f = $Dt(#m)_f_value

    H_i = H_i + Chop(
          Dq_#m_i * Dq_#m
        + Ds_#m_i * Ds_#m
        + Dt_#m_i * Dt_#m)

    H_m = H_m + Chop(
          Dq_#m_m * Dq_#m
        + Ds_#m_m * Ds_#m
        + Dt_#m_m * Dt_#m)

    H_f = H_f + Chop(
          Dq_#m_f * Dq_#m
        + Ds_#m_f * Ds_#m
        + Dt_#m_f * Dt_#m)
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

    Dq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L1_i = $10Dq(L1)_i_value / 10.0
    Ds_L1_i = $Ds(L1)_i_value
    Dt_L1_i = $Dt(L1)_i_value
    Va1g_#m_L1_i = $Va1g(#m,L1)_i_value
    Vb1g_#m_L1_i = $Vb1g(#m,L1)_i_value
    Vb2g_#m_L1_i = $Vb2g(#m,L1)_i_value
    Veg_#m_L1_i = $Veg(#m,L1)_i_value

    Dq_L1_m = $10Dq(L1)_m_value / 10.0
    Ds_L1_m = $Ds(L1)_m_value
    Dt_L1_m = $Dt(L1)_m_value
    Va1g_#m_L1_m = $Va1g(#m,L1)_m_value
    Vb1g_#m_L1_m = $Vb1g(#m,L1)_m_value
    Vb2g_#m_L1_m = $Vb2g(#m,L1)_m_value
    Veg_#m_L1_m = $Veg(#m,L1)_m_value

    Dq_L1_f = $10Dq(L1)_f_value / 10.0
    Ds_L1_f = $Ds(L1)_f_value
    Dt_L1_f = $Dt(L1)_f_value
    Va1g_#m_L1_f = $Va1g(#m,L1)_f_value
    Vb1g_#m_L1_f = $Vb1g(#m,L1)_f_value
    Vb2g_#m_L1_f = $Vb2g(#m,L1)_f_value
    Veg_#m_L1_f = $Veg(#m,L1)_f_value

    H_i = H_i + Chop(
          Dq_L1_i * Dq_L1
        + Ds_L1_i * Ds_L1
        + Dt_L1_i * Dt_L1
        + Va1g_#m_L1_i * Va1g_#m_L1
        + Vb1g_#m_L1_i * Vb1g_#m_L1
        + Vb2g_#m_L1_i * Vb2g_#m_L1
        + Veg_#m_L1_i * Veg_#m_L1)

    H_m = H_m + Chop(
          Dq_L1_m * Dq_L1
        + Ds_L1_m * Ds_L1
        + Dt_L1_m * Dt_L1
        + Va1g_#m_L1_m * Va1g_#m_L1
        + Vb1g_#m_L1_m * Vb1g_#m_L1
        + Vb2g_#m_L1_m * Vb2g_#m_L1
        + Veg_#m_L1_m * Veg_#m_L1)

    H_f = H_f + Chop(
          Dq_L1_f * Dq_L1
        + Ds_L1_f * Ds_L1
        + Dt_L1_f * Dt_L1
        + Va1g_#m_L1_f * Va1g_#m_L1
        + Vb1g_#m_L1_f * Vb1g_#m_L1
        + Vb2g_#m_L1_f * Vb2g_#m_L1
        + Veg_#m_L1_f * Veg_#m_L1)
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

    Dq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L2_i = $10Dq(L2)_i_value / 10.0
    Ds_L2_i = $Ds(L2)_i_value
    Dt_L2_i = $Dt(L2)_i_value
    Va1g_#m_L2_i = $Va1g(#m,L2)_i_value
    Vb1g_#m_L2_i = $Vb1g(#m,L2)_i_value
    Vb2g_#m_L2_i = $Vb2g(#m,L2)_i_value
    Veg_#m_L2_i = $Veg(#m,L2)_i_value

    Dq_L2_m = $10Dq(L2)_m_value / 10.0
    Ds_L2_m = $Ds(L2)_m_value
    Dt_L2_m = $Dt(L2)_m_value
    Va1g_#m_L2_m = $Va1g(#m,L2)_m_value
    Vb1g_#m_L2_m = $Vb1g(#m,L2)_m_value
    Vb2g_#m_L2_m = $Vb2g(#m,L2)_m_value
    Veg_#m_L2_m = $Veg(#m,L2)_m_value

    Dq_L2_f = $10Dq(L2)_f_value / 10.0
    Ds_L2_f = $Ds(L2)_f_value
    Dt_L2_f = $Dt(L2)_f_value
    Va1g_#m_L2_f = $Va1g(#m,L2)_f_value
    Vb1g_#m_L2_f = $Vb1g(#m,L2)_f_value
    Vb2g_#m_L2_f = $Vb2g(#m,L2)_f_value
    Veg_#m_L2_f = $Veg(#m,L2)_f_value

    H_i = H_i + Chop(
          Dq_L2_i * Dq_L2
        + Ds_L2_i * Ds_L2
        + Dt_L2_i * Dt_L2
        + Va1g_#m_L2_i * Va1g_#m_L2
        + Vb1g_#m_L2_i * Vb1g_#m_L2
        + Vb2g_#m_L2_i * Vb2g_#m_L2
        + Veg_#m_L2_i * Veg_#m_L2)

    H_m = H_m + Chop(
          Dq_L2_m * Dq_L2
        + Ds_L2_m * Ds_L2
        + Dt_L2_m * Dt_L2
        + Va1g_#m_L2_m * Va1g_#m_L2
        + Vb1g_#m_L2_m * Vb1g_#m_L2
        + Vb2g_#m_L2_m * Vb2g_#m_L2
        + Veg_#m_L2_m * Veg_#m_L2)

    H_f = H_f + Chop(
          Dq_L2_f * Dq_L2
        + Ds_L2_f * Ds_L2
        + Dt_L2_f * Dt_L2
        + Va1g_#m_L2_f * Va1g_#m_L2
        + Vb1g_#m_L2_f * Vb1g_#m_L2
        + Vb2g_#m_L2_f * Vb2g_#m_L2
        + Veg_#m_L2_f * Veg_#m_L2)
end
