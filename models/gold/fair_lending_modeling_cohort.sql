{{ config(materialized='table') }}

-- Internal-only row-grain model input. This relation must never be published.
with configured as (
    select 'cfpb_current' as configuration, *, census_tract as protected_geography,
        income as protected_income, loan_amount as protected_loan_amount
    from {{ ref('fct_application') }}
    union all
    select 'county_geo', *, substr(census_tract, 1, 5), income, loan_amount
    from {{ ref('fct_application') }}
    union all
    select 'county_banded', *, substr(census_tract, 1, 5),
        case when income is null then null else floor(income / 25000) * 25000 end,
        case when loan_amount is null then null else floor(loan_amount / 50000) * 50000 end
    from {{ ref('fct_application') }}
    union all
    select 'state_banded', *, substr(census_tract, 1, 2),
        case when income is null then null else floor(income / 50000) * 50000 end,
        case when loan_amount is null then null else floor(loan_amount / 100000) * 100000 end
    from {{ ref('fct_application') }}
),
scored as (
    select
        *,
        count(*) over (
            partition by configuration, protected_geography, applicant_age, applicant_sex,
                derived_race, derived_ethnicity, protected_income, protected_loan_amount,
                loan_purpose, occupancy_type, lien_status, derived_dwelling_category, lei
        ) as k
    from configured
)
select
    configuration,
    case when derived_race = 'Black or African American' then 1 else 0 end as is_black,
    cast(is_denied as integer) as is_denied,
    protected_income, protected_loan_amount, applicant_age, applicant_sex,
    loan_type, debt_to_income_ratio, loan_purpose, occupancy_type, lien_status,
    derived_dwelling_category
from scored
where k >= 5
  and derived_ethnicity = 'Not Hispanic or Latino'
  and derived_race in ('White', 'Black or African American')
  and action_taken in (1, 2, 3, 7)
