--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"111111 00000000000000", NElectrons_#i, NElectrons_#i},
                                           {"000000 11111111111111", NElectrons_#f, NElectrons_#f}}

FinalRestrictions = {NFermions, NBosons, {"111111 00000000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                         {"000000 11111111111111", NElectrons_#f + 1, NElectrons_#f + 1}}

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"111111 00000000000000 00000000000000", NElectrons_#i, NElectrons_#i},
                                               {"000000 11111111111111 00000000000000", NElectrons_#f, NElectrons_#f},
                                               {"000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {"111111 00000000000000 00000000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                             {"000000 11111111111111 00000000000000", NElectrons_#f + 1, NElectrons_#f + 1},
                                             {"000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {"000000 00000000000000 11111111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end
