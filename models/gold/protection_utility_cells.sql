with configured as (
    select 'cfpb_current' as configuration, *, census_tract as protected_geography,
        income as protected_income, loan_amount as protected_loan_amount
    from {{ ref('fct_application') }}
    union all
    select 'county_geo', *, substr(census_tract, 1, 5), income, loan_amount
    from {{ ref('fct_application') }}
    union all
    select 'county_banded', *, substr(census_tract, 1, 5),
        case when income is null then null else floor(income / {{ var('county_income_band_width') }}) * {{ var('county_income_band_width') }} end,
        case when loan_amount is null then null else floor(loan_amount / {{ var('county_loan_amount_band_width') }}) * {{ var('county_loan_amount_band_width') }} end
    from {{ ref('fct_application') }}
    union all
    select 'state_banded', *, substr(census_tract, 1, 2),
        case when income is null then null else floor(income / {{ var('state_income_band_width') }}) * {{ var('state_income_band_width') }} end,
        case when loan_amount is null then null else floor(loan_amount / {{ var('state_loan_amount_band_width') }}) * {{ var('state_loan_amount_band_width') }} end
    from {{ ref('fct_application') }}
),
scored as (
    select *, count(*) over (
        partition by configuration, protected_geography, applicant_age, applicant_sex,
            derived_race, derived_ethnicity, protected_income, protected_loan_amount,
            loan_type, debt_to_income_ratio, loan_purpose, occupancy_type, lien_status,
            derived_dwelling_category, lei
    ) as k
    from configured
)
select configuration, derived_race, derived_ethnicity, action_taken, k, count(*) as record_count
from scored
group by configuration, derived_race, derived_ethnicity, action_taken, k
