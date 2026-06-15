--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- Td crystal field for d electrons, cube-axis (xyz) setting: the tetrahedron is
    -- inscribed in a cube with edges along x, y and z, so the S4/C2 axes lie along
    -- x, y, z and the C3 axes along the cube diagonals [+-1, +-1, +-1]. The five #m
    -- orbitals split into e + t2 (e at -0.6 * 10Dq, t2 at +0.4 * 10Dq), the negative
    -- of the Oh cubic field. The Akm coefficients below reproduce
    -- PotentialExpandedOnClm("Td", 2, {-0.6, 0.4}) from the Quanty point-group
    -- tables (https://www.quanty.org/physics_chemistry/point_groups).
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
