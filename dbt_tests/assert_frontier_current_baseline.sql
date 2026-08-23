select 1
where (select count(*) from {{ ref('privacy_utility_frontier') }} where is_current_baseline) <> 1

