--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"00 1111111111", NElectrons_#f, NElectrons_#f}}

FinalRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                         {"00 1111111111", NElectrons_#f + 1, NElectrons_#f + 1}}

CalculationRestrictions = nil
