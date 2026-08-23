select
    census_tract,
    applicant_age,
    applicant_sex,
    derived_race,
    derived_ethnicity,
    count(*) as k
from {{ ref('fct_application') }}
group by
    census_tract,
    applicant_age,
    applicant_sex,
    derived_race,
    derived_ethnicity

