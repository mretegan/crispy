--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- PotentialExpandedOnClm("Oh", 3, {Ea2u, Et1u, Et2u})
    -- Ea2u_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))
    -- Et2u_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))
    -- Et1u_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))

    B40_#f_i = $B40(#f)_i_value
    B60_#f_i = $B60(#f)_i_value

    Akm_#f_i = {
        {4,  0, B40_#f_i},
        {4, -4, math.sqrt(5/14) * B40_#f_i},
        {4,  4, math.sqrt(5/14) * B40_#f_i},
        {6,  0, B60_#f_i},
        {6, -4, -math.sqrt(7/2) * B60_#f_i},
        {6,  4, -math.sqrt(7/2) * B60_#f_i},
    }

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.        E\n")
    io.write("================\n")
    io.write(string.format("a2u     %8.3f\n", -4 / 11 * B40_#f_i +  80 / 143 * B60_#f_i))
    io.write(string.format("t1u     %8.3f\n",  2 / 11 * B40_#f_i + 100 / 429 * B60_#f_i))
    io.write(string.format("t2u     %8.3f\n", -2 / 33 * B40_#f_i -  60 / 143 * B60_#f_i))
    io.write("================\n")
    io.write("\n")

    B40_#f_f = $B40(#f)_f_value
    B60_#f_f = $B60(#f)_f_value

    Akm_#f_f = {
        {4,  0, B40_#f_f},
        {4, -4, math.sqrt(5/14) * B40_#f_f},
        {4,  4, math.sqrt(5/14) * B40_#f_f},
        {6,  0, B60_#f_f},
        {6, -4, -math.sqrt(7/2) * B60_#f_f},
        {6,  4, -math.sqrt(7/2) * B60_#f_f},
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_i))

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm_#f_f))
end

--------------------------------------------------------------------------------
-- Define the #f-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if H_#f_ligands_hybridization_lmct == 1 then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1, 1, 1})

    Delta_#f_L1_i = $Delta(#f,L1)_i_value
    e_#f_i = (28 * Delta_#f_L1_i - 27 * U_#f_#f_i * NElectrons_#f - U_#f_#f_i * NElectrons_#f^2) / (2 * (14 + NElectrons_#f))
    e_L1_i = NElectrons_#f * (-2 * Delta_#f_L1_i + U_#f_#f_i * NElectrons_#f + U_#f_#f_i) / (2 * (NElectrons_#f + 14))

    Delta_#f_L1_f = $Delta(#f,L1)_f_value
    e_#f_f = (28 * Delta_#f_L1_f - 460 * U_#i_#f_f - U_#f_#f_f * NElectrons_#f^2 - 47 * U_#f_#f_f * NElectrons_#f) / (2 * (NElectrons_#f + 24))
    e_#i_f = (28 * Delta_#f_L1_f - 2 * U_#i_#f_f * NElectrons_#f^2 - 30 * U_#i_#f_f * NElectrons_#f - 28 * U_#i_#f_f + U_#f_#f_f * NElectrons_#f^2 + U_#f_#f_f * NElectrons_#f) / (2 * (NElectrons_#f + 24))
    e_L1_f = (-2 * Delta_#f_L1_f * NElectrons_#f - 20 * Delta_#f_L1_f + 20 * U_#i_#f_f * NElectrons_#f + 20 * U_#i_#f_f + U_#f_#f_f * NElectrons_#f^2 + U_#f_#f_f * NElectrons_#f) / (2 * (NElectrons_#f + 24))

    H_i = H_i + Chop(
          e_#f_i * N_#f
        + e_L1_i * N_L1)

    H_f = H_f + Chop(
          e_#f_f * N_#f
        + e_#i_f * N_#i
        + e_L1_f * N_L1)

    B40_L1_i = $B40(L1)_i_value
    B60_L1_i = $B60(L1)_i_value

    Akm_L1_i = {
        {4,  0, B40_L1_i},
        {4, -4, math.sqrt(5/14) * B40_L1_i},
        {4,  4, math.sqrt(5/14) * B40_L1_i},
        {6,  0, B60_L1_i},
        {6, -4, -math.sqrt(7/2) * B60_L1_i},
        {6,  4, -math.sqrt(7/2) * B60_L1_i},
    }

    H_i = H_i + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_i))

    B40_L1_f = $B40(L1)_f_value
    B60_L1_f = $B60(L1)_f_value

    Akm_L1_f = {
        {4,  0, B40_L1_f},
        {4, -4, math.sqrt(5/14) * B40_L1_f},
        {4,  4, math.sqrt(5/14) * B40_L1_f},
        {6,  0, B60_L1_f},
        {6, -4, -math.sqrt(7/2) * B60_L1_f},
        {6,  4, -math.sqrt(7/2) * B60_L1_f},
    }

    H_f = H_f + Chop(NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm_L1_f))

    -- Mixing of the f-orbitals with the ligands.
    Va2u_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {1, 0, 0}))

    Vt2u_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 1, 0}))

    Vt1u_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))
               + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("Oh", 3, {0, 0, 1}))

    Va2u_#f_L1_i = $Va2u(#f,L1)_i_value
    Vt2u_#f_L1_i = $Vt2u(#f,L1)_i_value
    Vt1u_#f_L1_i = $Vt1u(#f,L1)_i_value

    Va2u_#f_L1_f = $Va2u(#f,L1)_f_value
    Vt2u_#f_L1_f = $Vt2u(#f,L1)_f_value
    Vt1u_#f_L1_f = $Vt1u(#f,L1)_f_value

    H_i = H_i + Chop(
        Va2u_#f_L1_i * Va2u_#f_L1
      + Vt2u_#f_L1_i * Vt2u_#f_L1
      + Vt1u_#f_L1_i * Vt1u_#f_L1)

    H_f = H_f + Chop(
        Va2u_#f_L1_f * Va2u_#f_L1
      + Vt2u_#f_L1_f * Vt2u_#f_L1
      + Vt1u_#f_L1_f * Vt1u_#f_L1)
end
