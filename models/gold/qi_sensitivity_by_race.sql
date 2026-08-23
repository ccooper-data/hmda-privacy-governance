with tiered as (
    select
        'demographic_geo' as qi_tier,
        derived_race,
        derived_ethnicity,
        k
    from {{ ref('qi_profile_demographic_geo') }}

    union all

    select
        'financial_context' as qi_tier,
        derived_race,
        derived_ethnicity,
        k
    from {{ ref('qi_profile_financial_context') }}

    union all

    select
        'institution_aware' as qi_tier,
        derived_race,
        derived_ethnicity,
        k
    from {{ ref('qi_profile') }}
)

select
    qi_tier,
    derived_race,
    derived_ethnicity,
    cast(sum(k) as bigint) as record_count,
    sum(case when k = 1 then k else 0 end) * 1.0 / sum(k) as sample_uniqueness_rate,
    sum(case when k < 5 then k else 0 end) * 1.0 / sum(k) as share_records_k_lt_5,
    count(*) * 1.0 / sum(k) as prosecutor_expected_match_risk
from tiered
group by qi_tier, derived_race, derived_ethnicity
having sum(k) >= 20

