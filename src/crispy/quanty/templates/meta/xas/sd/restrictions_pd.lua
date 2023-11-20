--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"00 1111111111", NElectrons_#f, NElectrons_#f}}

FinalRestrictions = {NFermions, NBosons, {"11 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                         {"00 1111111111", NElectrons_#f + 1, NElectrons_#f + 1}}

CalculationRestrictions = nil

if PdHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"11 0000000000 000000", NElectrons_#i, NElectrons_#i},
                                               {"00 1111111111 000000", NElectrons_#f, NElectrons_#f},
                                               {"00 0000000000 111111", NElectrons_4p, NElectrons_4p}}

    FinalRestrictions = {NFermions, NBosons, {"11 0000000000 000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                             {"00 1111111111 000000", NElectrons_#f + 1, NElectrons_#f + 1},
                                             {"00 0000000000 111111", NElectrons_4p, NElectrons_4p}}

    CalculationRestrictions = {NFermions, NBosons, {"00 0000000000 111111", NElectrons_4p, NElectrons_4p + 1}}
end
