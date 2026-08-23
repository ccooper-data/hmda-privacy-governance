with scored as (
    select
        app.derived_race,
        app.derived_ethnicity,
        density.residential_density_quintile,
        profile.k
    from {{ ref('fct_application') }} as app
    inner join {{ ref('qi_profile_demographic_geo') }} as profile
      on app.census_tract is not distinct from profile.census_tract
     and app.applicant_age is not distinct from profile.applicant_age
     and app.applicant_sex is not distinct from profile.applicant_sex
     and app.derived_race is not distinct from profile.derived_race
     and app.derived_ethnicity is not distinct from profile.derived_ethnicity
    inner join {{ ref('tract_residential_density') }} as density
      on app.census_tract = density.census_tract
),
cohorts as (
    select residential_density_quintile, derived_race, derived_ethnicity, k from scored
    union all
    select residential_density_quintile, 'ALL', 'ALL', k from scored
)
select
    residential_density_quintile,
    derived_race,
    derived_ethnicity,
    count(*) as record_count,
    avg(case when k = 1 then 1.0 else 0.0 end) as sample_uniqueness_rate,
    avg(1.0 / k) as prosecutor_expected_match_risk
from cohorts
group by residential_density_quintile, derived_race, derived_ethnicity
having count(*) >= {{ var('minimum_cell_size') }}
