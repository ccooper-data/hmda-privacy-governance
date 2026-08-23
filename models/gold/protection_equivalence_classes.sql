with current_release as (
    select 'cfpb_current' as configuration, derived_race, derived_ethnicity, count(*) as k
    from {{ ref('fct_application') }}
    group by census_tract, applicant_age, applicant_sex, derived_race, derived_ethnicity,
             income, loan_amount, loan_type, debt_to_income_ratio, loan_purpose, occupancy_type, lien_status,
             derived_dwelling_category, lei
),
county_geo as (
    select 'county_geo' as configuration, derived_race, derived_ethnicity, count(*) as k
    from {{ ref('fct_application') }}
    group by substr(census_tract, 1, 5), applicant_age, applicant_sex, derived_race,
             derived_ethnicity, income, loan_amount, loan_type, debt_to_income_ratio, loan_purpose, occupancy_type,
             lien_status, derived_dwelling_category, lei
),
county_banded as (
    select 'county_banded' as configuration, derived_race, derived_ethnicity, count(*) as k
    from {{ ref('fct_application') }}
    group by substr(census_tract, 1, 5), applicant_age, applicant_sex, derived_race,
             derived_ethnicity, floor(income / {{ var('county_income_band_width') }}),
             floor(loan_amount / {{ var('county_loan_amount_band_width') }}), loan_type, debt_to_income_ratio,
             loan_purpose, occupancy_type, lien_status, derived_dwelling_category, lei
),
state_banded as (
    select 'state_banded' as configuration, derived_race, derived_ethnicity, count(*) as k
    from {{ ref('fct_application') }}
    group by substr(census_tract, 1, 2), applicant_age, applicant_sex, derived_race,
             derived_ethnicity, floor(income / {{ var('state_income_band_width') }}),
             floor(loan_amount / {{ var('state_loan_amount_band_width') }}), loan_type, debt_to_income_ratio,
             loan_purpose, occupancy_type, lien_status, derived_dwelling_category, lei
)
select configuration, derived_race, derived_ethnicity, k from current_release
union all
select configuration, derived_race, derived_ethnicity, k from county_geo
union all
select configuration, derived_race, derived_ethnicity, k from county_banded
union all
select configuration, derived_race, derived_ethnicity, k from state_banded
