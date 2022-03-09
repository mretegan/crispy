#header
--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_#i = NewOperator("Number", NFermions, IndexUp_#i, IndexUp_#i, {1})
     + NewOperator("Number", NFermions, IndexDn_#i, IndexDn_#i, {1})

N_#f = NewOperator("Number", NFermions, IndexUp_#f, IndexUp_#f, {1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_#f, IndexDn_#f, {1, 1, 1})

N_#m = NewOperator("Number", NFermions, IndexUp_#m, IndexUp_#m, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_#m, IndexDn_#m, {1, 1, 1, 1, 1})

if AtomicTerm then
    F0_#m_#m = NewOperator("U", NFermions, IndexUp_#m, IndexDn_#m, {1, 0, 0})
    F2_#m_#m = NewOperator("U", NFermions, IndexUp_#m, IndexDn_#m, {0, 1, 0})
    F4_#m_#m = NewOperator("U", NFermions, IndexUp_#m, IndexDn_#m, {0, 0, 1})

    F0_#f_#m = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#m, IndexDn_#m, {1, 0}, {0, 0})
    F2_#f_#m = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#m, IndexDn_#m, {0, 1}, {0, 0})
    G1_#f_#m = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#m, IndexDn_#m, {0, 0}, {1, 0})
    G3_#f_#m = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_#m, IndexDn_#m, {0, 0}, {0, 1})

    F0_#i_#m = NewOperator("U", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#m, IndexDn_#m, {1}, {0})
    G2_#i_#m = NewOperator("U", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#m, IndexDn_#m, {0}, {1})

    U_#m_#m_i = $U(#m,#m)_i_value
    F2_#m_#m_i = $F2(#m,#m)_i_value * $F2(#m,#m)_i_scaleFactor
    F4_#m_#m_i = $F4(#m,#m)_i_value * $F4(#m,#m)_i_scaleFactor
    F0_#m_#m_i = U_#m_#m_i + 2 / 63 * F2_#m_#m_i + 2 / 63 * F4_#m_#m_i

    U_#m_#m_m = $U(#m,#m)_m_value
    F2_#m_#m_m = $F2(#m,#m)_m_value * $F2(#m,#m)_m_scaleFactor
    F4_#m_#m_m = $F4(#m,#m)_m_value * $F4(#m,#m)_m_scaleFactor
    F0_#m_#m_m = U_#m_#m_m + 2 / 63 * F2_#m_#m_m + 2 / 63 * F4_#m_#m_m
    U_#i_#m_m = $U(#i,#m)_m_value
    G2_#i_#m_m = $G2(#i,#m)_m_value * $G2(#i,#m)_m_scaleFactor
    F0_#i_#m_m = U_#i_#m_m + 1 / 10 * G2_#i_#m_m

    U_#m_#m_f = $U(#m,#m)_f_value
    F2_#m_#m_f = $F2(#m,#m)_f_value * $F2(#m,#m)_f_scaleFactor
    F4_#m_#m_f = $F4(#m,#m)_f_value * $F4(#m,#m)_f_scaleFactor
    F0_#m_#m_f = U_#m_#m_f + 2 / 63 * F2_#m_#m_f + 2 / 63 * F4_#m_#m_f
    U_#f_#m_f = $U(#f,#m)_f_value
    F2_#f_#m_f = $F2(#f,#m)_f_value * $F2(#f,#m)_f_scaleFactor
    G1_#f_#m_f = $G1(#f,#m)_f_value * $G1(#f,#m)_f_scaleFactor
    G3_#f_#m_f = $G3(#f,#m)_f_value * $G3(#f,#m)_f_scaleFactor
    F0_#f_#m_f = U_#f_#m_f + 1 / 15 * G1_#f_#m_f + 3 / 70 * G3_#f_#m_f

    H_i = H_i + Chop(
          F0_#m_#m_i * F0_#m_#m
        + F2_#m_#m_i * F2_#m_#m
        + F4_#m_#m_i * F4_#m_#m)

    H_m = H_m + Chop(
          F0_#m_#m_m * F0_#m_#m
        + F2_#m_#m_m * F2_#m_#m
        + F4_#m_#m_m * F4_#m_#m
        + F0_#i_#m_m * F0_#i_#m
        + G2_#i_#m_m * G2_#i_#m)

    H_f = H_f + Chop(
          F0_#m_#m_f * F0_#m_#m
        + F2_#m_#m_f * F2_#m_#m
        + F4_#m_#m_f * F4_#m_#m
        + F0_#f_#m_f * F0_#f_#m
        + F2_#f_#m_f * F2_#f_#m
        + G1_#f_#m_f * G1_#f_#m
        + G3_#f_#m_f * G3_#f_#m)

    ldots_#m = NewOperator("ldots", NFermions, IndexUp_#m, IndexDn_#m)

    ldots_#f = NewOperator("ldots", NFermions, IndexUp_#f, IndexDn_#f)

    zeta_#m_i = $zeta(#m)_i_value * $zeta(#m)_i_scaleFactor

    zeta_#m_m = $zeta(#m)_m_value * $zeta(#m)_m_scaleFactor

    zeta_#m_f = $zeta(#m)_f_value * $zeta(#m)_f_scaleFactor
    zeta_#f_f = $zeta(#f)_f_value * $zeta(#f)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_#m_i * ldots_#m)

    H_m = H_m + Chop(
          zeta_#m_m * ldots_#m)

    H_f = H_f + Chop(
          zeta_#m_f * ldots_#m
        + zeta_#f_f * ldots_#f)
end

#symmetry_term
#fields_term
#restrictions
#helper_functions
#footer