--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    Dq_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}})
    Dsigma_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, {{2, 0, -7}})
    Dtau_3d = NewOperator('CF', NFermions, IndexUp_3d, IndexDn_3d, {{4, 0, -21}})

    Dq_3d_i = $Dq(#f)_i_value
    Dsigma_3d_i = $Dsigma(#f)_i_value
    Dtau_3d_i = $Dtau(#f)_i_value

    io.write('Energies of the 3d orbitals in the initial Hamiltonian (crystal field term only):\n')
    io.write('================\n')
    io.write('Irrep.         E\n')
    io.write('================\n')
    io.write(string.format('a1(t2g) %8.3f\n', -4 * Dq_3d_i - 2 * Dsigma_3d_i - 6 * Dtau_3d_i))
    io.write(string.format('e(eg)   %8.3f\n', 6 * Dq_3d_i + 7 / 3 * Dtau_3d_i))
    io.write(string.format('e(t2g)  %8.3f\n', -4 * Dq_3d_i + Dsigma_3d_i + 2 / 3 * Dtau_3d_i))
    io.write('================\n')
    io.write('\n')

    Dq_3d_f = $Dq(#f)_f_value
    Dsigma_3d_f = $Dsigma(#f)_f_value
    Dtau_3d_f = $Dtau(#f)_f_value

    H_i = H_i + Chop(
          Dq_3d_i * Dq_3d
        + Dsigma_3d_i * Dsigma_3d
        + Dtau_3d_i * Dtau_3d)

    H_f = H_f + Chop(
          Dq_3d_f * Dq_3d
        + Dsigma_3d_f * Dsigma_3d
        + Dtau_3d_f * Dtau_3d)
end