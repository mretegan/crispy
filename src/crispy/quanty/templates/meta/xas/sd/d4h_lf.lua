--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if  CrystalFieldTerm then
    -- PotentialExpandedOnClm("D4h", 2, {Ea1g, Eb1g, Eb2g, Eeg})
    -- Dq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    -- Ds_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    -- Dt_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Akm = {{4, 0, 21}, {4, -4, 1.5 * sqrt(70)}, {4, 4, 1.5 * sqrt(70)}}
    Dq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{2, 0, -7}}
    Ds_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{4, 0, -21}}
    Dt_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Dq_#f_i = $10Dq(#f)_i_value / 10.0
    Ds_#f_i = $Ds(#f)_i_value
    Dt_#f_i = $Dt(#f)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1g     %8.3f\n", 6 * Dq_#f_i - 2 * Ds_#f_i - 6 * Dt_#f_i ))
    io.write(string.format("b1g     %8.3f\n", 6 * Dq_#f_i + 2 * Ds_#f_i - Dt_#f_i ))
    io.write(string.format("b2g     %8.3f\n", -4 * Dq_#f_i + 2 * Ds_#f_i - Dt_#f_i ))
    io.write(string.format("eg      %8.3f\n", -4 * Dq_#f_i - Ds_#f_i + 4 * Dt_#f_i))
    io.write("================\n")
    io.write("\n")

    Dq_#f_f = $10Dq(#f)_f_value / 10.0
    Ds_#f_f = $Ds(#f)_f_value
    Dt_#f_f = $Dt(#f)_f_value

    H_i = H_i + Chop(
          Dq_#f_i * Dq_#f
        + Ds_#f_i * Ds_#f
        + Dt_#f_i * Dt_#f)

    H_f = H_f + Chop(
          Dq_#f_f * Dq_#f
        + Ds_#f_f * Ds_#f
        + Dt_#f_f * Dt_#f)
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
    E_#f_f = (10 * Delta_#f_L1_f - NElectrons_#f * (23 + NElectrons_#f) * U_#f_#f_f / 2 - 22 * U_#i_#f_f) / (12 + NElectrons_#f)
    E_#i_f = (10 * Delta_#f_L1_f + (1 + NElectrons_#f) * (NElectrons_#f * U_#f_#f_f / 2 - (10 + NElectrons_#f) * U_#i_#f_f)) / (12 + NElectrons_#f)
    E_L1_f = (-2 * Delta_#f_L1_f * NElectrons_#f - 4 * Delta_#f_L1_f + U_#f_#f_f * NElectrons_#f^2 + U_#f_#f_f * NElectrons_#f + 4 * U_#i_#f_f * NElectrons_#f + 4 * U_#i_#f_f) / (2 * (NElectrons_#f + 12))

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L1_i * N_L1)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
        + E_L1_f * N_L1)

    Dq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L1_i = $10Dq(L1)_i_value / 10.0
    Ds_L1_i = $Ds(L1)_i_value
    Dt_L1_i = $Dt(L1)_i_value
    Va1g_#f_L1_i = $Va1g(#f,L1)_i_value
    Vb1g_#f_L1_i = $Vb1g(#f,L1)_i_value
    Vb2g_#f_L1_i = $Vb2g(#f,L1)_i_value
    Veg_#f_L1_i = $Veg(#f,L1)_i_value

    Dq_L1_f = $10Dq(L1)_f_value / 10.0
    Ds_L1_f = $Ds(L1)_f_value
    Dt_L1_f = $Dt(L1)_f_value
    Va1g_#f_L1_f = $Va1g(#f,L1)_f_value
    Vb1g_#f_L1_f = $Vb1g(#f,L1)_f_value
    Vb2g_#f_L1_f = $Vb2g(#f,L1)_f_value
    Veg_#f_L1_f = $Veg(#f,L1)_f_value

    H_i = H_i + Chop(
          Dq_L1_i * Dq_L1
        + Ds_L1_i * Ds_L1
        + Dt_L1_i * Dt_L1
        + Va1g_#f_L1_i * Va1g_#f_L1
        + Vb1g_#f_L1_i * Vb1g_#f_L1
        + Vb2g_#f_L1_i * Vb2g_#f_L1
        + Veg_#f_L1_i  * Veg_#f_L1)

    H_f = H_f + Chop(
          Dq_L1_f * Dq_L1
        + Ds_L1_f * Ds_L1
        + Dt_L1_f * Dt_L1
        + Va1g_#f_L1_f * Va1g_#f_L1
        + Vb1g_#f_L1_f * Vb1g_#f_L1
        + Vb2g_#f_L1_f * Vb2g_#f_L1
        + Veg_#f_L1_f  * Veg_#f_L1)
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
    E_#f_f = -(U_#f_#f_f * NElectrons_#f^2 + 3 * U_#f_#f_f * NElectrons_#f + 4 * U_#i_#f_f) / (2 * NElectrons_#f + 4)
    E_#i_f = NElectrons_#f * (U_#f_#f_f * NElectrons_#f + U_#f_#f_f - 2 * U_#i_#f_f * NElectrons_#f - 2 * U_#i_#f_f) / (2 * (NElectrons_#f + 2))
    E_L2_f = (2 * Delta_#f_L2_f * NElectrons_#f + 4 * Delta_#f_L2_f + U_#f_#f_f * NElectrons_#f^2 - U_#f_#f_f * NElectrons_#f - 4 * U_#f_#f_f + 4 * U_#i_#f_f * NElectrons_#f + 4 * U_#i_#f_f) / (2 * (NElectrons_#f + 2))

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L2_i * N_L2)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
        + E_L2_f * N_L2)

    Dq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L2_i = $10Dq(L2)_i_value / 10.0
    Ds_L2_i = $Ds(L2)_i_value
    Dt_L2_i = $Dt(L2)_i_value
    Va1g_#f_L2_i = $Va1g(#f,L2)_i_value
    Vb1g_#f_L2_i = $Vb1g(#f,L2)_i_value
    Vb2g_#f_L2_i = $Vb2g(#f,L2)_i_value
    Veg_#f_L2_i = $Veg(#f,L2)_i_value

    Dq_L2_f = $10Dq(L2)_f_value / 10.0
    Ds_L2_f = $Ds(L2)_f_value
    Dt_L2_f = $Dt(L2)_f_value
    Va1g_#f_L2_f = $Va1g(#f,L2)_f_value
    Vb1g_#f_L2_f = $Vb1g(#f,L2)_f_value
    Vb2g_#f_L2_f = $Vb2g(#f,L2)_f_value
    Veg_#f_L2_f = $Veg(#f,L2)_f_value

    H_i = H_i + Chop(
          Dq_L2_i * Dq_L2
        + Ds_L2_i * Ds_L2
        + Dt_L2_i * Dt_L2
        + Va1g_#f_L2_i * Va1g_#f_L2
        + Vb1g_#f_L2_i * Vb1g_#f_L2
        + Vb2g_#f_L2_i * Vb2g_#f_L2
        + Veg_#f_L2_i  * Veg_#f_L2)

    H_f = H_f + Chop(
          Dq_L2_f * Dq_L2
        + Ds_L2_f * Ds_L2
        + Dt_L2_f * Dt_L2
        + Va1g_#f_L2_f * Va1g_#f_L2
        + Vb1g_#f_L2_f * Vb1g_#f_L2
        + Vb2g_#f_L2_f * Vb2g_#f_L2
        + Veg_#f_L2_f  * Veg_#f_L2)
end
