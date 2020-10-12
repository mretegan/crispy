--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- PotentialExpandedOnClm("Td", 2, {Ee, Et2})
    -- tenDq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, PotentialExpandedOnClm("Td", 2, {-0.6, 0.4}))

    Akm = {{4, 0, -2.1}, {4, -4, -1.5 * sqrt(0.7)}, {4, 4, -1.5 * sqrt(0.7)}}
    tenDq_#m = NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, Akm)

    tenDq_#m_i = $10Dq(#m)_i_value

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("e       %8.3f\n", -0.6 * tenDq_#m_i))
    io.write(string.format("t2      %8.3f\n",  0.4 * tenDq_#m_i))
    io.write("================\n")
    io.write("\n")

    tenDq_#m_m = $10Dq(#m)_m_value

    tenDq_#m_f = $10Dq(#m)_f_value

    H_i = H_i + Chop(
          tenDq_#m_i * tenDq_#m)

    H_m = H_m + Chop(
          tenDq_#m_m * tenDq_#m)

    H_f = H_f + Chop(
          tenDq_#m_f * tenDq_#m)
end
