--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"1111111111 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"0000000000 1111111111", NElectrons_#f, NElectrons_#f}}

FinalRestrictions = {NFermions, NBosons, {"1111111111 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                         {"0000000000 1111111111", NElectrons_#f, NElectrons_#f}}

CalculationRestrictions = nil
