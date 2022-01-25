--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_#m = NewOperator("Sx", NFermions, IndexUp_#m, IndexDn_#m)
Sy_#m = NewOperator("Sy", NFermions, IndexUp_#m, IndexDn_#m)
Sz_#m = NewOperator("Sz", NFermions, IndexUp_#m, IndexDn_#m)
Ssqr_#m = NewOperator("Ssqr", NFermions, IndexUp_#m, IndexDn_#m)
Splus_#m = NewOperator("Splus", NFermions, IndexUp_#m, IndexDn_#m)
Smin_#m = NewOperator("Smin", NFermions, IndexUp_#m, IndexDn_#m)

Lx_#m = NewOperator("Lx", NFermions, IndexUp_#m, IndexDn_#m)
Ly_#m = NewOperator("Ly", NFermions, IndexUp_#m, IndexDn_#m)
Lz_#m = NewOperator("Lz", NFermions, IndexUp_#m, IndexDn_#m)
Lsqr_#m = NewOperator("Lsqr", NFermions, IndexUp_#m, IndexDn_#m)
Lplus_#m = NewOperator("Lplus", NFermions, IndexUp_#m, IndexDn_#m)
Lmin_#m = NewOperator("Lmin", NFermions, IndexUp_#m, IndexDn_#m)

Jx_#m = NewOperator("Jx", NFermions, IndexUp_#m, IndexDn_#m)
Jy_#m = NewOperator("Jy", NFermions, IndexUp_#m, IndexDn_#m)
Jz_#m = NewOperator("Jz", NFermions, IndexUp_#m, IndexDn_#m)
Jsqr_#m = NewOperator("Jsqr", NFermions, IndexUp_#m, IndexDn_#m)
Jplus_#m = NewOperator("Jplus", NFermions, IndexUp_#m, IndexDn_#m)
Jmin_#m = NewOperator("Jmin", NFermions, IndexUp_#m, IndexDn_#m)

Tx_#m = NewOperator("Tx", NFermions, IndexUp_#m, IndexDn_#m)
Ty_#m = NewOperator("Ty", NFermions, IndexUp_#m, IndexDn_#m)
Tz_#m = NewOperator("Tz", NFermions, IndexUp_#m, IndexDn_#m)

Sx = Sx_#m
Sy = Sy_#m
Sz = Sz_#m

Lx = Lx_#m
Ly = Ly_#m
Lz = Lz_#m

Jx = Jx_#m
Jy = Jy_#m
Jz = Jz_#m

Tx = Tx_#m
Ty = Ty_#m
Tz = Tz_#m

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if MagneticFieldTerm then
    -- The values are in eV, and not Tesla. To convert from Tesla to eV multiply
    -- the value with EnergyUnits.Tesla.value.
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_m = $Bx_m_value
    By_m = $By_m_value
    Bz_m = $Bz_m_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_m = H_m + Chop(
          Bx_m * (2 * Sx + Lx)
        + By_m * (2 * Sy + Ly)
        + Bz_m * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if ExchangeFieldTerm then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_m = $Hx_m_value
    Hy_m = $Hy_m_value
    Hz_m = $Hz_m_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_m = H_m + Chop(
          Hx_m * Sx
        + Hy_m * Sy
        + Hz_m * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end
