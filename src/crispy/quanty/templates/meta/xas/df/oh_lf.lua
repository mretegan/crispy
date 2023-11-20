--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Eav_#f_i = ($Ea2u(#f)_i_value + 3 * $Et1u(#f)_i_value + 3 * $Et2u(#f)_i_value) / 7
    Ea2u_#f_i = $Ea2u(#f)_i_value - Eav_#f_i
    Et1u_#f_i = $Et1u(#f)_i_value - Eav_#f_i
    Et2u_#f_i = $Et2u(#f)_i_value - Eav_#f_i

    Akm_#f_i = {
        {0, 0, (1 / 7) * (Ea2u_#f_i + (3) * (Et1u_#f_i + Et2u_#f_i))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_#f_i) + (-3) * (Et1u_#f_i) + Et2u_#f_i)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#f_i) + (-3) * (Et1u_#f_i) + Et2u_#f_i))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#f_i) + (-3) * (Et1u_#f_i) + Et2u_#f_i))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_#f_i) + (5) * (Et1u_#f_i) + (-9) * (Et2u_#f_i))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#f_i) + (5) * (Et1u_#f_i) + (-9) * (Et2u_#f_i)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#f_i) + (5) * (Et1u_#f_i) + (-9) * (Et2u_#f_i)))}
    }

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a2u     %8.3f\n", Ea2u_#f_i))
    io.write(string.format("t1u     %8.3f\n", Et1u_#f_i))
    io.write(string.format("t2u     %8.3f\n", Et2u_#f_i))
    io.write("================\n")
    io.write("\n")

    Eav_#f_f = ($Ea2u(#f)_f_value + 3 * $Et1u(#f)_f_value + 3 * $Et2u(#f)_f_value) / 7
    Ea2u_#f_f = $Ea2u(#f)_f_value - Eav_#f_f
    Et1u_#f_f = $Et1u(#f)_f_value - Eav_#f_f
    Et2u_#f_f = $Et2u(#f)_f_value - Eav_#f_f

    Akm_#f_f = {
        {0, 0, (1 / 7) * (Ea2u_#f_f + (3) * (Et1u_#f_f + Et2u_#f_f))},
        {4, 0, (-3 / 4) * ((2) * (Ea2u_#f_f) + (-3) * (Et1u_#f_f) + Et2u_#f_f)},
        {4, -4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#f_f) + (-3) * (Et1u_#f_f) + Et2u_#f_f))},
        {4, 4, (-3 / 4) * ((sqrt(5 / 14)) * ((2) * (Ea2u_#f_f) + (-3) * (Et1u_#f_f) + Et2u_#f_f))},
        {6, 0, (39 / 280) * ((4) * (Ea2u_#f_f) + (5) * (Et1u_#f_f) + (-9) * (Et2u_#f_f))},
        {6, -4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#f_f) + (5) * (Et1u_#f_f) + (-9) * (Et2u_#f_f)))},
        {6, 4, (-39 / 40) * ((1 / (sqrt(14))) * ((4) * (Ea2u_#f_f) + (5) * (Et1u_#f_f) + (-9) * (Et2u_#f_f)))}
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_i))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_f))
end

--------------------------------------------------------------------------------
-- Define the #f-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1, 1, 1})

    Delta_#f_L1_i = $Delta(#f,L1)_i_value
    E_#f_i = (28 * Delta_#f_L1_i - 27 * U_#f_#f_i * NElectrons_#f - U_#f_#f_i * NElectrons_#f^2) / (2 * (14 + NElectrons_#f))
    E_L1_i = NElectrons_#f * (-2 * Delta_#f_L1_i + U_#f_#f_i * NElectrons_#f + U_#f_#f_i) / (2 * (NElectrons_#f + 14))

    Delta_#f_L1_f = $Delta(#f,L1)_f_value
    E_#f_f = (28 * Delta_#f_L1_f - 460 * U_#i_#f_f - U_#f_#f_f * NElectrons_#f^2 - 47 * U_#f_#f_f * NElectrons_#f) / (2 * (NElectrons_#f + 24))
    E_#i_f = (28 * Delta_#f_L1_f - 2 * U_#i_#f_f * NElectrons_#f^2 - 30 * U_#i_#f_f * NElectrons_#f - 28 * U_#i_#f_f + U_#f_#f_f * NElectrons_#f^2 + U_#f_#f_f * NElectrons_#f) / (2 * (NElectrons_#f + 24))
    E_L1_f = (-2 * Delta_#f_L1_f * NElectrons_#f - 20 * Delta_#f_L1_f + 20 * U_#i_#f_f * NElectrons_#f + 20 * U_#i_#f_f + U_#f_#f_f * NElectrons_#f^2 + U_#f_#f_f * NElectrons_#f) / (2 * (NElectrons_#f + 24))

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L1_i * N_L1)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
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
    Va2u_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))

    Vt1u_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))

    Vt2u_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))

    Va2u_#f_L1_i = $Va2u(#f,L1)_i_value
    Vt1u_#f_L1_i = $Vt1u(#f,L1)_i_value
    Vt2u_#f_L1_i = $Vt2u(#f,L1)_i_value

    Va2u_#f_L1_f = $Va2u(#f,L1)_f_value
    Vt1u_#f_L1_f = $Vt1u(#f,L1)_f_value
    Vt2u_#f_L1_f = $Vt2u(#f,L1)_f_value

    H_i = H_i + Chop(
        Va2u_#f_L1_i * Va2u_#f_L1
      + Vt1u_#f_L1_i * Vt1u_#f_L1
      + Vt2u_#f_L1_i * Vt2u_#f_L1)

    H_f = H_f + Chop(
        Va2u_#f_L1_f * Va2u_#f_L1
      + Vt1u_#f_L1_f * Vt1u_#f_L1
      + Vt2u_#f_L1_f * Vt2u_#f_L1)
end
