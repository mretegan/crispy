--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------
InitialRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_#i, NElectrons_#i},
                                           {"000000 1111111111", NElectrons_#m, NElectrons_#m}}

IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                                {"000000 1111111111", NElectrons_#m + 1, NElectrons_#m + 1}}

FinalRestrictions = InitialRestrictions

CalculationRestrictions = nil

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_#i, NElectrons_#i},
                                               {"000000 1111111111 0000000000", NElectrons_#f, NElectrons_#f},
                                               {"000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                                    {"000000 1111111111 0000000000", NElectrons_#f + 1, NElectrons_#f + 1},
                                                    {"000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}

    FinalRestrictions = InitialRestrictions

    CalculationRestrictions = {NFermions, NBosons, {"000000 0000000000 1111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}
end

if MlctLigandsHybridizationTerm then
    InitialRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_#i, NElectrons_#i},
                                               {"000000 1111111111 0000000000", NElectrons_#f, NElectrons_#f},
                                               {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    IntermediateRestrictions = {NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_#i - 1, NElectrons_#i - 1},
                                                    {"000000 1111111111 0000000000", NElectrons_#f + 1, NElectrons_#f + 1},
                                                    {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}

    FinalRestrictions = InitialRestrictions

    CalculationRestrictions = {NFermions, NBosons, {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2 + (NConfigurations - 1)}}
end
