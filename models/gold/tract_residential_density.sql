with ranked as (
    select
        census_tract,
        population,
        land_area_sqmi,
        population_density_per_sqmi,
        ntile(5) over (order by population_density_per_sqmi) as residential_density_quintile
    from {{ ref('stg_census_tract_context') }}
    where population_density_per_sqmi is not null
      and population_density_per_sqmi >= 0
)
select
    census_tract,
    population,
    land_area_sqmi,
    population_density_per_sqmi,
    residential_density_quintile
from ranked
