select
    cast(census_tract as varchar) as census_tract,
    try_cast(population as bigint) as population,
    try_cast(land_area_sqmi as double) as land_area_sqmi,
    try_cast(population_density_per_sqmi as double) as population_density_per_sqmi
from read_csv_auto('{{ var("census_tract_context_path") }}', header = true, all_varchar = true)
