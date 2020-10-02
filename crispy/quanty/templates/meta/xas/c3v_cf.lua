--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Dq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}})
    Dsigma_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, {{2, 0, -7}})
    Dtau_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, {{4, 0, -21}})

    Dq_#f_i = $Dq(#f)_i_value
    Dsigma_#f_i = $Dsigma(#f)_i_value
    Dtau_#f_i = $Dtau(#f)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1(t2g) %8.3f\n", -4 * Dq_#f_i - 2 * Dsigma_#f_i - 6 * Dtau_#f_i))
    io.write(string.format("e(eg)   %8.3f\n", 6 * Dq_#f_i + 7 / 3 * Dtau_#f_i))
    io.write(string.format("e(t2g)  %8.3f\n", -4 * Dq_#f_i + Dsigma_#f_i + 2 / 3 * Dtau_#f_i))
    io.write("================\n")
    io.write("Note: For C3v symmetry the crystal field Hamiltonian is expressed in the basis\n")
    io.write("      of the irreducible representations.\n")
    io.write("\n")

    Dq_#f_f = $Dq(#f)_f_value
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