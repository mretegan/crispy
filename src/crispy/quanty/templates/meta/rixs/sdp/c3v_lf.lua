--------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if CrystalFieldTerm then
    -- C3v crystal field for d electrons: the three-fold C3 axis is along z and a
    -- vertical mirror plane sigma_v contains the y-axis (the Koenig & Kremer
    -- convention, equivalent to the inversion-related Quanty D3d "Zy" setting). The
    -- five #m orbitals split into a1 + e + e, parametrized by Dq, Dsigma and Dtau.
    -- The two e sets (descended from the cubic t2g and eg) share an irrep and mix,
    -- so the Hamiltonian is not diagonal in the irrep basis (see Koenig & Kremer,
    -- p. 56). The Akm expansion is taken from the Quanty point-group tables
    -- (https://www.quanty.org/physics_chemistry/point_groups).
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
    io.write(string.format("e(t2g)  %8.3f\n", -4 * Dq_#m_i + Dsigma_#m_i + 2 / 3 * Dtau_#m_i))
    io.write(string.format("e(eg)   %8.3f\n", 6 * Dq_#m_i + 7 / 3 * Dtau_#m_i))
    io.write("================\n")
    io.write("For the C3v symmetry, the crystal field Hamiltonian is not necessarily diagonal in\n")
    io.write("the basis of the irreducible representations. See the König and Kremer book, page 56.\n")
    io.write(string.format("The non-diagonal element <e(t2g)|H|e(eg)> is %.3f.\n", -math.sqrt(2) / 3 * (3 * Dsigma_#m_i - 5 * Dtau_#m_i)))
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

--------------------------------------------------------------------------------
-- Define the #m-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_#m_L1_i = $Delta(#m,L1)_i_value
    E_#m_i = (10 * Delta_#m_L1_i - NElectrons_#m * (19 + NElectrons_#m) * U_#m_#m_i / 2) / (10 + NElectrons_#m)
    E_L1_i = NElectrons_#m * ((1 + NElectrons_#m) * U_#m_#m_i / 2 - Delta_#m_L1_i) / (10 + NElectrons_#m)

    Delta_#m_L1_m = $Delta(#m,L1)_m_value
    E_#m_m = (10 * Delta_#m_L1_m - NElectrons_#m * (23 + NElectrons_#m) * U_#m_#m_m / 2 - 22 * U_#i_#m_m) / (12 + NElectrons_#m)
    E_#i_m = (10 * Delta_#m_L1_m + (1 + NElectrons_#m) * (NElectrons_#m * U_#m_#m_m / 2 - (10 + NElectrons_#m) * U_#i_#m_m)) / (12 + NElectrons_#m)
    E_L1_m = ((1 + NElectrons_#m) * (NElectrons_#m * U_#m_#m_m / 2 + 2 * U_#i_#m_m) - (2 + NElectrons_#m) * Delta_#m_L1_m) / (12 + NElectrons_#m)

    Delta_#m_L1_f = $Delta(#m,L1)_f_value
    E_#m_f = (10 * Delta_#m_L1_f - NElectrons_#m * (31 + NElectrons_#m) * U_#m_#m_f / 2 - 90 * U_#f_#m_f) / (16 + NElectrons_#m)
    E_#f_f = (10 * Delta_#m_L1_f + (1 + NElectrons_#m) * (NElectrons_#m * U_#m_#m_f / 2 - (10 + NElectrons_#m) * U_#f_#m_f)) / (16 + NElectrons_#m)
    E_L1_f = ((1 + NElectrons_#m) * (NElectrons_#m * U_#m_#m_f / 2 + 6 * U_#f_#m_f) - (6 + NElectrons_#m) * Delta_#m_L1_f) / (16 + NElectrons_#m)

    H_i = H_i + Chop(
          E_#m_i * N_#m
        + E_L1_i * N_L1)

    H_m = H_m + Chop(
          E_#m_m * N_#m
        + E_#i_m * N_#i
        + E_L1_m * N_L1)

    H_f = H_f + Chop(
          E_#m_f * N_#m
        + E_#f_f * N_#f
        + E_L1_f * N_L1)

    -- The #m and ligand orbitals use the same C3v basis: a1(t2g), e(eg), and
    -- e(t2g). Each hybridization parameter couples a #m irrep only with the ligand
    -- irrep that has the same cubic parent (see Tables S7 and S8 in the supporting
    -- information of Retegan et al., Inorg. Chem. 62, 18864 (2023),
    -- https://doi.org/10.1021/acs.inorgchem.3c02158). Each Akm list is the
    -- expansion of the projector on one irrep, and the three projectors sum to
    -- the identity. The ligand crystal field uses the Akm of the #m crystal field.
    Akm = {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}}
    Dq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{2, 0, -7}}
    Dsigma_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{4, 0, -21}}
    Dtau_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{0, 0, 1 / 5}, {2, 0, 1}, {4, 0, 9 / 5}}
    Va1_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, Akm)
              + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{0, 0, 2 / 5}, {4, 0, -7 / 5}, {4, 3, -math.sqrt(70) / 5}, {4, -3, math.sqrt(70) / 5}}
    Ve_eg_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, Akm)
                + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, Akm)

    Akm = {{0, 0, 2 / 5}, {2, 0, -1}, {4, 0, -2 / 5}, {4, 3, math.sqrt(70) / 5}, {4, -3, -math.sqrt(70) / 5}}
    Ve_t2g_#m_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_#m, IndexDn_#m, Akm)
                 + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L1, IndexDn_L1, Akm)

    Dq_L1_i = $10Dq(L1)_i_value / 10.0
    Dsigma_L1_i = $Dsigma(L1)_i_value
    Dtau_L1_i = $Dtau(L1)_i_value
    Va1_#m_L1_i = $Va1(#m,L1)_i_value
    Ve_eg_#m_L1_i = $Ve(eg)(#m,L1)_i_value
    Ve_t2g_#m_L1_i = $Ve(t2g)(#m,L1)_i_value

    Dq_L1_m = $10Dq(L1)_m_value / 10.0
    Dsigma_L1_m = $Dsigma(L1)_m_value
    Dtau_L1_m = $Dtau(L1)_m_value
    Va1_#m_L1_m = $Va1(#m,L1)_m_value
    Ve_eg_#m_L1_m = $Ve(eg)(#m,L1)_m_value
    Ve_t2g_#m_L1_m = $Ve(t2g)(#m,L1)_m_value

    Dq_L1_f = $10Dq(L1)_f_value / 10.0
    Dsigma_L1_f = $Dsigma(L1)_f_value
    Dtau_L1_f = $Dtau(L1)_f_value
    Va1_#m_L1_f = $Va1(#m,L1)_f_value
    Ve_eg_#m_L1_f = $Ve(eg)(#m,L1)_f_value
    Ve_t2g_#m_L1_f = $Ve(t2g)(#m,L1)_f_value

    H_i = H_i + Chop(
          Dq_L1_i * Dq_L1
        + Dsigma_L1_i * Dsigma_L1
        + Dtau_L1_i * Dtau_L1
        + Va1_#m_L1_i * Va1_#m_L1
        + Ve_eg_#m_L1_i * Ve_eg_#m_L1
        + Ve_t2g_#m_L1_i * Ve_t2g_#m_L1)

    H_m = H_m + Chop(
          Dq_L1_m * Dq_L1
        + Dsigma_L1_m * Dsigma_L1
        + Dtau_L1_m * Dtau_L1
        + Va1_#m_L1_m * Va1_#m_L1
        + Ve_eg_#m_L1_m * Ve_eg_#m_L1
        + Ve_t2g_#m_L1_m * Ve_t2g_#m_L1)

    H_f = H_f + Chop(
          Dq_L1_f * Dq_L1
        + Dsigma_L1_f * Dsigma_L1
        + Dtau_L1_f * Dtau_L1
        + Va1_#m_L1_f * Va1_#m_L1
        + Ve_eg_#m_L1_f * Ve_eg_#m_L1
        + Ve_t2g_#m_L1_f * Ve_t2g_#m_L1)
end

--------------------------------------------------------------------------------
-- Define the #m-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if MlctLigandsHybridizationTerm then
    N_L2 = NewOperator("Number", NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_#m_L2_i = $Delta(#m,L2)_i_value
    E_#m_i = U_#m_#m_i * (-NElectrons_#m + 1) / 2
    E_L2_i = Delta_#m_L2_i + U_#m_#m_i * NElectrons_#m / 2 - U_#m_#m_i / 2

    Delta_#m_L2_m = $Delta(#m,L2)_m_value
    E_#m_m = -(U_#m_#m_m * NElectrons_#m^2 + 3 * U_#m_#m_m * NElectrons_#m + 4 * U_#i_#m_m) / (2 * NElectrons_#m + 4)
    E_#i_m = NElectrons_#m * (U_#m_#m_m * NElectrons_#m + U_#m_#m_m - 2 * U_#i_#m_m * NElectrons_#m - 2 * U_#i_#m_m) / (2 * (NElectrons_#m + 2))
    E_L2_m = (2 * Delta_#m_L2_m * NElectrons_#m + 4 * Delta_#m_L2_m + U_#m_#m_m * NElectrons_#m^2 - U_#m_#m_m * NElectrons_#m - 4 * U_#m_#m_m + 4 * U_#i_#m_m * NElectrons_#m + 4 * U_#i_#m_m) / (2 * (NElectrons_#m + 2))

    Delta_#m_L2_f = $Delta(#m,L2)_f_value
    E_#m_f = -(U_#m_#m_f * NElectrons_#m^2 + 11 * U_#m_#m_f * NElectrons_#m + 60 * U_#f_#m_f) / (2 * NElectrons_#m + 12)
    E_#f_f = NElectrons_#m * (U_#m_#m_f * NElectrons_#m + U_#m_#m_f - 2 * U_#f_#m_f * NElectrons_#m - 2 * U_#f_#m_f) / (2 * (NElectrons_#m + 6))
    E_L2_f = (2 * Delta_#m_L2_f * NElectrons_#m + 12 * Delta_#m_L2_f + U_#m_#m_f * NElectrons_#m^2 - U_#m_#m_f * NElectrons_#m - 12 * U_#m_#m_f + 12 * U_#f_#m_f * NElectrons_#m + 12 * U_#f_#m_f) / (2 * (NElectrons_#m + 6))

    H_i = H_i + Chop(
          E_#m_i * N_#m
        + E_L2_i * N_L2)

    H_m = H_m + Chop(
          E_#m_m * N_#m
        + E_#i_m * N_#i
        + E_L2_m * N_L2)

    H_f = H_f + Chop(
          E_#m_f * N_#m
        + E_#f_f * N_#f  
        + E_L2_f * N_L2)

    -- The #m and ligand orbitals use the same C3v basis: a1(t2g), e(eg), and
    -- e(t2g). Each hybridization parameter couples a #m irrep only with the ligand
    -- irrep that has the same cubic parent (see Tables S7 and S8 in the supporting
    -- information of Retegan et al., Inorg. Chem. 62, 18864 (2023),
    -- https://doi.org/10.1021/acs.inorgchem.3c02158). Each Akm list is the
    -- expansion of the projector on one irrep, and the three projectors sum to
    -- the identity. The ligand crystal field uses the Akm of the #m crystal field.
    Akm = {{4, 0, -14}, {4, 3, -2 * math.sqrt(70)}, {4, -3, 2 * math.sqrt(70)}}
    Dq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{2, 0, -7}}
    Dsigma_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{4, 0, -21}}
    Dtau_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{0, 0, 1 / 5}, {2, 0, 1}, {4, 0, 9 / 5}}
    Va1_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, Akm)
              + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{0, 0, 2 / 5}, {4, 0, -7 / 5}, {4, 3, -math.sqrt(70) / 5}, {4, -3, math.sqrt(70) / 5}}
    Ve_eg_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, Akm)
                + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, Akm)

    Akm = {{0, 0, 2 / 5}, {2, 0, -1}, {4, 0, -2 / 5}, {4, 3, math.sqrt(70) / 5}, {4, -3, -math.sqrt(70) / 5}}
    Ve_t2g_#m_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_#m, IndexDn_#m, Akm)
                 + NewOperator("CF", NFermions, IndexUp_#m, IndexDn_#m, IndexUp_L2, IndexDn_L2, Akm)

    Dq_L2_i = $10Dq(L2)_i_value / 10.0
    Dsigma_L2_i = $Dsigma(L2)_i_value
    Dtau_L2_i = $Dtau(L2)_i_value
    Va1_#m_L2_i = $Va1(#m,L2)_i_value
    Ve_eg_#m_L2_i = $Ve(eg)(#m,L2)_i_value
    Ve_t2g_#m_L2_i = $Ve(t2g)(#m,L2)_i_value

    Dq_L2_m = $10Dq(L2)_m_value / 10.0
    Dsigma_L2_m = $Dsigma(L2)_m_value
    Dtau_L2_m = $Dtau(L2)_m_value
    Va1_#m_L2_m = $Va1(#m,L2)_m_value
    Ve_eg_#m_L2_m = $Ve(eg)(#m,L2)_m_value
    Ve_t2g_#m_L2_m = $Ve(t2g)(#m,L2)_m_value

    Dq_L2_f = $10Dq(L2)_f_value / 10.0
    Dsigma_L2_f = $Dsigma(L2)_f_value
    Dtau_L2_f = $Dtau(L2)_f_value
    Va1_#m_L2_f = $Va1(#m,L2)_f_value
    Ve_eg_#m_L2_f = $Ve(eg)(#m,L2)_f_value
    Ve_t2g_#m_L2_f = $Ve(t2g)(#m,L2)_f_value

    H_i = H_i + Chop(
          Dq_L2_i * Dq_L2
        + Dsigma_L2_i * Dsigma_L2
        + Dtau_L2_i * Dtau_L2
        + Va1_#m_L2_i * Va1_#m_L2
        + Ve_eg_#m_L2_i * Ve_eg_#m_L2
        + Ve_t2g_#m_L2_i * Ve_t2g_#m_L2)

    H_m = H_m + Chop(
          Dq_L2_m * Dq_L2
        + Dsigma_L2_m * Dsigma_L2
        + Dtau_L2_m * Dtau_L2
        + Va1_#m_L2_m * Va1_#m_L2
        + Ve_eg_#m_L2_m * Ve_eg_#m_L2
        + Ve_t2g_#m_L2_m * Ve_t2g_#m_L2)

    H_f = H_f + Chop(
          Dq_L2_f * Dq_L2
        + Dsigma_L2_f * Dsigma_L2
        + Dtau_L2_f * Dtau_L2
        + Va1_#m_L2_f * Va1_#m_L2
        + Ve_eg_#m_L2_f * Ve_eg_#m_L2
        + Ve_t2g_#m_L2_f * Ve_t2g_#m_L2)
end
