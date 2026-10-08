--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- C3v crystal field for d electrons: the three-fold C3 axis is along z and a
    -- vertical mirror plane sigma_v contains the y-axis (the Koenig & Kremer
    -- convention, equivalent to the inversion-related Quanty D3d "Zy" setting). The
    -- five #f orbitals split into a1 + e + e, parametrized by Dq, Dsigma and Dtau.
    -- The two e sets (descended from the cubic t2g and eg) share an irrep and mix,
    -- so the Hamiltonian is not diagonal in the irrep basis (see Koenig & Kremer,
    -- p. 56). The Akm expansion is taken from the Quanty point-group tables
    -- (https://www.quanty.org/physics_chemistry/point_groups).
    Akm = {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}}
    Dq_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{2, 0, -7}}
    Dsigma_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)

    Akm = {{4, 0, -21}}
    Dtau_#f = NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, Akm)


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
    io.write(string.format("The non-diagonal element <e(t2g)|H|e(eg)> is %.3f.\n", -math.sqrt(2) / 3 * (3 * Dsigma_#f_i - 5 * Dtau_#f_i)))
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
-- Define the #f-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_#f_L1_i = $Delta(#f,L1)_i_value
    E_#f_i = (10 * Delta_#f_L1_i - NElectrons_#f * (19 + NElectrons_#f) * U_#f_#f_i / 2) / (10 + NElectrons_#f)
    E_L1_i = NElectrons_#f * ((1 + NElectrons_#f) * U_#f_#f_i / 2 - Delta_#f_L1_i) / (10 + NElectrons_#f)

    Delta_#f_L1_f = $Delta(#f,L1)_f_value
    E_#f_f = (10 * Delta_#f_L1_f - NElectrons_#f * (23 + NElectrons_#f) * U_#f_#f_f / 2 - 22 * U_#i_#f_f) / (12 + NElectrons_#f)
    E_#i_f = (10 * Delta_#f_L1_f + (1 + NElectrons_#f) * (NElectrons_#f * U_#f_#f_f / 2 - (10 + NElectrons_#f) * U_#i_#f_f)) / (12 + NElectrons_#f)
    E_L1_f = (-2 * Delta_#f_L1_f * NElectrons_#f - 4 * Delta_#f_L1_f + U_#f_#f_f * NElectrons_#f^2 + U_#f_#f_f * NElectrons_#f + 4 * U_#i_#f_f * NElectrons_#f + 4 * U_#i_#f_f) / (2 * (NElectrons_#f + 12))

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L1_i * N_L1)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
        + E_L1_f * N_L1)

    -- The #f and ligand orbitals use the same C3v basis: a1(t2g), e(eg), and
    -- e(t2g). Each hybridization parameter couples a #f irrep only with the ligand
    -- irrep that has the same cubic parent (see Tables S7 and S8 in the supporting
    -- information of Retegan et al., Inorg. Chem. 62, 18864 (2023),
    -- https://doi.org/10.1021/acs.inorgchem.3c02158). Each Akm list is the
    -- expansion of the projector on one irrep, and the three projectors sum to
    -- the identity. The ligand crystal field uses the Akm of the #f crystal field.
    Akm = {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}}
    Dq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{2, 0, -7}}
    Dsigma_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{4, 0, -21}}
    Dtau_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{0, 0, 1 / 5}, {2, 0, 1}, {4, 0, 9 / 5}}
    Va1_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, Akm)
              + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{0, 0, 2 / 5}, {4, 0, -7 / 5}, {4, 3, -math.sqrt(70) / 5}, {4, -3, math.sqrt(70) / 5}}
    Ve_eg_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, Akm)
                + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{0, 0, 2 / 5}, {2, 0, -1}, {4, 0, -2 / 5}, {4, 3, math.sqrt(70) / 5}, {4, -3, -math.sqrt(70) / 5}}
    Ve_t2g_#f_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#f, IndexDn_#f, Akm)
                 + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L1, IndexDn_L1, Akm)

    Dq_L1_i = $10Dq(L1)_i_value / 10.0
    Dsigma_L1_i = $Dsigma(L1)_i_value
    Dtau_L1_i = $Dtau(L1)_i_value
    Va1_#f_L1_i = $Va1(#f,L1)_i_value
    Ve_eg_#f_L1_i = $Ve(eg)(#f,L1)_i_value
    Ve_t2g_#f_L1_i = $Ve(t2g)(#f,L1)_i_value

    Dq_L1_f = $10Dq(L1)_f_value / 10.0
    Dsigma_L1_f = $Dsigma(L1)_f_value
    Dtau_L1_f = $Dtau(L1)_f_value
    Va1_#f_L1_f = $Va1(#f,L1)_f_value
    Ve_eg_#f_L1_f = $Ve(eg)(#f,L1)_f_value
    Ve_t2g_#f_L1_f = $Ve(t2g)(#f,L1)_f_value

    H_i = H_i + Chop(
          Dq_L1_i * Dq_L1
        + Dsigma_L1_i * Dsigma_L1
        + Dtau_L1_i * Dtau_L1
        + Va1_#f_L1_i * Va1_#f_L1
        + Ve_eg_#f_L1_i * Ve_eg_#f_L1
        + Ve_t2g_#f_L1_i * Ve_t2g_#f_L1)

    H_f = H_f + Chop(
          Dq_L1_f * Dq_L1
        + Dsigma_L1_f * Dsigma_L1
        + Dtau_L1_f * Dtau_L1
        + Va1_#f_L1_f * Va1_#f_L1
        + Ve_eg_#f_L1_f * Ve_eg_#f_L1
        + Ve_t2g_#f_L1_f * Ve_t2g_#f_L1)
end

--------------------------------------------------------------------------------
-- Define the #f-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if MlctLigandsHybridizationTerm then
    N_L2 = NewOperator("Number", NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_#f_L2_i = $Delta(#f,L2)_i_value
    E_#f_i = U_#f_#f_i * (-NElectrons_#f + 1) / 2
    E_L2_i = Delta_#f_L2_i + U_#f_#f_i * NElectrons_#f / 2 - U_#f_#f_i / 2

    Delta_#f_L2_f = $Delta(#f,L2)_f_value
    E_#f_f = -(U_#f_#f_f * NElectrons_#f^2 + 3 * U_#f_#f_f * NElectrons_#f + 4 * U_#i_#f_f) / (2 * NElectrons_#f + 4)
    E_#i_f = NElectrons_#f * (U_#f_#f_f * NElectrons_#f + U_#f_#f_f - 2 * U_#i_#f_f * NElectrons_#f - 2 * U_#i_#f_f) / (2 * (NElectrons_#f + 2))
    E_L2_f = (2 * Delta_#f_L2_f * NElectrons_#f + 4 * Delta_#f_L2_f + U_#f_#f_f * NElectrons_#f^2 - U_#f_#f_f * NElectrons_#f - 4 * U_#f_#f_f + 4 * U_#i_#f_f * NElectrons_#f + 4 * U_#i_#f_f) / (2 * (NElectrons_#f + 2))

    H_i = H_i + Chop(
          E_#f_i * N_#f
        + E_L2_i * N_L2)

    H_f = H_f + Chop(
          E_#f_f * N_#f
        + E_#i_f * N_#i
        + E_L2_f * N_L2)

    -- The #f and ligand orbitals use the same C3v basis: a1(t2g), e(eg), and
    -- e(t2g). Each hybridization parameter couples a #f irrep only with the ligand
    -- irrep that has the same cubic parent (see Tables S7 and S8 in the supporting
    -- information of Retegan et al., Inorg. Chem. 62, 18864 (2023),
    -- https://doi.org/10.1021/acs.inorgchem.3c02158). Each Akm list is the
    -- expansion of the projector on one irrep, and the three projectors sum to
    -- the identity. The ligand crystal field uses the Akm of the #f crystal field.
    Akm = {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}}
    Dq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{2, 0, -7}}
    Dsigma_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{4, 0, -21}}
    Dtau_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{0, 0, 1 / 5}, {2, 0, 1}, {4, 0, 9 / 5}}
    Va1_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, Akm)
              + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{0, 0, 2 / 5}, {4, 0, -7 / 5}, {4, 3, -math.sqrt(70) / 5}, {4, -3, math.sqrt(70) / 5}}
    Ve_eg_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, Akm)
                + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{0, 0, 2 / 5}, {2, 0, -1}, {4, 0, -2 / 5}, {4, 3, math.sqrt(70) / 5}, {4, -3, -math.sqrt(70) / 5}}
    Ve_t2g_#f_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#f, IndexDn_#f, Akm)
                 + NewOperator("CF", NFermions, IndexUp_#f, IndexDn_#f, IndexUp_L2, IndexDn_L2, Akm)

    Dq_L2_i = $10Dq(L2)_i_value / 10.0
    Dsigma_L2_i = $Dsigma(L2)_i_value
    Dtau_L2_i = $Dtau(L2)_i_value
    Va1_#f_L2_i = $Va1(#f,L2)_i_value
    Ve_eg_#f_L2_i = $Ve(eg)(#f,L2)_i_value
    Ve_t2g_#f_L2_i = $Ve(t2g)(#f,L2)_i_value

    Dq_L2_f = $10Dq(L2)_f_value / 10.0
    Dsigma_L2_f = $Dsigma(L2)_f_value
    Dtau_L2_f = $Dtau(L2)_f_value
    Va1_#f_L2_f = $Va1(#f,L2)_f_value
    Ve_eg_#f_L2_f = $Ve(eg)(#f,L2)_f_value
    Ve_t2g_#f_L2_f = $Ve(t2g)(#f,L2)_f_value

    H_i = H_i + Chop(
          Dq_L2_i * Dq_L2
        + Dsigma_L2_i * Dsigma_L2
        + Dtau_L2_i * Dtau_L2
        + Va1_#f_L2_i * Va1_#f_L2
        + Ve_eg_#f_L2_i * Ve_eg_#f_L2
        + Ve_t2g_#f_L2_i * Ve_t2g_#f_L2)

    H_f = H_f + Chop(
          Dq_L2_f * Dq_L2
        + Dsigma_L2_f * Dsigma_L2
        + Dtau_L2_f * Dtau_L2
        + Va1_#f_L2_f * Va1_#f_L2
        + Ve_eg_#f_L2_f * Ve_eg_#f_L2
        + Ve_t2g_#f_L2_f * Ve_t2g_#f_L2)
end
