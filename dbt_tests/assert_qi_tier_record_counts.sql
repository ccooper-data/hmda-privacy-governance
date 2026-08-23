with source as (
    select count(*) as n from {{ ref('fct_application') }}
),
tier_counts as (
    select 'demographic_geo' as qi_tier, sum(k) as n
    from {{ ref('qi_profile_demographic_geo') }}
    union all
    select 'financial_context' as qi_tier, sum(k) as n
    from {{ ref('qi_profile_financial_context') }}
    union all
    select 'institution_aware' as qi_tier, sum(k) as n
    from {{ ref('qi_profile') }}
)
select tier_counts.qi_tier, source.n as source_n, tier_counts.n as tier_n
from source cross join tier_counts
where source.n <> tier_counts.n

