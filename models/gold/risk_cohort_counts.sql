select
    activity_year,
    derived_race,
    derived_ethnicity,
    count(*) as record_count,
    avg(cast(is_denied as integer)) as denial_rate
from {{ ref('fct_application') }}
group by 1, 2, 3
having count(*) >= {{ var('minimum_cell_size') }}
