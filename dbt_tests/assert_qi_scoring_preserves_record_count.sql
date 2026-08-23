with source_count as (
    select count(*) as n from {{ ref('fct_application') }}
),
scored_count as (
    select sum(k) as n from {{ ref('qi_profile') }}
)
select source_count.n as source_n, scored_count.n as scored_n
from source_count cross join scored_count
where source_count.n <> scored_count.n

