--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"000000 1111111111", NElectrons_#m, NElectrons_#m}}

IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                                {"000000 1111111111", NElectrons_#m + 1, NElectrons_#m + 1}}

FinalRestrictions = InitialRestrictions

CalculationRestrictions = nil
