#header
--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_#i = NewOperator("Number", NFermions, IndexUp_#i, IndexUp_#i, {1})
     + NewOperator("Number", NFermions, IndexDn_#i, IndexDn_#i, {1})

N_#f = NewOperator("Number", NFermions, IndexUp_#f, IndexUp_#f, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_#f, IndexDn_#f, {1, 1, 1, 1, 1})

if AtomicTerm then
    F0_#f_#f = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, {1, 0, 0})
    F2_#f_#f = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, {0, 1, 0})
    F4_#f_#f = NewOperator("U", NFermions, IndexUp_#f, IndexDn_#f, {0, 0, 1})

    F0_#i_#f = NewOperator("U", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {1}, {0})
    G2_#i_#f = NewOperator("U", NFermions, IndexUp_#i, IndexDn_#i, IndexUp_#f, IndexDn_#f, {0}, {1})

    U_#f_#f_i = $U(#f,#f)_i_value
    F2_#f_#f_i = $F2(#f,#f)_i_value * $F2(#f,#f)_i_scaleFactor
    F4_#f_#f_i = $F4(#f,#f)_i_value * $F4(#f,#f)_i_scaleFactor
    F0_#f_#f_i = U_#f_#f_i + 2 / 63 * F2_#f_#f_i + 2 / 63 * F4_#f_#f_i

    U_#f_#f_f = $U(#f,#f)_f_value
    F2_#f_#f_f = $F2(#f,#f)_f_value * $F2(#f,#f)_f_scaleFactor
    F4_#f_#f_f = $F4(#f,#f)_f_value * $F4(#f,#f)_f_scaleFactor
    F0_#f_#f_f = U_#f_#f_f + 2 / 63 * F2_#f_#f_f + 2 / 63 * F4_#f_#f_f
    U_#i_#f_f = $U(#i,#f)_f_value
    G2_#i_#f_f = $G2(#i,#f)_f_value * $G2(#i,#f)_f_scaleFactor
    F0_#i_#f_f = U_#i_#f_f + 1 / 10 * G2_#i_#f_f

    H_i = H_i + Chop(
          F0_#f_#f_i * F0_#f_#f
        + F2_#f_#f_i * F2_#f_#f
        + F4_#f_#f_i * F4_#f_#f)

    H_f = H_f + Chop(
          F0_#f_#f_f * F0_#f_#f
        + F2_#f_#f_f * F2_#f_#f
        + F4_#f_#f_f * F4_#f_#f
        + F0_#i_#f_f * F0_#i_#f
        + G2_#i_#f_f * G2_#i_#f)

    ldots_#f = NewOperator("ldots", NFermions, IndexUp_#f, IndexDn_#f)

    zeta_#f_i = $zeta(#f)_i_value * $zeta(#f)_i_scaleFactor

    zeta_#f_f = $zeta(#f)_f_value * $zeta(#f)_f_scaleFactor

    H_i = H_i + Chop(
          zeta_#f_i * ldots_#f)

    H_f = H_f + Chop(
          zeta_#f_f * ldots_#f)
end

#symmetry_term
#fields_term
#restrictions
#helper_functions
#footer