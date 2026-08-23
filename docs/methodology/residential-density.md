# Residential-density risk concentration

This analysis tests whether disclosure risk concentrates in low-density Census tracts. It uses
only aggregate geography context: 2023 ACS five-year total population (`B01003_001E`) and 2023
Census Gazetteer tract land area. Residential density is total population divided by land square
miles. Texas tracts are ranked into five equal-count tract groups; quintile 1 is lowest density.

HMDA applications are joined to tract context by the 11-digit Census GEOID. Equivalence-class
sizes are computed on the complete state-year HMDA release using the demographic/geographic QI
tier before any race or ethnicity cohort is reported. Published cells contain at least 20 HMDA
records. No address, resident record, person-level Census data, or linkage target is obtained.

ACS population is an estimate and tract land area is created for statistical purposes. Density
quintiles describe residential context, not an official rural/urban classification. The analysis
must report join coverage and should not generalize unmatched tracts.
