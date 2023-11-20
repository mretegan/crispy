--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"1111111111 00000000000000", NElectrons_#i, NElectrons_#i},
                                           {"0000000000 11111111111111", NElectrons_#f, NElectrons_#f}}

FinalRestrictions = {NFermions, NBosons, {"1111111111 00000000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                         {"0000000000 11111111111111", NElectrons_#f, NElectrons_#f}}

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"1111111111 00000000000000 00000000000000", NElectrons_#i, NElectrons_#i},
                                               {"0000000000 11111111111111 00000000000000", NElectrons_#f, NElectrons_#f},
                                               {"0000000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {"1111111111 00000000000000 00000000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                             {"0000000000 11111111111111 00000000000000", NElectrons_#f, NElectrons_#f},
                                             {"0000000000 00000000000000 11111111111111", NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {"0000000000 00000000000000 11111111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end
