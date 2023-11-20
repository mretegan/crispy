--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Dq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}})
    Dsigma_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, {{2, 0, -7}})
    Dtau_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, {{4, 0, -21}})

    Dq_#f_i = $10Dq(#f)_i_value / 10.0
    Dsigma_#f_i = $Dsigma(#f)_i_value
    Dtau_#f_i = $Dtau(#f)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1(t2g) %8.3f\n", -4 * Dq_#f_i - 2 * Dsigma_#f_i - 6 * Dtau_#f_i))
    io.write(string.format("e(t2g)  %8.3f\n", -4 * Dq_#f_i + Dsigma_#f_i + 2 / 3 * Dtau_#f_i))
    io.write(string.format("e(eg)   %8.3f\n", 6 * Dq_#f_i + 7 / 3 * Dtau_#f_i))
    io.write("================\n")
    io.write("For the C3v symmetry, the crystal field Hamiltonian is not necessarily diagonal in\n")
    io.write("the basis of the irreducible representations. See the König and Kremer book, page 56.\n")
    io.write(string.format("The non-digonal element <e(t2g)|H|e(eg)> is %.3f.\n", -math.sqrt(2) / 3 * (3 * Dsigma_#f_i - 5 * Dtau_#f_i)))
    io.write("\n")

    Dq_#f_f = $10Dq(#f)_f_value / 10.0
    Dsigma_#f_f = $Dsigma(#f)_f_value
    Dtau_#f_f = $Dtau(#f)_f_value

    H_i = H_i + Chop(
          Dq_#f_i * Dq_#f
        + Dsigma_#f_i * Dsigma_#f
        + Dtau_#f_i * Dtau_#f)

    H_f = H_f + Chop(
          Dq_#f_f * Dq_#f
        + Dsigma_#f_f * Dsigma_#f
        + Dtau_#f_f * Dtau_#f)
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

  Akm = {{1, 0, -math.sqrt(3 / 5)}, {3, 0, -7 / math.sqrt(15)}}
  Va1_#f_4p = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_4p, IndexDn_4p, Akm)
            + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, Akm)

  Akm = {{1, 0, math.sqrt(6 / 5)}, {3, 0, -14 / 3 * math.sqrt(2 / 15)}, {3, 3, -7 / 3 / math.sqrt(3)}, {3, -3, 7 / 3 / math.sqrt(3)}}
  Ve_eg_#f_4p = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_4p, IndexDn_4p, Akm)
              + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, Akm)

  Akm = {{1, 0, math.sqrt(3 / 5)}, {3, 0, -14 / 3 / math.sqrt(15)}, {3, 3, 7 / 3 * math.sqrt(2 / 3)}, {3, -3, -7 / 3 * math.sqrt(2 / 3)}}
  Ve_t2g_#f_4p = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_4p, IndexDn_4p, Akm)
               + NewOperator("CF", NFermions, IndexUp_4p, IndexDn_4p, IndexUp_#f, IndexDn_#f, Akm)

  Va1_#f_4p_i = $Va1(#f,4p)_i_value
  Ve_eg_#f_4p_i = $Ve(eg)(#f,4p)_i_value
  Ve_t2g_#f_4p_i = $Ve(t2g)(#f,4p)_i_value

  Va1_#f_4p_f = $Va1(#f,4p)_f_value
  Ve_eg_#f_4p_f = $Ve(eg)(#f,4p)_f_value
  Ve_t2g_#f_4p_f = $Ve(t2g)(#f,4p)_f_value

  H_i = H_i + Chop(
        Va1_#f_4p_i * Va1_#f_4p
      + Ve_eg_#f_4p_i * Ve_eg_#f_4p
      + Ve_t2g_#f_4p_i * Ve_t2g_#f_4p)

  H_f = H_f + Chop(
        Va1_#f_4p_f * Va1_#f_4p
      + Ve_eg_#f_4p_f * Ve_eg_#f_4p
      + Ve_t2g_#f_4p_f * Ve_t2g_#f_4p)
end
