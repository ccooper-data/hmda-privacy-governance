select
    activity_year,
    lei,
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
    action_taken,
    (action_taken = 3 or action_taken = 7) as is_denied
from {{ ref('stg_lar') }}
where activity_year between 2018 and 2025
