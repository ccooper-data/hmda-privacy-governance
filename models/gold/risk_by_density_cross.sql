with scored as (
    select
        residential.residential_density_quintile,
        release.release_density_quintile,
        profile.k
    from {{ ref('fct_application') }} as app
    inner join {{ ref('qi_profile_demographic_geo') }} as profile
      on app.census_tract is not distinct from profile.census_tract
     and app.applicant_age is not distinct from profile.applicant_age
     and app.applicant_sex is not distinct from profile.applicant_sex
     and app.derived_race is not distinct from profile.derived_race
     and app.derived_ethnicity is not distinct from profile.derived_ethnicity
    inner join {{ ref('tract_residential_density') }} as residential
      on app.census_tract = residential.census_tract
    inner join {{ ref('tract_release_density') }} as release
      on app.census_tract = release.census_tract
)
select residential_density_quintile, release_density_quintile,
    count(*) as record_count,
    avg(case when k = 1 then 1.0 else 0.0 end) as sample_uniqueness_rate,
    avg(1.0 / k) as prosecutor_expected_match_risk
from scored
group by residential_density_quintile, release_density_quintile
having count(*) >= {{ var('minimum_cell_size') }}
