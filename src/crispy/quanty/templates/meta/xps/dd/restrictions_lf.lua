--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"1111111111 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"0000000000 1111111111", NElectrons_#f, NElectrons_#f}}

FinalRestrictions = {NFermions, NBosons, {"1111111111 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                         {"0000000000 1111111111", NElectrons_#f, NElectrons_#f}}

CalculationRestrictions = nil

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"1111111111 0000000000 0000000000", NElectrons_#i, NElectrons_#i},
                                               {"0000000000 1111111111 0000000000", NElectrons_#f, NElectrons_#f},
                                               {"0000000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = {NFermions, NBosons, {"1111111111 0000000000 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                             {"0000000000 1111111111 0000000000", NElectrons_#f, NElectrons_#f},
                                             {"0000000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    CalculationRestrictions = {NFermions, NBosons, {"0000000000 0000000000 1111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

if MlctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"1111111111 0000000000 0000000000", NElectrons_#i, NElectrons_#i},
                                               {"0000000000 1111111111 0000000000", NElectrons_#f, NElectrons_#f},
                                               {"0000000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    FinalRestrictions = {NFermions, NBosons, {"1111111111 0000000000 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                             {"0000000000 1111111111 0000000000", NElectrons_#f, NElectrons_#f},
                                             {"0000000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    CalculationRestrictions = {NFermions, NBosons, {"0000000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2 + (NConfigurations - 1)}}
end
