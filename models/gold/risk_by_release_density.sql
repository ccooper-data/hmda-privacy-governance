select
    density.release_density_quintile,
    profile.derived_race,
    profile.derived_ethnicity,
    cast(sum(profile.k) as bigint) as record_count,
    sum(case when profile.k = 1 then profile.k else 0 end) * 1.0 / sum(profile.k)
        as sample_uniqueness_rate,
    count(*) * 1.0 / sum(profile.k) as prosecutor_expected_match_risk
from {{ ref('qi_profile_demographic_geo') }} as profile
inner join {{ ref('tract_release_density') }} as density
    on profile.census_tract = density.census_tract
group by
    density.release_density_quintile,
    profile.derived_race,
    profile.derived_ethnicity
having sum(profile.k) >= 20

