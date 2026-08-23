with risk as (
    select
        configuration,
        cast(sum(k) as bigint) as record_count,
        sum(case when k = 1 then k else 0 end) * 1.0 / sum(k) as sample_uniqueness_rate,
        count(*) * 1.0 / sum(k) as prosecutor_expected_match_risk,
        sum(case when k >= 5 then k else 0 end) * 1.0 / sum(k) as retained_share_k5
    from {{ ref('protection_equivalence_classes') }}
    group by configuration
),
cohort_n as (
    select
        configuration,
        sum(case when derived_race = 'White' and derived_ethnicity = 'Not Hispanic or Latino'
                 and k >= 5 then k else 0 end) as reference_n_k5,
        sum(case when derived_race = 'Black or African American'
                 and derived_ethnicity = 'Not Hispanic or Latino'
                 and k >= 5 then k else 0 end) as comparison_n_k5
    from {{ ref('protection_equivalence_classes') }}
    group by configuration
),
baseline as (
    select avg(cast(is_denied as integer)) as reference_denial_rate
    from {{ ref('fct_application') }}
    where derived_race = 'White' and derived_ethnicity = 'Not Hispanic or Latino'
)
select
    risk.configuration,
    risk.configuration = 'cfpb_current' as is_current_baseline,
    risk.record_count,
    risk.sample_uniqueness_rate,
    risk.prosecutor_expected_match_risk,
    risk.retained_share_k5,
    cohort_n.reference_n_k5,
    cohort_n.comparison_n_k5,
    baseline.reference_denial_rate,
    100 * 2.801585 * sqrt(
        baseline.reference_denial_rate * (1 - baseline.reference_denial_rate)
        * (1.0 / nullif(cohort_n.reference_n_k5, 0)
           + 1.0 / nullif(cohort_n.comparison_n_k5, 0))
    ) as minimum_detectable_disparity_points_k5
from risk
inner join cohort_n using (configuration)
cross join baseline

