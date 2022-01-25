--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_#f = NewOperator("Sx", NFermions, IndexUp_#f, IndexDn_#f)
Sy_#f = NewOperator("Sy", NFermions, IndexUp_#f, IndexDn_#f)
Sz_#f = NewOperator("Sz", NFermions, IndexUp_#f, IndexDn_#f)
Ssqr_#f = NewOperator("Ssqr", NFermions, IndexUp_#f, IndexDn_#f)
Splus_#f = NewOperator("Splus", NFermions, IndexUp_#f, IndexDn_#f)
Smin_#f = NewOperator("Smin", NFermions, IndexUp_#f, IndexDn_#f)

Lx_#f = NewOperator("Lx", NFermions, IndexUp_#f, IndexDn_#f)
Ly_#f = NewOperator("Ly", NFermions, IndexUp_#f, IndexDn_#f)
Lz_#f = NewOperator("Lz", NFermions, IndexUp_#f, IndexDn_#f)
Lsqr_#f = NewOperator("Lsqr", NFermions, IndexUp_#f, IndexDn_#f)
Lplus_#f = NewOperator("Lplus", NFermions, IndexUp_#f, IndexDn_#f)
Lmin_#f = NewOperator("Lmin", NFermions, IndexUp_#f, IndexDn_#f)

Jx_#f = NewOperator("Jx", NFermions, IndexUp_#f, IndexDn_#f)
Jy_#f = NewOperator("Jy", NFermions, IndexUp_#f, IndexDn_#f)
Jz_#f = NewOperator("Jz", NFermions, IndexUp_#f, IndexDn_#f)
Jsqr_#f = NewOperator("Jsqr", NFermions, IndexUp_#f, IndexDn_#f)
Jplus_#f = NewOperator("Jplus", NFermions, IndexUp_#f, IndexDn_#f)
Jmin_#f = NewOperator("Jmin", NFermions, IndexUp_#f, IndexDn_#f)

Tx_#f = NewOperator("Tx", NFermions, IndexUp_#f, IndexDn_#f)
Ty_#f = NewOperator("Ty", NFermions, IndexUp_#f, IndexDn_#f)
Tz_#f = NewOperator("Tz", NFermions, IndexUp_#f, IndexDn_#f)

Sx = Sx_#f
Sy = Sy_#f
Sz = Sz_#f

Lx = Lx_#f
Ly = Ly_#f
Lz = Lz_#f

Jx = Jx_#f
Jy = Jy_#f
Jz = Jz_#f

Tx = Tx_#f
Ty = Ty_#f
Tz = Tz_#f

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if MagneticFieldTerm then
    -- The values are in eV, and not Tesla. To convert from Tesla to eV multiply
    -- the value with EnergyUnits.Tesla.value.
    Bx_i = $Bx_i_value
    By_i = $By_i_value
    Bz_i = $Bz_i_value

    Bx_f = $Bx_f_value
    By_f = $By_f_value
    Bz_f = $Bz_f_value

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if ExchangeFieldTerm then
    Hx_i = $Hx_i_value
    Hy_i = $Hy_i_value
    Hz_i = $Hz_i_value

    Hx_f = $Hx_f_value
    Hy_f = $Hy_f_value
    Hz_f = $Hz_f_value

    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end
