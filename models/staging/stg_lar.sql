select
    cast(activity_year as integer) as activity_year,
    cast(lei as varchar) as lei,
    cast(census_tract as varchar) as census_tract,
    cast(applicant_age as varchar) as applicant_age,
    cast(applicant_sex as varchar) as applicant_sex,
    cast(derived_race as varchar) as derived_race,
    cast(derived_ethnicity as varchar) as derived_ethnicity,
    try_cast(income as double) * 1000 as income,
    try_cast(loan_amount as double) as loan_amount,
    cast(loan_purpose as varchar) as loan_purpose,
    cast(occupancy_type as varchar) as occupancy_type,
    cast(lien_status as varchar) as lien_status,
    cast(derived_dwelling_category as varchar) as derived_dwelling_category,
    cast(action_taken as integer) as action_taken
from read_csv_auto('{{ var("hmda_lar_path") }}', header = true, all_varchar = true)

