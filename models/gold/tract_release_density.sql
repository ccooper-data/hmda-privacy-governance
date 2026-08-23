select
    census_tract,
    count(*) as application_count,
    ntile(5) over (order by count(*)) as release_density_quintile
from {{ ref('fct_application') }}
where census_tract is not null
group by census_tract

