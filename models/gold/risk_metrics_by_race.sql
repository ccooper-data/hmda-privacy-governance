with scored as (
    select
        applications.derived_race,
        applications.derived_ethnicity,
        profile.k
    from {{ ref('fct_application') }} as applications
    inner join {{ ref('qi_profile') }} as profile
        on applications.census_tract is not distinct from profile.census_tract
        and applications.applicant_age is not distinct from profile.applicant_age
        and applications.applicant_sex is not distinct from profile.applicant_sex
        and applications.derived_race is not distinct from profile.derived_race
        and applications.derived_ethnicity is not distinct from profile.derived_ethnicity
        and applications.income is not distinct from profile.income
        and applications.loan_amount is not distinct from profile.loan_amount
        and applications.loan_purpose is not distinct from profile.loan_purpose
        and applications.occupancy_type is not distinct from profile.occupancy_type
        and applications.lien_status is not distinct from profile.lien_status
        and applications.derived_dwelling_category is not distinct from profile.derived_dwelling_category
        and applications.lei is not distinct from profile.lei
)

select
    'full_state_year' as equivalence_universe,
    derived_race,
    derived_ethnicity,
    count(*) as record_count,
    avg(cast(k = 1 as integer)) as sample_uniqueness_rate,
    avg(cast(k < 5 as integer)) as share_records_k_lt_5,
    avg(cast(k < 10 as integer)) as share_records_k_lt_10,
    avg(1.0 / k) as prosecutor_expected_match_risk
from scored
group by derived_race, derived_ethnicity
having count(*) >= {{ var('minimum_cell_size') }}
