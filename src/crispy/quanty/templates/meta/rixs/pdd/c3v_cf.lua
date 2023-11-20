--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Akm = {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}}
    Dq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{2, 0, -7}}
    Dsigma_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Akm = {{4, 0, -21}}
    Dtau_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    Dq_#m_i = $10Dq(#m)_i_value / 10.0
    Dsigma_#m_i = $Dsigma(#m)_i_value
    Dtau_#m_i = $Dtau(#m)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1(t2g) %8.3f\n", -4 * Dq_#m_i - 2 * Dsigma_#m_i - 6 * Dtau_#m_i))
    io.write(string.format("e(eg)   %8.3f\n", 6 * Dq_#m_i + 7 / 3 * Dtau_#m_i))
    io.write(string.format("e(t2g)  %8.3f\n", -4 * Dq_#m_i + Dsigma_#m_i + 2 / 3 * Dtau_#m_i))
    io.write("================\n")
    io.write("For the C3v symmetry, the crystal field Hamiltonian is not necessarily diagonal in\n")
    io.write("the basis of the irreducible representations. See the König and Kremer book, page 56.\n")
    io.write(string.format("The non-digonal element <e(t2g)|H|e(eg)> is %.3f.\n", -math.sqrt(2) / 3 * (3 * Dsigma_#f_i - 5 * Dtau_#f_i)))
    io.write("\n")


    Dq_#m_m = $10Dq(#m)_m_value / 10.0
    Dsigma_#m_m = $Dsigma(#m)_m_value
    Dtau_#m_m = $Dtau(#m)_m_value

    Dq_#m_f = $10Dq(#m)_f_value / 10.0
    Dsigma_#m_f = $Dsigma(#m)_f_value
    Dtau_#m_f = $Dtau(#m)_f_value

    H_i = H_i + Chop(
          Dq_#m_i * Dq_#m
        + Dsigma_#m_i * Dsigma_#m
        + Dtau_#m_i * Dtau_#m)

    H_m = H_m + Chop(
          Dq_#m_m * Dq_#m
        + Dsigma_#m_m * Dsigma_#m
        + Dtau_#m_m * Dtau_#m)

    H_f = H_f + Chop(
          Dq_#m_f * Dq_#m
        + Dsigma_#m_f * Dsigma_#m
        + Dtau_#m_f * Dtau_#m)
end
