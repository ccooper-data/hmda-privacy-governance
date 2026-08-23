# HMDA Release-Density Concentration

This analysis ranks census tracts into quintiles by the number of HMDA application records in the released state-year file. Quintile 1 has the lowest application volume and quintile 5 the highest.

This is **release density**, not residential population density, rurality, or physical population per square mile. It directly tests whether sparse representation in the released mortgage dataset is associated with greater demographic/geographic uniqueness. A later ACS/TIGER enrichment is required before making claims about residential population density or rural communities.

Risk is calculated from the `demographic_geo` QI tier, then aggregated by density quintile, race, and ethnicity. Cells below 20 records are suppressed.

