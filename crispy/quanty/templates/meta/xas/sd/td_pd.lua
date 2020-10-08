--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- PotentialExpandedOnClm("Td", 2, {Ee, Et2})
    -- tenDq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, PotentialExpandedOnClm("Td", 2, {-0.6, 0.4}))

    Akm = {{4, 0, -2.1}, {4, -4, -1.5 * sqrt(0.7)}, {4, 4, -1.5 * sqrt(0.7)}}
    tenDq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    tenDq_#f_i = $10Dq(#f)_i_value

    io.write("Energies of the #f orbitals in the initial Hamiltonian (crystal field term only):\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("e       %8.3f\n", -0.6 * tenDq_#f_i))
    io.write(string.format("t2      %8.3f\n",  0.4 * tenDq_#f_i))
    io.write("================\n")
    io.write("\n")

    tenDq_#f_f = $10Dq(#f)_f_value

    H_i = H_i + Chop(
          tenDq_#f_i * tenDq_#f)

    H_f = H_f + Chop(
          tenDq_#f_f * tenDq_#f)
end

--------------------------------------------------------------------------------
-- Define the #f-4p hybridization term.
--------------------------------------------------------------------------------
if PdHybridizationTerm then
    F0_#f_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, {1, 0}, {0, 0})
    F2_#f_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, {0, 1}, {0, 0})
    G1_#f_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, {0, 0}, {1, 0})
    G3_#f_4p = NewOperator("U", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, {0, 0}, {0, 1})
    G1_#i_4p = NewOperator("U", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_4p, IndexDn_4p, {0}, {1})

    F2_#f_4p_i = $F2(#f,4p)_i_value * $F2(#f,4p)_i_scaleFactor
    G1_#f_4p_i = $G1(#f,4p)_i_value * $G1(#f,4p)_i_scaleFactor
    G3_#f_4p_i = $G3(#f,4p)_i_value * $G3(#f,4p)_i_scaleFactor

    F2_#f_4p_f = $F2(#f,4p)_i_value * $F2(#f,4p)_i_scaleFactor
    G1_#f_4p_f = $G1(#f,4p)_i_value * $G1(#f,4p)_i_scaleFactor
    G3_#f_4p_f = $G3(#f,4p)_i_value * $G3(#f,4p)_i_scaleFactor
    G1_#i_4p_f = $G1(#i,4p)_f_value * $G1(#i,4p)_f_scaleFactor

    H_i = H_i + Chop(
          F2_#f_4p_i * F2_#f_4p
        + G1_#f_4p_i * G1_#f_4p
        + G3_#f_4p_i * G3_#f_4p)

    H_f = H_f + Chop(
          F2_#f_4p_f * F2_#f_4p
        + G1_#f_4p_f * G1_#f_4p
        + G3_#f_4p_f * G3_#f_4p
        + G1_#i_4p_f * G1_#i_4p)

    ldots_4p = NewOperator("ldots", NFermions, IndexUp_4p, IndexDn_4p)

    zeta_4p_i = $zeta(4p)_i_value

    zeta_4p_f = $zeta(4p)_f_value

    H_i = H_i + Chop(
          zeta_4p_i * ldots_4p)

    H_f = H_f + Chop(
          zeta_4p_f * ldots_4p)

    N_4p = NewOperator("Number", NFermions, IndexUp_4p, IndexUp_4p, {1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_4p, IndexDn_4p, {1, 1, 1})

    Delta_#f_4p_i = $Delta(#f,4p)_i_value
    e_#f_i = -(NElectrons_#f - 1) * U_#f_#f_i / 2
    e_4p_i =  (NElectrons_#f - 1) * U_#f_#f_i / 2 + Delta_#f_4p_i

    Delta_#f_4p_f = $Delta(#f,4p)_f_value
    e_#f_f= -(NElectrons_#f - 1) * U_#f_#f_f / 2
    e_4p_f=  (NElectrons_#f - 1) * U_#f_#f_f / 2 + Delta_#f_4p_f

    H_i = H_i + Chop(
          e_#f_i * N_#f
        + e_4p_i * N_4p)

    H_f = H_f + Chop(
          e_#f_f * N_#f
        + e_4p_f * N_4p)

    Akm = {{3, 2, (-7 * I) / math.sqrt(6)}, {3, -2, (7 * I) / math.sqrt(6)}}
    Vt2_#f_4p = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_4p, IndexDn_4p, Akm)
              + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, Akm)

    Vt2_#f_4p_i = $Vt2(#f,4p)_i_value

    Vt2_#f_4p_f = $Vt2(#f,4p)_f_value

    H_i = H_i + Chop(
          Vt2_#f_4p_i * Vt2_#f_4p)

    H_f = H_f + Chop(
          Vt2_#f_4p_f * Vt2_#f_4p)
end
