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