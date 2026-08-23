select *
from {{ ref('risk_cohort_counts') }}
where record_count < {{ var('minimum_cell_size') }}
