with risk as (
    select configuration, cast(sum(k) as bigint) as record_count,
        sum(case when k = 1 then k else 0 end) * 1.0 / sum(k)
            as pre_suppression_uniqueness_rate,
        count(*) * 1.0 / sum(k) as pre_suppression_prosecutor_risk,
        sum(case when k >= 5 then k else 0 end) * 1.0 / sum(k) as retained_share
    from {{ ref('protection_equivalence_classes') }}
    group by configuration
),
release_states as (
    select configuration, configuration as field_configuration,
        false as is_unsuppressed_status_quo, record_count,
        pre_suppression_uniqueness_rate, pre_suppression_prosecutor_risk,
        retained_share, 0.0 as post_suppression_uniqueness_rate
    from risk
    union all
    select 'cfpb_current_unsuppressed', 'cfpb_current', true, record_count,
        pre_suppression_uniqueness_rate, pre_suppression_prosecutor_risk,
        1.0, pre_suppression_uniqueness_rate
    from risk where configuration = 'cfpb_current'
),
decision_utility as (
    select states.configuration,
        sum(case when cells.derived_race = 'White' then cells.record_count else 0 end)
            as reference_n,
        sum(case when cells.derived_race = 'Black or African American'
                 then cells.record_count else 0 end) as comparison_n,
        sum(case when cells.derived_race = 'White' and cells.action_taken in (3, 7)
                 then cells.record_count else 0 end) * 1.0
            / nullif(sum(case when cells.derived_race = 'White'
                              then cells.record_count else 0 end), 0)
            as reference_denial_rate
    from release_states as states
    inner join {{ ref('protection_utility_cells') }} as cells
      on cells.configuration = states.field_configuration
     and (states.is_unsuppressed_status_quo or cells.k >= 5)
     and cells.derived_ethnicity = 'Not Hispanic or Latino'
     and cells.derived_race in ('White', 'Black or African American')
     and cells.action_taken in (1, 2, 3, 7)
    group by states.configuration
)
select states.configuration,
    states.is_unsuppressed_status_quo as is_current_baseline,
    states.record_count,
    states.pre_suppression_uniqueness_rate,
    states.pre_suppression_prosecutor_risk,
    states.post_suppression_uniqueness_rate,
    1 - states.retained_share as suppression_cost_share,
    states.retained_share,
    utility.reference_n, utility.comparison_n,
    utility.reference_n >= {{ var('minimum_cell_size') }}
        and utility.comparison_n >= {{ var('minimum_cell_size') }} as utility_estimable,
    utility.reference_denial_rate,
    case when utility.reference_n >= {{ var('minimum_cell_size') }}
              and utility.comparison_n >= {{ var('minimum_cell_size') }}
         then 100 * 2.801585 * sqrt(
             utility.reference_denial_rate * (1 - utility.reference_denial_rate)
             * (1.0 / utility.reference_n + 1.0 / utility.comparison_n)
         ) end as minimum_detectable_disparity_points
from release_states as states
left join decision_utility as utility using (configuration)
