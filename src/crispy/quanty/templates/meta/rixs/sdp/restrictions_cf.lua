--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"11 000000 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"00 111111 0000000000", NElectrons_#f, NElectrons_#f},
                                           {"00 000000 1111111111", NElectrons_#m, NElectrons_#m}}

IntermediateRestrictions = {NFermions, NBosons, {"11 000000 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                                {"00 111111 0000000000", NElectrons_#f, NElectrons_#f},
                                                {"00 000000 1111111111", NElectrons_#m + 1, NElectrons_#m + 1}}

FinalRestrictions = {NFermions, NBosons, {"11 000000 0000000000", NElectrons_#i, NElectrons_#i},
                                         {"00 111111 0000000000", NElectrons_#f - 1, NElectrons_#f - 1},
                                         {"00 000000 1111111111", NElectrons_#m + 1, NElectrons_#m + 1}}

CalculationRestrictions = nil
