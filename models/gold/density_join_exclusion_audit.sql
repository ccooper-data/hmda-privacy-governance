with labeled as (
    select app.*,
        case when density.census_tract is null then 'dropped' else 'retained' end as join_status
    from {{ ref('fct_application') }} as app
    left join {{ ref('tract_residential_density') }} as density using (census_tract)
), dimensions as (
    select join_status, 'derived_race' as dimension, derived_race as category, count(*) as record_count
    from labeled group by 1, 2, 3
    union all
    select join_status, 'derived_ethnicity', derived_ethnicity, count(*) from labeled group by 1, 2, 3
    union all
    select join_status, 'action_taken', cast(action_taken as varchar), count(*) from labeled group by 1, 2, 3
    union all
    select join_status, 'derived_dwelling_category', derived_dwelling_category, count(*)
    from labeled group by 1, 2, 3
    union all
    select join_status, 'lei', lei, count(*) from labeled group by 1, 2, 3
)
select join_status, dimension, category, record_count
from dimensions
where record_count >= {{ var('minimum_cell_size') }}
