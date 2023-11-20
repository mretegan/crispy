--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Eav_#m_i = ($Ea2u(#m)_i_value + 3 * $Et1u(#m)_i_value + 3 * $Et2u(#m)_i_value) / 7
    Ea2u_#m_i = $Ea2u(#m)_i_value - Eav_#m_i
    Et1u_#m_i = $Et1u(#m)_i_value - Eav_#m_i
    Et2u_#m_i = $Et2u(#m)_i_value - Eav_#m_i

    Akm_#m_i = {
        {0, 0, (1 / 7) * (Ea2u_#m_i + (3) * (Et1u_#m_i + Et2u_#m_i))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_#m_i) + (-3) * (Et1u_#m_i) + Et2u_#m_i)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#m_i) + (-3) * (Et1u_#m_i) + Et2u_#m_i))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#m_i) + (-3) * (Et1u_#m_i) + Et2u_#m_i))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_#m_i) + (5) * (Et1u_#m_i) + (-9) * (Et2u_#m_i))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#m_i) + (5) * (Et1u_#m_i) + (-9) * (Et2u_#m_i)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#m_i) + (5) * (Et1u_#m_i) + (-9) * (Et2u_#m_i)))}
    }

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a2u     %8.3f\n", Ea2u_#m_i))
    io.write(string.format("t1u     %8.3f\n", Et1u_#m_i))
    io.write(string.format("t2u     %8.3f\n", Et2u_#m_i))
    io.write("================\n")
    io.write("\n")

    Eav_#m_m = ($Ea2u(#m)_m_value + 3 * $Et1u(#m)_m_value + 3 * $Et2u(#m)_m_value) / 7
    Ea2u_#m_m = $Ea2u(#m)_m_value - Eav_#m_m
    Et1u_#m_m = $Et1u(#m)_m_value - Eav_#m_m
    Et2u_#m_m = $Et2u(#m)_m_value - Eav_#m_m

    Akm_#m_m = {
        {0, 0, (1 / 7) * (Ea2u_#m_m + (3) * (Et1u_#m_m + Et2u_#m_m))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_#m_m) + (-3) * (Et1u_#m_m) + Et2u_#m_m)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#m_m) + (-3) * (Et1u_#m_m) + Et2u_#m_m))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#m_m) + (-3) * (Et1u_#m_m) + Et2u_#m_m))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_#m_m) + (5) * (Et1u_#m_m) + (-9) * (Et2u_#m_m))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#m_m) + (5) * (Et1u_#m_m) + (-9) * (Et2u_#m_m)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#m_m) + (5) * (Et1u_#m_m) + (-9) * (Et2u_#m_m)))}
    }

    Eav_#m_f = ($Ea2u(#m)_f_value + 3 * $Et1u(#m)_f_value + 3 * $Et2u(#m)_f_value) / 7
    Ea2u_#m_f = $Ea2u(#m)_f_value - Eav_#m_f
    Et1u_#m_f = $Et1u(#m)_f_value - Eav_#m_f
    Et2u_#m_f = $Et2u(#m)_f_value - Eav_#m_f

    Akm_#m_f = {
        {0, 0, (1 / 7) * (Ea2u_#m_f + (3) * (Et1u_#m_f + Et2u_#m_f))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_#m_f) + (-3) * (Et1u_#m_f) + Et2u_#m_f)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#m_f) + (-3) * (Et1u_#m_f) + Et2u_#m_f))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#m_f) + (-3) * (Et1u_#m_f) + Et2u_#m_f))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_#m_f) + (5) * (Et1u_#m_f) + (-9) * (Et2u_#m_f))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#m_f) + (5) * (Et1u_#m_f) + (-9) * (Et2u_#m_f)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#m_f) + (5) * (Et1u_#m_f) + (-9) * (Et2u_#m_f)))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_i))

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_m))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm_#m_f))
end

--------------------------------------------------------------------------------
-- Define the #m-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1, 1, 1})

    Delta_#m_L1_i = $Delta(#m,L1)_i_value
    E_#m_i = (28 * Delta_#m_L1_i - 27 * U_#m_#m_i * NElectrons_#m - U_#m_#m_i * NElectrons_#m^2) / (2 * (14 + NElectrons_#m))
    E_L1_i = NElectrons_#m * (-2 * Delta_#m_L1_i + U_#m_#m_i * NElectrons_#m + U_#m_#m_i) / (2 * (NElectrons_#m + 14))

    Delta_#m_L1_m = $Delta(#m,L1)_m_value
    E_#m_m = (28 * Delta_#m_L1_m - U_#m_#m_m * NElectrons_#m^2 - 39 * U_#m_#m_m * NElectrons_#m - 228 * U_#i_#m_m) / (2 * (NElectrons_#m + 20))
    E_#i_m = (28 * Delta_#m_L1_m + U_#m_#m_m * NElectrons_#m^2 + U_#m_#m_m * NElectrons_#m - 2 * U_#i_#m_m * NElectrons_#m^2 - 30 * U_#i_#m_m * NElectrons_#m - 28 * U_#i_#m_m) / (2 * (NElectrons_#m + 20))
    E_L1_m = (-2 * Delta_#m_L1_m * NElectrons_#m - 12 * Delta_#m_L1_m + U_#m_#m_m * NElectrons_#m^2 + U_#m_#m_m * NElectrons_#m + 12 * U_#i_#m_m * NElectrons_#m + 12 * U_#i_#m_m) / (2 * (NElectrons_#m + 20))

    Delta_#m_L1_f = $Delta(#m,L1)_f_value
    E_#m_f = (28 * Delta_#m_L1_f - 460 * U_#f_#m_f - U_#m_#m_f * NElectrons_#m^2 - 47 * U_#m_#m_f * NElectrons_#m) / (2 * (NElectrons_#m + 24))
    E_#f_f = (28 * Delta_#m_L1_f - 2 * U_#f_#m_f * NElectrons_#m^2 - 30 * U_#f_#m_f * NElectrons_#m - 28 * U_#f_#m_f + U_#m_#m_f * NElectrons_#m^2 + U_#m_#m_f * NElectrons_#m) / (2 * (NElectrons_#m + 24))
    E_L1_f = (-2 * Delta_#m_L1_f * NElectrons_#m - 20 * Delta_#m_L1_f + 20 * U_#f_#m_f * NElectrons_#m + 20 * U_#f_#m_f + U_#m_#m_f * NElectrons_#m^2 + U_#m_#m_f * NElectrons_#m) / (2 * (NElectrons_#m + 24))

    H_i = H_i + Chop(
          E_#m_i * N_#m
        + E_L1_i * N_L1)

    H_m = H_f + Chop(
          E_#m_m * N_#m
        + E_#i_m * N_#i
        + E_L1_m * N_L1)

    H_f = H_f + Chop(
          E_#m_f * N_#m
        + E_#f_f * N_#f
        + E_L1_f * N_L1)

    Eav_L1_i = ($Ea2u(L1)_i_value + 3 * $Et1u(L1)_i_value + 3 * $Et2u(L1)_i_value) / 7
    Ea2u_L1_i = $Ea2u(L1)_i_value - Eav_L1_i
    Et1u_L1_i = $Et1u(L1)_i_value - Eav_L1_i
    Et2u_L1_i = $Et2u(L1)_i_value - Eav_L1_i

    Akm_L1_i = {
        {0, 0, (1 / 7) * (Ea2u_L1_i + (3) * (Et1u_L1_i + Et2u_L1_i))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_L1_i) + (-3) * (Et1u_L1_i) + Et2u_L1_i)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_i) + (-3) * (Et1u_L1_i) + Et2u_L1_i))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_i) + (-3) * (Et1u_L1_i) + Et2u_L1_i))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_L1_i) + (5) * (Et1u_L1_i) + (-9) * (Et2u_L1_i))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_i) + (5) * (Et1u_L1_i) + (-9) * (Et2u_L1_i)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_i) + (5) * (Et1u_L1_i) + (-9) * (Et2u_L1_i)))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_i))

    Eav_L1_m = ($Ea2u(L1)_m_value + 3 * $Et1u(L1)_m_value + 3 * $Et2u(L1)_m_value) / 7
    Ea2u_L1_m = $Ea2u(L1)_m_value - Eav_L1_m
    Et1u_L1_m = $Et1u(L1)_m_value - Eav_L1_m
    Et2u_L1_m = $Et2u(L1)_m_value - Eav_L1_m

    Akm_L1_m = {
        {0, 0, (1 / 7) * (Ea2u_L1_m + (3) * (Et1u_L1_m + Et2u_L1_m))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_L1_m) + (-3) * (Et1u_L1_m) + Et2u_L1_m)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_m) + (-3) * (Et1u_L1_m) + Et2u_L1_m))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_m) + (-3) * (Et1u_L1_m) + Et2u_L1_m))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_L1_m) + (5) * (Et1u_L1_m) + (-9) * (Et2u_L1_m))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_m) + (5) * (Et1u_L1_m) + (-9) * (Et2u_L1_m)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_m) + (5) * (Et1u_L1_m) + (-9) * (Et2u_L1_m)))}
    }

    H_m = H_m + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_m))

    Eav_L1_f = ($Ea2u(L1)_f_value + 3 * $Et1u(L1)_f_value + 3 * $Et2u(L1)_f_value) / 7
    Ea2u_L1_f = $Ea2u(L1)_f_value - Eav_L1_f
    Et1u_L1_f = $Et1u(L1)_f_value - Eav_L1_f
    Et2u_L1_f = $Et2u(L1)_f_value - Eav_L1_f

    Akm_L1_f = {
        {0, 0, (1 / 7) * (Ea2u_L1_f + (3) * (Et1u_L1_f + Et2u_L1_f))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_L1_f) + (-3) * (Et1u_L1_f) + Et2u_L1_f)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_f) + (-3) * (Et1u_L1_f) + Et2u_L1_f))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_L1_f) + (-3) * (Et1u_L1_f) + Et2u_L1_f))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_L1_f) + (5) * (Et1u_L1_f) + (-9) * (Et2u_L1_f))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_f) + (5) * (Et1u_L1_f) + (-9) * (Et2u_L1_f)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_L1_f) + (5) * (Et1u_L1_f) + (-9) * (Et2u_L1_f)))}
    }

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_f))

    -- Mixing of the f-orbitals with the ligands.
    Va2u_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))

    Vt1u_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))

    Vt2u_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))

    Va2u_#m_L1_i = $Va2u(#m,L1)_i_value
    Vt1u_#m_L1_i = $Vt1u(#m,L1)_i_value
    Vt2u_#m_L1_i = $Vt2u(#m,L1)_i_value

    Va2u_#m_L1_f = $Va2u(#m,L1)_f_value
    Vt1u_#m_L1_f = $Vt1u(#m,L1)_f_value
    Vt2u_#m_L1_f = $Vt2u(#m,L1)_f_value

    H_i = H_i + Chop(
        Va2u_#m_L1_i * Va2u_#m_L1
      + Vt1u_#m_L1_i * Vt1u_#m_L1)
      + Vt2u_#m_L1_i * Vt2u_#m_L1

    H_f = H_f + Chop(
        Va2u_#m_L1_f * Va2u_#m_L1
      + Vt1u_#m_L1_f * Vt1u_#m_L1)
      + Vt2u_#m_L1_f * Vt2u_#m_L1
end
