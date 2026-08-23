select
    census_tract,
    applicant_age,
    applicant_sex,
    derived_race,
    derived_ethnicity,
    income,
    loan_amount,
    loan_purpose,
    occupancy_type,
    lien_status,
    derived_dwelling_category,
    lei,
    count(*) as k
from {{ ref('fct_application') }}
group by
    census_tract,
    applicant_age,
    applicant_sex,
    derived_race,
    derived_ethnicity,
    income,
    loan_amount,
    loan_purpose,
    occupancy_type,
    lien_status,
    derived_dwelling_category,
    lei

